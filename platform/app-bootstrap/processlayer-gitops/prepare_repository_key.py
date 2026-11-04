#!/usr/bin/env python3
"""Generate a new repository-only deploy key and seal its private half offline.

Linux/WSL only: private temporary files use verified POSIX 0700/0600 modes.
Inputs: a trusted controller PUBLIC certificate. Outputs: sealed JSON + public
SSH key only. No kubectl, secret reads, network calls or GitHub registration.
"""
import argparse
import base64
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile


NAME = "processlayer-gitops-repository"
NAMESPACE = "argocd"
REPOSITORY = "git@github.com:TheDivine/processlayer-ai.git"
LABELS = {"argocd.argoproj.io/secret-type": "repository"}
SEALED_FILE = NAME + ".sealed.json"
PUBLIC_FILE = NAME + ".pub"
KEYS = {"type", "url", "project", "sshPrivateKey"}


def command(args, data=None):
    result = subprocess.run(args, input=data, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=60)
    if result.returncode:
        raise RuntimeError("Local credential preparation command failed; output suppressed")
    return result.stdout


def metadata():
    return {"name": NAME, "namespace": NAMESPACE, "labels": LABELS.copy()}


def validate_sealed(value):
    if value.get("apiVersion") != "bitnami.com/v1alpha1" or value.get("kind") != "SealedSecret":
        raise ValueError("Expected a SealedSecret")
    spec = value.get("spec", {})
    template = spec.get("template", {})
    for item in (value, spec, template):
        if "data" in item or "stringData" in item:
            raise ValueError("Plaintext Secret fields are forbidden")
    for item in (value.get("metadata", {}), template.get("metadata", {})):
        if item.get("name") != NAME or item.get("namespace") != NAMESPACE:
            raise ValueError("Strict name/namespace mismatch")
        annotations = item.get("annotations", {})
        if any(key.startswith("sealedsecrets.bitnami.com/") for key in annotations):
            raise ValueError("Scope/ownership annotations are not accepted")
    if template.get("metadata", {}).get("labels", {}).get("argocd.argoproj.io/secret-type") != "repository":
        raise ValueError("Argo repository label missing from Secret template")
    if template.get("type") != "Opaque":
        raise ValueError("Unexpected Secret type")
    encrypted = spec.get("encryptedData", {})
    if set(encrypted) != KEYS:
        raise ValueError("Unexpected encrypted credential fields")
    for value in encrypted.values():
        if not isinstance(value, str):
            raise ValueError("Encrypted value must be a string")
        raw = base64.b64decode(value, validate=True)
        rsa_length = int.from_bytes(raw[:2], "big")
        # HybridEncrypt stores a 2-byte RSA length, RSA envelope, and AES-GCM
        # ciphertext/tag. The nonce is not serialized; the tag is 16 bytes.
        # Short nonempty values such as type=git must remain valid.
        if rsa_length not in (256, 384, 512, 1024) or len(raw) <= 2 + rsa_length + 16:
            raise ValueError("Invalid encrypted envelope")


def prepare(cert, output_dir):
    if os.name != "posix":
        raise RuntimeError("Run under Linux/WSL for verified private-file permissions")
    cert = Path(cert).resolve(strict=True)
    output = Path(output_dir).resolve(strict=True)
    if not output.is_dir():
        raise ValueError("Output directory does not exist")
    destinations = [output / SEALED_FILE, output / PUBLIC_FILE]
    if any(path.exists() or path.is_symlink() for path in destinations):
        raise FileExistsError("Existing output will not be overwritten; do not rotate accidentally")
    certificate = cert.read_bytes()
    if b"-----BEGIN CERTIFICATE-----" not in certificate or b"PRIVATE KEY" in certificate:
        raise ValueError("Supply only a controller public certificate")
    command(["openssl", "x509", "-in", str(cert), "-noout", "-checkend", "0"])
    old_mask = os.umask(0o077)
    created = []
    try:
        # Reserve both output names exclusively before generating any key.
        for path in destinations:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            os.close(descriptor)
            created.append(path)
        # Keep the private file on native Linux /tmp, not an inherited Windows
        # TMPDIR whose POSIX mode bits may not describe the underlying ACL.
        with tempfile.TemporaryDirectory(prefix="processlayer-deploy-key-", dir="/tmp") as temporary:
            folder = Path(temporary)
            folder.chmod(0o700)
            if stat.S_IMODE(folder.stat().st_mode) != 0o700:
                raise RuntimeError("Private temporary directory permissions are unsafe")
            private_path = folder / "repository-key"
            command(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", NAME, "-f", str(private_path)])
            private_path.chmod(0o600)
            if stat.S_IMODE(private_path.stat().st_mode) != 0o600:
                raise RuntimeError("Private key permissions are unsafe")
            private = private_path.read_bytes()
            public = private_path.with_suffix(".pub").read_text().strip()
            if not private.startswith(b"-----BEGIN OPENSSH PRIVATE KEY-----") or not public.startswith("ssh-ed25519 ") or "\n" in public:
                raise ValueError("Unexpected generated SSH key format")
            # Decode the public blob for structural validation, never a private key.
            base64.b64decode(public.split()[1], validate=True)
            secret = {"apiVersion": "v1", "kind": "Secret", "metadata": metadata(), "type": "Opaque",
                      "data": {key: base64.b64encode(value).decode() for key, value in {
                          "type": b"git", "url": REPOSITORY.encode(), "project": b"default", "sshPrivateKey": private}.items()}}
            sealed = json.loads(command(["kubeseal", "--cert", str(cert), "--scope", "strict", "--format", "json"], json.dumps(secret).encode()))
            validate_sealed(sealed)
            serialized = (json.dumps(sealed, indent=2) + "\n").encode()
            if private in serialized or base64.b64encode(private) in serialized or b"PRIVATE KEY" in serialized:
                raise ValueError("Plaintext private material found in output")
            destinations[0].write_bytes(serialized)
            destinations[1].write_text(public + "\n")
        # The temporary private file has been removed before this function returns.
        return destinations
    except BaseException:
        for path in created:
            path.unlink(missing_ok=True)
        raise
    finally:
        os.umask(old_mask)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cert", required=True, help="Trusted controller public PEM certificate")
    parser.add_argument("--output-dir", default=str(Path(__file__).resolve().parent))
    args = parser.parse_args()
    try:
        destinations = prepare(args.cert, args.output_dir)
    except Exception as error:
        print("Stopped: " + type(error).__name__ + ". No credential published or cluster changed; diagnostics suppressed.")
        return 1
    print("Prepared encrypted repository credential and public deploy key only:")
    for path in destinations:
        print(path)
    print("Register the public key on TheDivine/processlayer-ai with read_only=true before GitOps activation.")
    print("No GitHub, Argo, Flux or Kubernetes changes were made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
