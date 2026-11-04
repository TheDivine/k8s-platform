# ProcessLayer production registry access

The production backup Job is admitted after the container security-context fix,
but its private GHCR image pull is denied with HTTP 403. The existing `ghcr-pull`
credential remains untouched. Git repository SSH access and registry image
access are separate credentials; the SSH deploy key cannot pull OCI images.

## Prepared change and boundaries

This package prepares one new strict SealedSecret,
`processlayer-prod/processlayer-registry-pull`, containing only a GHCR Docker
authentication entry. Flux owns it through the new
`processlayer-registry-credentials` child Kustomization. The child is included in the production root with real operator-prepared ciphertext. No placeholder Secret is used. The child uses `prune: false`, `wait: true` and the
controller's `Synced=True` health gate. Staging and existing Secrets are unchanged.

The helper accepts a new classic PAT belonging to `TheDivine` with **exactly
`read:packages`**. Broader scopes, an OAuth CLI token, a fine-grained PAT, a missing
scope header and another owner are rejected. This is a personal package-read
credential: classic PATs cannot restrict access to only these three packages.
Its scope permits reading packages already accessible to the account. Use an
expiry and record the rotation date privately. Do not grant `repo`,
`write:packages`, `delete:packages` or administrative scopes.

GitHub documents [classic PAT authentication and package-read scope](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
and the [X-OAuth-Scopes response header](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps).
The helper checks the authenticated `/user` identity and exact granted scopes,
then obtains pull-only GHCR tokens and HEAD-checks the approved manifests:

| Package | Approved digest |
| --- | --- |
| `thedivine/processlayer-api` | `sha256:cb9f02594cd2d8f4f746cc1797e8911a6093eaf7781f30eb2aa6d1848e6109ab` |
| `thedivine/processlayer-web` | `sha256:d7787cadd63fe42ceaa22af0c5893213c22c3a0654a1ff74907de122f5007cfb` |
| `thedivine/processlayer-postgres` | `sha256:4fa3df2076f34cfc88700481d005d6b3faac181938acd2be2b436fcdfad1a497` |

Every image must return HTTP 200 with the exact `Docker-Content-Digest`. Requests
use verified HTTPS and fixed GitHub/GHCR endpoints; redirects are refused.
Response bodies, authorization headers and subprocess diagnostics are never
printed. This verifies manifest access, not a kubelet pull or healthy rollout.

## One local operator step

Create the new expiring classic PAT in the `TheDivine` account with only
`read:packages`. Do not paste it into chat, a command, an environment variable or
a file. Open an interactive WSL terminal. Replace only the public paths below,
using the existing trusted controller public certificate and verified local
`kubeseal` binary; no kubeconfig is needed:

```bash
PATH="/absolute/path/to/workspace/.tools:$PATH" python3 -B /absolute/path/to/platform-df-release/platform/app-bootstrap/processlayer-registry/prepare_registry_credential.py --cert /absolute/path/to/trusted-controller-public.pem
```

Enter the PAT only at the hidden terminal prompt. The helper refuses an echoed
stdin fallback. Plaintext exists only in process memory and the `kubeseal` stdin
pipe; it is not written to disk, passed in process arguments, stored in the
environment, logged, or put in Docker configuration. The offline seal uses
`--cert --scope strict`, bound to the exact production name and namespace.

The only retained output is
`platform/app-bootstrap/processlayer-registry/processlayer-registry-pull.sealed.json`.
Its metadata, Secret type, encrypted envelope and absence of plaintext are checked
before writing. Existing output, including a dangling symlink, is refused;
failure removes only the newly reserved output. Do not delete a valid existing
credential merely to retry. Share only the completion result and ciphertext
path. The helper does not publish Git changes or contact Kubernetes.

## GitOps activation after successful preparation

1. Review the encrypted file and the helper's seven successful read requests
   (identity plus token/manifest for each image). The operator confirmed successful helper completion on 4 November 2026; the resulting strict ciphertext was validated before activation.
2. Include `processlayer-registry-credentials.yaml` in the production root
   Kustomization, adjust the activation regression into a real-ciphertext
   activation guard, and publish through the platform PR workflow. Do not merge
   activation without ciphertext and all-image verification.
3. Observe Flux reconciliation and SealedSecret `Synced=True` for the new name.
   This provisions a new Secret; it does not adopt or overwrite `ghcr-pull`.
4. Separately change only the relevant ProcessLayer **production**
   `imagePullSecrets` references in the application repo to the new name:
   API, web, schema Job and pre-migration backup Job. Render and test those
   references; preserve the running PostgreSQL StatefulSet and its storage.
   Publish that app PR only after the prerequisite Secret is confirmed ready.
5. Observe Argo's backup/restore checkpoint, safe schema hook and app rollout.
   Verify a synthetic inquiry persists once under the intended dashboard owner
   before enabling the public form. A merged PR or authenticated manifest HEAD
   alone is not deployment proof.

Rollback remains through Git. Do not revoke or delete the old credential during
this repair; do not delete Jobs, PVCs, Secrets or relax admission policy to force
progress. Before expiry, prepare a reviewed credential rotation while current
pulls still work. Revocation and rotation require a separate explicit operation.

## Offline regression checks

Run `make processlayer-registry-check` (Python 3, PyYAML and `kubectl` for local
Kustomize rendering). Tests use mock credentials and temporary ciphertext
fixtures outside Git. They cover identity/scope enforcement, all three exact
digests, redirect refusal, hidden input, strict scope, plaintext rejection,
overwrite/symlink safety, failure cleanup and gated Flux wiring.

## Activation checkpoint — 4 November 2026

The operator supplied the helper-generated encrypted credential. The application bootstrap now depends on registry readiness as well as Git repository readiness. Its production Application receives `processlayer.ai/registry-prerequisite: processlayer-registry-pull-2026-11-04` only after Flux sees the registry child Ready. This annotation is an observable prerequisite checkpoint in Argo; it is not proof of image pull or app rollout. Application pull references remain unchanged until that checkpoint is observed. Existing Secrets and staging workload configuration remain unchanged.
