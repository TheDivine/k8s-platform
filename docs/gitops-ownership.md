# GitOps And IaC Ownership

This matrix defines which system should own each kind of change. The goal is to reduce manual drift while avoiding conflicts between controllers.

## Ownership Matrix

| Domain | Owner | Examples | Notes |
| --- | --- | --- | --- |
| Kubernetes app manifests | Argo CD or Flux | Kasm, future app overlays | Pick one controller per app path. |
| Kubernetes platform manifests | Argo CD or Flux | Traefik, MetalLB, monitoring, backup | Avoid dual ownership of the same resource. |
| Route-derived DNS records | ExternalDNS through Flux | app and UI A records, ownership TXT records | Restricted by zone filters and TXT owner ID. |
| Cluster bootstrap | Manual bootstrap, then GitOps | first controller install, initial repo sync | Keep bootstrap minimal and documented. |
| Provider infrastructure | Terraform or reviewed provider workflow | DNS zones, mail records, object storage, cloud firewall, IAM | ExternalDNS owns only route-derived records. |
| OS/node configuration | Ansible | SSH, firewall, packages, auditd, fail2ban, ClamAV | Test in check mode first. |
| Reusable Kubernetes packaging | Helm | app/platform charts | Use Helm as packaging, GitOps as deployment. |
| Policy as code | GitOps | Kyverno, NetworkPolicies, RBAC review artifacts | Start in audit mode where possible. |
| Local operational helpers | Scripts/tools | validation, scanning, report generation | Scripts wrap workflows; they should not replace IaC. |
| Emergency actions | Manual runbook | break-glass secrets, disaster recovery | Document commands and approval conditions. |

## Argo CD Ownership

Good fit:

- App-of-apps pattern.
- Platform bundles where visual app health and sync workflows are useful.
- Curated app deployments.

Rules:

- Do not let Argo CD and Flux own the same path or resource.
- Keep Argo CD admin UI protected.
- Store secrets outside public Git.

## Flux Ownership

Good fit:

- Cluster bootstrap through `flux-system`.
- Path-based `Kustomization` reconciliation.
- App wiring such as `flux/apps/kasm/kustomization.yaml`.
- Suspended placeholders for future apps.

Rules:

- Use `suspend: true` for incomplete app scaffolds.
- Keep source references explicit.
- Document target namespace and pruning behavior.

## Terraform Ownership

Good fit:

- DNS zone creation, nameservers, mail records, and non-Kubernetes records.
- Object storage buckets for backups.
- Registry resources.
- Cloud firewall or load balancer resources when external providers are used.
- IAM/service accounts for backup or DNS automation.

Rules:

- Never commit `*.tfstate`, `.terraform/`, real `*.tfvars`, or provider credentials.
- Use remote state when real resources are introduced.
- Run `terraform plan` in review before any apply.

## ExternalDNS Ownership

Good fit:

- A and CNAME records derived from Kubernetes Ingress resources.
- Traefik IngressRoute hostnames.
- Cloudflare proxy state declared by route annotation.
- TXT ownership records for collision avoidance.

Rules:

- Keep `domainFilters` explicit.
- Use a unique TXT owner per cluster.
- Do not import mail, validation, or unrelated manual records casually.
- Use `upsert-only` until deletion behavior and recovery are tested.
- DNS record creation does not replace application health checks.

## Ansible Ownership

Good fit:

- Linux hardening.
- SSH baseline.
- Firewall baseline.
- Package installation.
- auditd/fail2ban/ClamAV/Maldet setup.
- Kubernetes node prerequisites.

Rules:

- Keep real inventories private.
- Keep vault material private.
- Prefer idempotent roles and check mode.

## Helm Ownership

Good fit:

- Packaging reusable deployments.
- Values-driven platform/app components.
- Upstream chart consumption.

Rules:

- Helm should not be the only state owner. Argo CD or Flux should reconcile Helm releases where possible.
- Keep real values and secrets out of public `values.yaml`.

## Scripts And Tools Ownership

Good fit:

- Validation helpers.
- Secret scanning wrappers.
- Kustomize/Helm rendering checks.
- Backup verification helpers.

Rules:

- Scripts should be wrappers around documented IaC/GitOps workflows.
- Scripts should support dry-run or read-only modes where practical.
- Scripts must not contain embedded credentials.

## Manual Actions

Keep manual for now:

- Initial cluster creation.
- First GitOps controller bootstrap.
- Secret bootstrap.
- Hardware, disk, firmware, and network switch changes.
- Emergency recovery when GitOps is unavailable.

Every manual action should eventually have a runbook and, where safe, an automated equivalent.

## TODOs

- TODO: choose the default public example controller: Argo CD, Flux, or both with strict boundaries.
- TODO: define ownership for each `platform/` subtree.
- TODO: define whether app workspaces are in-repo, external repos, or submodules.
- TODO: add CI checks for controller ownership drift.
