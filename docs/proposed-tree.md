# Proposed Repository Tree

This tree keeps the repo professional and reusable while allowing working nested applications to remain local. The public baseline should expose clean GitOps/IaC interfaces, not raw local app state.

```text
.
├── README.md
├── apps/
│   ├── README.md
│   ├── kasm/
│   ├── examples/
│   └── <local-app-workspaces ignored or separately documented>
├── archive/
│   └── README.md
├── clusters/
│   ├── production/
│   └── staging/
├── docs/
│   ├── architecture.md
│   ├── devsecops-baseline.md
│   ├── gitops-ownership.md
│   ├── proposed-tree.md
│   ├── repo-audit.md
│   ├── repo-restructure-plan.md
│   └── security-scan-paths.md
├── flux/
│   └── apps/
├── infra/
│   ├── networking/
│   └── storage/
├── platform/
│   ├── argocd/
│   ├── backup/
│   ├── drone-ci/
│   ├── flux/
│   ├── k8s-admin/
│   ├── metallb/
│   ├── monitoring/
│   └── traefik/
├── security/
│   ├── kyverno/
│   ├── falco/
│   ├── trivy/
│   ├── networkpolicies/
│   └── rbac/
├── ansible/
│   ├── inventories/
│   ├── roles/
│   └── playbooks/
├── terraform/
│   ├── modules/
│   ├── environments/
│   └── README.md
├── tools/
│   ├── audit/
│   ├── validation/
│   └── image-security/
└── scripts/
    ├── bootstrap/
    ├── maintenance/
    └── README.md
```

## `apps/`

Belongs here:

- Clean app deployment scaffolds.
- App-specific Kustomize bases and overlays.
- App docs and operational runbooks.
- Placeholder-only examples.

Does not belong here:

- Real `.env` files.
- Nested `.git` directories in tracked public content.
- `node_modules`, uploads, logs, or runtime data.
- Raw Docker Compose stacks unless explicitly documented as migration source.

## `platform/`

Belongs here:

- Kubernetes platform services: Argo CD, Flux, Traefik, MetalLB, Longhorn-related ingress, monitoring, backup, Drone CI, dashboards.
- Platform service README files with ownership and secret handling.
- Helm values and Kustomize overlays for platform services.

Does not belong here:

- Generated `kubectl get all -o yaml` exports.
- Live event dumps, endpoints snapshots, or unmanaged backups.
- Real secrets.

## `infra/`

Belongs here:

- Cluster-adjacent infrastructure manifests such as storage classes and networking test manifests.
- Infrastructure documentation that is not provider-managed Terraform.

Does not belong here:

- Provider state.
- Secrets.
- One-off debug workloads without documentation.

## `clusters/`

Belongs here:

- Cluster bootstrap entry points.
- Environment-specific GitOps controller wiring.
- Minimal references into `platform/`, `apps/`, and `flux/`.

Does not belong here:

- App source code.
- Runtime exports.
- Provider credentials.

## `docs/`

Belongs here:

- Architecture diagrams.
- Security baseline.
- Ownership matrix.
- Migration plans.
- Runbooks.
- Manual procedures.

Does not belong here:

- Secret values.
- Large generated outputs.
- Files that must be applied directly without review.

## `tools/`

Belongs here:

- Local validation wrappers.
- Audit helpers.
- Lint and scan helper scripts.

Does not belong here:

- Scripts that become the only source of infrastructure truth.
- Scripts containing credentials or hardcoded cluster assumptions.

## `security/`

Belongs here:

- Kyverno policies.
- Falco rules.
- Trivy configuration.
- RBAC review docs.
- NetworkPolicy baselines.

Does not belong here:

- Live incident evidence.
- Private detection rules with sensitive environment details.

## `ansible/`

Belongs here:

- Linux node hardening roles.
- SSH, firewall, auditd, fail2ban, ClamAV, and optional Maldet roles.
- Example inventories with placeholder hosts.

Does not belong here:

- Real inventories.
- Vault passwords.
- Private SSH material.

## `terraform/`

Belongs here:

- Provider modules.
- Environment examples.
- Remote state documentation.
- DNS, object storage, registry, IAM, and firewall resources.

Does not belong here:

- `.terraform/`.
- `*.tfstate`.
- Real `*.tfvars`.
- Provider credentials.

## `scripts/`

Belongs here:

- Bootstrap wrappers.
- Maintenance helpers.
- Human-run operational scripts with dry-run modes where possible.

Does not belong here:

- Unreviewed deployment scripts that bypass GitOps.
- Scripts that apply cluster changes without explicit operator action.

## `archive/`

Belongs here:

- README files describing where retired/private/generated material lives.
- Sanitized historical notes.

Does not belong here:

- Real backups.
- Raw cluster exports.
- Database dumps.
- Private project payloads.
