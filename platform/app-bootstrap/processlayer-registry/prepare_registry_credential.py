#!/usr/bin/env python3
"""Verify a hidden, read-only PAT and seal an environment-scoped pull Secret offline.

No credential argument, environment input, plaintext file, Docker login or
cluster access. Only ciphertext is written; the package stays inactive until
its separately reviewed Flux activation and application imagePullSecrets change.
"""
import argparse
import base64
import getpass
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import warnings

OWNER = "TheDivine"
NAME = "processlayer-registry-pull"
NAMESPACE = "processlayer-prod"
SEALED_FILE = NAME + ".sealed.json"
SECRET_TYPE = "kubernetes.io/dockerconfigjson"
IMAGES = {
    "processlayer-api": "sha256:791b83a2137c5b5b8f8e864fb448b68c3cd46832a8b0b31edc01b3188fe84f88",
    "processlayer-web": "sha256:d7787cadd63fe42ceaa22af0c5893213c22c3a0654a1ff74907de122f5007cfb",
    "processlayer-postgres": "sha256:4fa3df2076f34cfc88700481d005d6b3faac181938acd2be2b436fcdfad1a497",
}
API_URL = "https://api.github.com/user"
ACCEPT = ", ".join(("application/vnd.oci.image.index.v1+json",
                    "application/vnd.oci.image.manifest.v1+json",
                    "application/vnd.docker.distribution.manifest.list.v2+json",
                    "application/vnd.docker.distribution.manifest.v2+json"))


class SafeFailure(Exception):
    """Only fixed messages, never provider response or credential details."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def token_url(image):
    return "https://ghcr.io/token?" + urllib.parse.urlencode({
        "service": "ghcr.io", "scope": "repository:thedivine/" + image + ":pull"})


def manifest_url(image):
    return "https://ghcr.io/v2/thedivine/" + image + "/manifests/" + IMAGES[image]


ALLOWED_REQUESTS = {("GET", API_URL)} | {
    request for image in IMAGES for request in
    (("GET", token_url(image)), ("HEAD", manifest_url(image)))}


def fetch(method, url, headers):
    if (method, url) not in ALLOWED_REQUESTS:
        raise SafeFailure("Unexpected verification endpoint or method.")
    # Default TLS verification remains enabled. No redirect may forward auth.
    opener = urllib.request.build_opener(NoRedirect())
    request = urllib.request.Request(url, headers=headers, method=method)
    try:
        with opener.open(request, timeout=30) as response:
            if response.status != 200 or response.geturl() != url:
                raise SafeFailure("Verification returned an unexpected HTTP response.")
            data = response.read(1024 * 1024 + 1)
            if len(data) > 1024 * 1024:
                raise SafeFailure("Verification response exceeded its size limit.")
            return data, {key.lower(): value for key, value in response.headers.items()}
    except (urllib.error.HTTPError, urllib.error.URLError, OSError):
        raise SafeFailure("GitHub/GHCR verification failed; check access and HTTPS connectivity. No output was retained.") from None


def read_token():
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            value = getpass.getpass("TheDivine classic PAT with only read:packages (hidden): ").strip()
    except (getpass.GetPassWarning, EOFError, OSError, io.UnsupportedOperation):
        raise SafeFailure("A hidden interactive terminal is required; echoed input is forbidden.") from None
    if not re.fullmatch(r"ghp_[A-Za-z0-9]{20,200}", value):
        raise SafeFailure("Enter a newly created classic GitHub PAT at the hidden prompt.")
    return value


def verify_access(token, request=fetch):
    body, headers = request("GET", API_URL, {
        "Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "processlayer-registry-bootstrap"})
    try:
        user = json.loads(body)
        scopes = {item.strip() for item in headers.get("x-oauth-scopes", "").split(",") if item.strip()}
        if user.get("login", "").lower() != OWNER.lower() or scopes != {"read:packages"}:
            raise SafeFailure("Token owner must be TheDivine and authorized scopes must be exactly read:packages.")
    except (ValueError, AttributeError, TypeError):
        raise SafeFailure("GitHub identity verification returned an unexpected response.") from None
    auth = base64.b64encode((OWNER + ":" + token).encode()).decode()
    for image, digest in IMAGES.items():
        body, _ = request("GET", token_url(image), {"Authorization": "Basic " + auth})
        try:
            session = json.loads(body)
            bearer = session.get("token") or session.get("access_token")
            if not isinstance(bearer, str) or not bearer or any(character.isspace() for character in bearer):
                raise ValueError()
        except (ValueError, AttributeError, TypeError):
            raise SafeFailure("GHCR did not return a usable package access token.") from None
        _, headers = request("HEAD", manifest_url(image), {
            "Authorization": "Bearer " + bearer, "Accept": ACCEPT})
        if headers.get("docker-content-digest") != digest:
            raise SafeFailure("A manifest response did not match its exact approved image digest.")
    return auth


def validate_sealed(value, namespace=NAMESPACE):
    if namespace not in (NAMESPACE, "processlayer"):
        raise SafeFailure("Unexpected target namespace.")
    if set(value) - {"apiVersion", "kind", "metadata", "spec"}:
        raise SafeFailure("Unexpected fields in sealed output.")
    if value.get("apiVersion") != "bitnami.com/v1alpha1" or value.get("kind") != "SealedSecret":
        raise SafeFailure("Expected a SealedSecret.")
    spec = value.get("spec", {})
    template = spec.get("template", {})
    if set(spec) != {"encryptedData", "template"} or set(template) != {"metadata", "type"}:
        raise SafeFailure("Unexpected or plaintext fields in sealed output.")
    for metadata in (value.get("metadata", {}), template.get("metadata", {})):
        if set(metadata) - {"name", "namespace", "creationTimestamp"}:
            raise SafeFailure("Sealed output annotations, ownership or extra metadata are forbidden.")
        if metadata.get("name") != NAME or metadata.get("namespace") != namespace or metadata.get("creationTimestamp") is not None:
            raise SafeFailure("Sealed output must have the exact target name and namespace.")
    if template.get("type") != SECRET_TYPE or set(spec["encryptedData"]) != {".dockerconfigjson"}:
        raise SafeFailure("Unexpected Secret type or encrypted fields.")
    try:
        raw = base64.b64decode(spec["encryptedData"][".dockerconfigjson"], validate=True)
        rsa_length = int.from_bytes(raw[:2], "big")
        if rsa_length not in (256, 384, 512, 1024) or len(raw) <= 2 + rsa_length + 16:
            raise ValueError()
    except (ValueError, TypeError):
        raise SafeFailure("Invalid encrypted envelope.") from None


def command(args, payload=None):
    try:
        result = subprocess.run(args, input=payload, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        raise SafeFailure("Required local certificate/sealing command could not complete.") from None
    if result.returncode:
        raise SafeFailure("Certificate validation or offline sealing failed; command output suppressed.")
    return result.stdout


def prepare(cert, output_dir, namespace=NAMESPACE):
    if namespace not in (NAMESPACE, "processlayer"):
        raise SafeFailure("Unexpected target namespace.")
    cert = Path(cert).resolve(strict=True)
    output = Path(output_dir).resolve(strict=True) / (SEALED_FILE if namespace == NAMESPACE else "staging-" + SEALED_FILE)
    if output.exists() or output.is_symlink():
        raise SafeFailure("Existing ciphertext will not be overwritten; preserve the current credential.")
    certificate = cert.read_bytes()
    if b"-----BEGIN CERTIFICATE-----" not in certificate or b"PRIVATE KEY" in certificate:
        raise SafeFailure("Supply only the trusted controller public PEM certificate.")
    command(["openssl", "x509", "-in", str(cert), "-noout", "-checkend", "0"])
    # Reserve the ciphertext destination exclusively before collecting input.
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(descriptor)
    try:
        token = read_token()
        auth = verify_access(token)
        config = json.dumps({"auths": {"ghcr.io": {"auth": auth}}})
        encoded = base64.b64encode(config.encode()).decode()
        secret = {"apiVersion": "v1", "kind": "Secret", "type": SECRET_TYPE,
                  "metadata": {"name": NAME, "namespace": namespace},
                  "data": {".dockerconfigjson": encoded}}
        sealed = json.loads(command(["kubeseal", "--cert", str(cert), "--scope", "strict", "--format", "json"], json.dumps(secret).encode()))
        validate_sealed(sealed, namespace)
        serialized = json.dumps(sealed, indent=2) + "\n"
        if any(sensitive in serialized for sensitive in (token, auth, config, encoded)):
            raise SafeFailure("Plaintext credential material was detected in output.")
        output.write_text(serialized, encoding="utf-8")
        return output
    except BaseException:
        output.unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cert", required=True, help="Trusted controller public PEM certificate")
    parser.add_argument("--output-dir", default=str(Path(__file__).resolve().parent))
    parser.add_argument("--namespace", choices=(NAMESPACE, "processlayer"), default=NAMESPACE)
    args = parser.parse_args()
    try:
        output = prepare(args.cert, args.output_dir, args.namespace)
    except SafeFailure as error:
        print("Stopped: " + str(error), file=sys.stderr)
        return 1
    except (Exception, KeyboardInterrupt) as error:
        print("Stopped: " + type(error).__name__ + "; diagnostics suppressed, no credential published.", file=sys.stderr)
        return 1
    print("Verified TheDivine, exactly read:packages, and all three pinned manifests.")
    print("Prepared encrypted file only: " + str(output))
    print("No registry, Git, Flux, Argo or Kubernetes changes were made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
