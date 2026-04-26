# Repository Restructure Plan

This plan keeps the repository safe for public GitHub and useful as a B2B portfolio/reference project. It does not require deleting anything immediately or rewriting history.

## Goals

- Present a clean production-style GitOps/IaC/DevSecOps baseline.
- Keep public content reusable and sanitized.
- Separate source-of-truth manifests from generated exports, backups, and local app checkouts.
- Make ownership boundaries clear between Flux, Argo CD, Ansible, Terraform, and manual bootstrap scripts.

## Phase 0: Freeze Risky Inputs

- Keep `.env`, nested Git repos, `node_modules`, runtime uploads, and backup dumps ignored.
- Do not publish `apps/CyberLynxBlog/.env`.
- Do not commit raw `apps/kwiki` until it is sanitized.
- Do not use `platform/exports` or `platform/exports-clean` as GitOps source-of-truth.

## Phase 1: Document Current State

- Keep `docs/repo-audit.md` as the current risk register.
- Keep `docs/public-safety-checklist.md` as the public release gate.
- Keep `docs/proposed-tree.md` as the target tree.
- TODO: Add owners for each subtree.

## Phase 2: Define Controller Ownership

Use one reconciler per subtree:

- Flux: app/platform kustomizations under `flux/` where Flux is the controller.
- Argo CD: Argo CD apps under `platform/argocd/` and `clusters/*/argocd-*` only where Argo CD owns the target.
- Manual bootstrap scripts: one-time cluster creation, controller installation, and secret bootstrap.
- Ansible: Linux host configuration and hardening.
- Terraform: cloud, DNS, registry, object storage, and provider resources.

TODO: decide whether Flux or Argo CD is the primary public demo GitOps engine. Running both is fine for a lab, but portfolio documentation should make controller boundaries explicit.

## Phase 3: Sanitize Or Archive Risky Areas

### `QloudK-Backup`

Current status: not present in this checkout. Keep ignored by default.

Plan:

- If restored locally, inspect offline for secrets, dumps, customer data, and private keys.
- Keep real backups in private storage only.
- Public repo should contain `archive/README.md` and restore runbooks, not backup payloads.

### `platform/exports`

Current status: tracked live cluster export-style manifests.

Plan:

- Treat as historical evidence, not GitOps source.
- Move to private archive or replace with sanitized summaries after review.
- TODO: verify whether any files include real endpoints, tokens, service account material, event history, or private domains before public release.

### `platform/exports-clean`

Current status: tracked cleaned export-style manifests but still generated from live state.

Plan:

- Review with the same standard as `platform/exports`.
- Keep only intentionally curated examples if needed.
- Prefer documenting generated-export workflow instead of storing large generated output.

### `apps/kasm`

Current status: safe scaffold with placeholders.

Plan:

- Keep public.
- Add official Kasm Helm/manifests only after upstream validation.
- Keep Flux Kustomization suspended until secrets and hostnames are ready.

### `apps/kwiki`

Current status: untracked app checkout with nested `.git`, `node_modules`, runtime uploads, local logs, backup files, Traefik auth artifacts, and app manifests.

Plan:

- Keep ignored for now.
- Create a clean `apps/kwiki-public/` or sanitize `apps/kwiki/` in a separate commit after manual review.
- Remove nested `.git`, generated dependencies, uploads, logs, local auth, and backup artifacts from the public version.
- Replace sensitive values with `.example` files.

### `platform/backup`

Current status: useful public platform content if templates remain placeholders.

Plan:

- Keep `README.md`, namespaces, schedules, PVCs, and sanitized object storage templates.
- Ensure MinIO and Velero secrets are examples only.
- Add restore validation documentation.

### `platform/monitoring`

Current status: useful public platform content, with old backup ingress files.

Plan:

- Keep sanitized Prometheus/Grafana values and ingress examples.
- Review `old-backup/` and remove or move to private archive after documentation.
- Add alerting and dashboard docs without private endpoints.

## Phase 4: Add Security Baseline

Add public-safe examples and runbooks for:

- Linux hardening.
- SSH hardening.
- Firewall baseline.
- `auditd`.
- `fail2ban`.
- ClamAV.
- Maldet only for web/upload/file nodes.
- Trivy image, manifest, and filesystem scanning.
- Kyverno policies.
- Falco runtime detection.
- Kubernetes RBAC review.
- NetworkPolicies.
- Backup and restore notes.

## Phase 5: CI And Review Gates

- Add secret scanning with Gitleaks or TruffleHog.
- Add Trivy filesystem and Kubernetes manifest scanning.
- Add YAML linting and kustomize rendering checks.
- Add markdown linting if desired.
- TODO: add CI only after noisy generated exports are addressed.

## Safe Migration Steps

1. Commit documentation and `.gitignore` safeguards.
2. Keep risky local app directories untracked.
3. Open issues for each risky directory instead of deleting immediately.
4. Create sanitized replacements or examples in small, reviewable commits.
5. Move real backup/export payloads to private storage.
6. Add CI guardrails after sensitive content is removed from the public tree.
7. Only then promote the repository as public portfolio material.
