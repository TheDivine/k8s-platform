# ProcessLayer repository access through Flux and Argo CD

Updated 4 November 2026. Invalid HTTPS repository credentials prevented Argo from
comparing ProcessLayer Git state. Platform
[PR #21](https://github.com/TheDivine/k8s-platform/pull/21) merged as
`c21ff3f31e37f8536b0feb369aee75504552a728`, declaring the new repository credential
and **staging-only** SSH access. This follow-up is local preparation to extend
the same access to the existing production Application, subject to the gate
below. No direct Kubernetes patch is used.

## Exact ownership and scope

- Flux installs a **new** strict-scope SealedSecret named
  `processlayer-gitops-repository` in `argocd`. The generated Secret has Argo's
  repository label, `type=git`, `project=default`, the exact SSH repository URL,
  and a newly generated repository-only deploy key.
- The public half is registered **read-only** on
  `TheDivine/processlayer-ai`. It is not a personal SSH key or account token.
- PR #21 declares the existing staging Application `processlayer`, preserving
  its project, path, namespace, main revision and automated sync settings.
- This follow-up adds the already-prepared `production.yaml` for the existing
  `processlayer-prod` Application to the package. It preserves the corresponding
  production settings. Do not publish/merge it until staging acceptance and the
  safe production-hook release are proven. Early access restoration could let
  automatic sync resume the legacy seed-capable production Job.
- The repository URL is `git@github.com:TheDivine/processlayer-ai.git`. The old HTTPS
  credential entry is left unused; no existing Secret is adopted or overwritten.
- No new ApplicationSet entry is added for either name. Confirm the live
  Applications have no competing declarative owner or source/image overrides
  before taking their declarations under Flux.

The child Flux Kustomizations are `processlayer-gitops-credentials` and
`processlayer-applications`. Both use the existing `flux-system` GitRepository,
`prune: false` and `wait: true`. Application registration depends on the
credential Kustomization. Its explicit SealedSecret health expression requires
`Synced=True`, rather than assuming that submitting ciphertext created a usable
Secret. Confirm the installed Flux CRD supports `healthCheckExprs`; unsupported
fields must be resolved at platform ownership, not silently dropped.

## Prepare the encrypted credential once

Obtain only the current SealedSecrets controller **public certificate**, through
the user's trusted authenticated route. Do not request its private sealing key,
read an unrelated Secret, retrieve a personal token, or use an unverified cached
certificate. The public certificate does not grant cluster access.

Run under Linux/WSL with `ssh-keygen`, `openssl`, `kubeseal` and Python 3:

```bash
python3 platform/app-bootstrap/processlayer-gitops/prepare_repository_key.py \
  --cert /trusted/path/controller-public.pem
```

The helper checks certificate validity, refuses to overwrite either output,
generates a new Ed25519 key in a private temporary directory, pipes an in-memory
Secret to `kubeseal --scope strict`, validates the encrypted output/template,
and deletes the temporary private file. It invokes no network, GitHub, kubectl,
Flux or Argo command. It outputs **only**:

- `processlayer-gitops-repository.sealed.json` — publishable encrypted manifest.
- `processlayer-gitops-repository.pub` — publishable SSH public key.

POSIX 0700/0600 permissions are checked; run the helper in WSL rather than
claiming Windows chmod provides an equivalent ACL. No private key is retained
for convenience. File deletion is not a claim of forensic erasure. Back up the
controller's sealing keys through the existing private recovery procedure.

Do not rerun the helper just to recover a path or retry a publication step.
Existing outputs stop accidental rotation. If preparation fails, private temp
files and newly reserved output files are removed; previous outputs are kept.

## Register only the public deploy key

After reviewing the generated public key, register it under this repository's
Settings → Deploy keys with **Allow write access unchecked**, or use the exact
GitHub API operation with `read_only: true`:

```text
POST /repos/TheDivine/processlayer-ai/keys
title: processlayer-gitops-repository
key: contents of processlayer-gitops-repository.pub
read_only: true
```

Record the provider key ID/fingerprint and read back `read_only=true`. Do not
publish the private key, create an account-wide credential or grant write access.
The helper deliberately does not perform this separate provider registration.

## Activate only the complete reviewed package

The candidate references both child Kustomizations from
`clusters/production/kustomization.yaml`. Authenticated live inspection confirmed
both existing Applications have no competing owner, image overrides or different
source/sync settings. The tracked Flux v2.7.5 CRD supports `healthCheckExprs`
(kustomize-controller v1.7.3). These are preparation checks, not evidence that the
candidate has reconciled. Before publishing/merging this activation:

1. Confirm existing Application names, paths, namespaces, project, revision,
   automatic sync settings and absence of conflicting owners/overrides.
2. Generate the real sealed manifest with the trusted public certificate;
   register/read back the public deploy key. Never commit a fake ciphertext.
3. Render the credential and Application packages, run the helper tests and
   verify the root rendering contains only the intended additional resources.
4. Review the production-root references to
   `processlayer-gitops-credentials.yaml` and `processlayer-applications.yaml`,
   then merge the complete platform change only after the encrypted artifact
   exists and the matching public deploy key has been registered.
5. Observe Flux credential readiness, then application registration. Check Argo
   reads the SSH URL, comparison succeeds and its revision advances. Preserve
   normal SSH host-key verification; never enable insecure SSH/TLS flags.

Restoring repository access resumes each Application's already-enabled automatic
sync to main. PR #21 deliberately leaves production's current HTTPS reference
alone. This locally prepared follow-up includes `production.yaml` and updates
the activation guard test to expect both names. Review the complete application
main desired state before publishing/merging it. Repository access success does
not prove a healthy app, database migration, backup or DF enquiry flow.

## Production follow-up gate — verified prerequisites

The following prerequisite checks are verified. They authorize the reviewed
platform follow-up; they do not claim production reconciliation or a completed
production enquiry. No key generation, rotation or additional GitHub access is
required.

| Gate | Evidence |
| --- | --- |
| Platform staging repair merged | PR #21, `c21ff3f31e37f8536b0feb369aee75504552a728` |
| Exact repository deploy key approved and registered read-only | GitHub key `168781237`; verified fingerprint recorded below |
| Credential works; Flux-managed staging Argo SSH comparison succeeds at intended revision | Verified: Flux controller Apply ownership on the existing Application; Argo `Synced`/`Healthy` at `f2c99cda513fdbea4964685a1c38bd034ec7bb66`, completed `2026-11-04T17:00:00Z` |
| Staging DF enquiry saved under the intended founder, with one lead after retry | Verified by two identical POSTs, authenticated API read-back and exactly one matching dashboard row; acceptance record below |
| Safe production release merged in application main | [ProcessLayer PR #10](https://github.com/TheDivine/processlayer-ai/pull/10), merge `519a3c45218efa734a5eec03f9cbfb6ffbc5854d`; final-head `b8d81069` checks passed in [CI run 41875386121](https://github.com/TheDivine/processlayer-ai/actions/runs/41875386121) |
| Complete production desired state reviewed before restoring automatic sync | Read-only GitHub verification confirmed exact main `519a3c45218efa734a5eec03f9cbfb6ffbc5854d`, retained PVC/backup restore hook at Sync wave -2, fail-closed no-seed schema hook at -1, independently pinned schema image, signed v0.2.3 API/web digests and DF owner wiring; CI includes full rendered preservation/rollback checks |

Staging acceptance used labelled synthetic request
`5edaa949-4b8f-4910-a3ac-b5e1e07960da`. Two identical submissions both returned HTTP
201 and the same record ID:
`df-5edaa949-4b8f-4910-a3ac-b5e1e07960da-9bb505fcb5553c9eb3f4c92e96c53aaf`.
Authenticated dashboard filtering found exactly one matching company row. API
read-back confirmed owner `5fdcceda-3057-4a03-9f67-fa4db049360c`, matching the
existing `admin@processlayerai.com` founder, status `NEW`, source
`dfmarketsolutions.com`, service `other`, and the submitted synthetic message
and email. No real prospect data or outreach was used. This establishes staging
persistence, ownership and retry deduplication; it is not production evidence.

The production application release is merged, but its repository-access
activation and runtime checks remain separate. Successful final-head CI and
the merge are not evidence that production has executed the new hooks yet.

With those prerequisites verified, publish/review the platform follow-up that changes only the
Application package inclusion, its guard test and this record. Observe production
comparison and reconciliation; then verify the backup/restore/schema hooks and
actual DF lead flow. Preserve residual unrelated degradation in the report.

The unrelated production application SealedSecret ownership failure and old
backup Job remain separately reported. This change must not adopt/regenerate
that working application Secret, remove storage, or delete Jobs to force health.

## Validation and rollback

The initial key was registered after explicit owner approval on 4 November 2026:
GitHub deploy-key ID `168781237`, fingerprint
`SHA256:mMd1ywzgFOSW9f2+lcNeperEEc6IUIvbCNoj3b6zM7U`.
Provider read-back confirmed the exact SSH key material and `read_only=true`.
Only the public key and strict-scope ciphertext are stored in this repository.

```bash
python3 -B -m unittest discover \
  -s platform/app-bootstrap/processlayer-gitops -p 'test_*.py'
kubectl kustomize platform/app-bootstrap/processlayer-gitops
kubectl kustomize platform/app-bootstrap/processlayer-applications
kubectl kustomize clusters/production
```

All rendering is local. The credential package intentionally cannot render
before a real sealed file exists. Tests may create structural ciphertext
fixtures in temporary directories outside Git; fixtures are never activated.

The Flux child resources use `prune: false`, so reverting registration does not
delete Applications, their workloads or the new credential. A Git revert alone
does not revoke a GitHub deploy key. For rollback, preserve the Applications and
working data, restore a reviewed known-good repository reference/credential,
then revoke only the recorded new deploy-key ID when no consumer depends on it.
The broken old HTTPS entry is not a known-good rollback target.

## References

- [Argo repository Secret configuration](https://argo-cd.readthedocs.io/en/stable/operator-manual/declarative-setup/#repositories)
- [Flux dependencies and health checks](https://fluxcd.io/flux/components/kustomize/kustomizations/#health-check-expressions)
- [SealedSecrets strict scope and Secret templates](https://github.com/bitnami/sealed-secrets#scopes)
