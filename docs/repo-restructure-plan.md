# Repository Restructure Plan

This plan is intentionally conservative. It keeps working nested application directories available locally while building a professional public GitOps/IaC/DevSecOps baseline around them.

## Guiding Rules

- Do not delete live or unknown files during restructuring.
- Do not move live Kubernetes manifests without a reviewable migration commit.
- Do not commit secrets, kubeconfigs, tokens, private keys, certificates, or `.env` files.
- Keep working app repositories nested if that supports local development, but expose only sanitized GitOps interfaces in the platform repo.
- Prefer docs, README files, examples, and suspended GitOps wiring before active reconciliation.

## Phase 1: Documentation Only

Actions:

- Maintain `docs/repo-audit.md`, `docs/repo-restructure-plan.md`, `docs/proposed-tree.md`, `docs/gitops-ownership.md`, `docs/devsecops-baseline.md`, `docs/security-scan-paths.md`, and `docs/architecture.md`.
- Capture current structure, risks, ownership, and target layout.
- Add TODO markers for manual decisions.

Rollback:

- Revert the documentation commit only.

TODO:

- Decide whether the public baseline should present Flux, Argo CD, or both as first-class examples.
- Decide whether app workspaces remain nested long-term or become separate repos referenced by docs/submodules.

## Phase 2: Create Clean Folders

Actions:

- Add README-only folders for:
  - `tools/`
  - `security/`
  - `ansible/`
  - `terraform/`
  - `scripts/`
  - optional `policies/`
- Explain what belongs in each folder before moving any content.

Rollback:

- Revert the README-only folder commit.

TODO:

- Pick naming: `security/kyverno` versus `policies/kyverno`.
- Pick `scripts/bootstrap` versus `tools/bootstrap` for one-shot admin wrappers.

## Phase 3: Move Non-Live Docs And Examples

Actions:

- Convert unclear notes such as `.txt` files into Markdown where safe.
- Move only non-live, non-secret documentation in small commits.
- Keep generated exports out of Git.
- Keep local nested apps ignored unless sanitized.

Rollback:

- Revert individual doc/example move commits.

TODO:

- Review `platform/drone-ci/drone.txt`.
- Review `infra/storage/local-storage-provisioner.txt`.
- Review `infra/networking/*iperf*` as benchmark tooling or examples.

## Phase 4: Migrate Platform Manifests

Actions:

- Add README files under each platform component documenting ownership, deployment method, inputs, secrets, and rollback.
- Consolidate duplicate dashboard manifests before enabling GitOps.
- Keep secrets as `*.example.yaml`, `*.template.yaml`, SOPS, SealedSecrets, or ExternalSecrets only.
- Prefer overlays by environment for production-style services.

Rollback:

- Disable/suspend GitOps reconciliation first.
- Revert the manifest migration commit.
- Restore prior controller ownership from Git if needed.

TODO:

- Decide ownership for `platform/argocd`, `platform/flux`, `platform/traefik`, `platform/metallb`, `platform/monitoring`, `platform/backup`, and `platform/drone-ci`.
- Decide whether `platform/k8s-admin` should remain a lab-only example.

## Phase 5: Migrate Apps

Actions:

- Keep working nested app directories available for development.
- Add clean GitOps-facing app directories only when sanitized.
- Use the `apps/kasm` scaffold as the app pattern: docs, namespace, kustomize base, overlays, example secrets, and suspended GitOps wiring.
- For `apps/kwiki`, introduce a clean public deployment surface separately from local runtime data and nested repo content.

Rollback:

- Suspend app GitOps reconciliation.
- Revert the app scaffold or overlay commit.
- Keep local nested app workspaces untouched.

TODO:

- Decide if `apps/kwiki` becomes a public app example, private app, or external repo.
- Decide whether Kasm will use official Helm, upstream manifests, or a custom chart after upstream validation.

## Phase 6: Introduce Argo CD App-Of-Apps Or Flux Structure

Actions:

- Define one primary ownership tree per controller.
- For Argo CD: use app-of-apps for curated platform/app bundles.
- For Flux: use `GitRepository` and `Kustomization` objects with explicit paths and `suspend: true` for incomplete apps.
- Avoid managing the same path/resource from both controllers.

Rollback:

- Set Argo CD apps to manual/suspended equivalent or remove the app from the app-of-apps entry.
- Set Flux `spec.suspend: true`.
- Revert the controller wiring commit.

TODO:

- Decide whether Flux manages `apps/` while Argo CD manages `platform/`, or vice versa.
- Decide if one controller should be the public default and the other a documented alternative.

## Phase 7: Introduce Ansible Node Baseline

Actions:

- Add Ansible inventory examples with placeholder hosts only.
- Add roles for Linux hardening, SSH, firewall, auditd, fail2ban, ClamAV, and optional Maldet.
- Use check mode in docs before applying to real nodes.
- Keep vault files, real inventories, and SSH private material out of Git.

Rollback:

- Revert Ansible role commits.
- Restore host state from OS backups or package manager history if any role is ever applied manually.

TODO:

- Choose supported OS family and version.
- Decide whether Kubernetes node bootstrap belongs in Ansible or kubeadm docs.

## Phase 8: Introduce Terraform Infrastructure Baseline

Actions:

- Add provider-free module skeletons or examples first.
- Add DNS, object storage, registry, firewall, and IAM examples with placeholder values.
- Never commit `.tfstate`, `.terraform/`, real `*.tfvars`, or provider credentials.
- Document remote state setup before real resources exist.

Rollback:

- Revert Terraform example commits.
- For real infrastructure later, use `terraform plan` and targeted rollback plans before `apply`.

TODO:

- Decide provider targets: cloud DNS, object storage, registry, firewall, or homelab DNS only.
- Decide whether state backend is local-private, S3-compatible, or Terraform Cloud.

## What Remains Manual For Now

- Initial cluster bootstrap.
- First install of GitOps controllers.
- Secret bootstrap and emergency break-glass credentials.
- Hardware/BIOS/storage firmware changes.
- Recovery from total cluster or node loss.
- Any workload whose official Kubernetes deployment method has not been validated.
