# Repository Operating Model

This repository is a public-safe Kubernetes, GitOps, and DevSecOps reference. It should show professional patterns without exposing real environment state.

## What Belongs In This Repo

- Sanitized Kubernetes manifests and examples.
- GitOps structure for Argo CD and Flux.
- Public app scaffolds and deployment examples.
- Placeholder-only secret templates.
- Architecture diagrams and runbooks.
- Platform operating docs.
- Public-safe security baseline examples.
- Validation helpers that do not mutate live infrastructure.

## What Does Not Belong In This Repo

- Real secrets, passwords, OAuth secrets, API tokens, private keys, kubeconfigs, registry auth, or `.env` files.
- Terraform state, real `tfvars`, provider credentials, or production backend configuration.
- Ansible vault files, real inventories, host-specific secrets, SSH private material, or Wazuh enrollment secrets.
- Generated cluster exports, endpoint dumps, event dumps, or raw `kubectl get all -o yaml` snapshots.
- Backup payloads, database dumps, logs, uploads, or runtime data.
- Nested private application repositories unless intentionally sanitized and documented.

## Public-Safe Examples

Public-safe examples must use obvious placeholder values such as `CHANGE_ME`, `example.com`, and `example.local`. They should explain how real values are created outside public Git.

Acceptable patterns:

- `*.example.yaml`
- `*.template.yaml`
- SOPS examples without private keys
- SealedSecrets examples only when the controller key lifecycle is understood
- ExternalSecrets references without provider credentials

## Private Environment Overlays

Private overlays contain environment-specific domains, IPs, storage classes, secrets references, node selectors, and production routing choices. These should live in a private repo or private branch unless fully sanitized.

TODO: Decide whether private overlays are maintained as a separate repo or generated from secure CI/CD inputs.

## Generated Exports

`platform/exports/` and `platform/exports-clean/` are generated cluster exports. They must remain ignored and untracked because they may expose topology, endpoint data, labels, annotations, service names, or operational state.

## Secrets Handling

Real secrets must be created through one of:

- SOPS with private key material outside public Git.
- SealedSecrets with a documented controller key lifecycle.
- ExternalSecrets with provider credentials outside public Git.
- Manual `kubectl create secret` commands run by an operator outside Git.

Historical committed secrets should be treated as exposed and rotated through a private operational process.

## App Repositories

Application source code can stay in separate private repositories. This platform repo should reference deployable application outputs such as container images, Helm charts, or sanitized Kustomize overlays.

Nested local app repositories under `apps/` should stay ignored unless converted into public examples.

## Terraform Repo Boundary

Real provisioning belongs in a private Terraform repository. This public repo may later contain non-sensitive examples, diagrams, and module interface documentation, but not provider credentials, state, or real environment variables.

## Ansible And Security Repo Boundary

Real host hardening, inventories, Wazuh enrollment, and environment-specific security automation should live in a private infra-security repository. This public repo may contain example roles, SOPs, and documentation showing the intended operating model.
