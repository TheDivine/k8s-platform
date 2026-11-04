# ProcessLayer repository access through Flux and Argo CD

Prepared 4 November 2026. The existing ProcessLayer Applications cannot compare
Git because their HTTPS repository credential is invalid. This repair belongs
to the platform repository. It does not deploy with a direct Kubernetes patch.

## Exact ownership and scope

- Flux installs a **new** strict-scope SealedSecret named
  `processlayer-gitops-repository` in `argocd`. The generated Secret has Argo's
  repository label, `type=git`, `project=default`, the exact SSH repository URL,
  and a newly generated repository-only deploy key.
- The public half is registered **read-only** on
  `TheDivine/processlayer-ai`. It is not a personal SSH key or account token.
- This first activation declares only the existing staging Application
  `processlayer`, with its existing project, path, namespace, main revision and
  automated sync settings. Argo still owns application workloads.
- `production.yaml` is an **unreferenced preparation file** for the existing
  `processlayer-prod` Application. Restore production's SSH access only in a
  follow-up platform commit after staging acceptance and the safe production
  hook release are merged in the application repository. Restoring access now
  would let automatic sync resume the legacy seed-capable production Job.
- The staging URL becomes `git@github.com:TheDivine/processlayer-ai.git`. The old HTTPS
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

Restoring repository access resumes staging's already-enabled automatic sync
to main. Production stays on its current HTTPS reference during this first
activation. After staging acceptance and the safe production release merge,
add `production.yaml` to the Application package in a reviewed follow-up and
update the activation guard test to expect both names. Review the complete main
desired state before either merge. Repository access success does not prove a
healthy app, database migration, backup or DF enquiry flow.

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
