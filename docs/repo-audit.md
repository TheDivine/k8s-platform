# Repository Audit

This audit is documentation-only. It records the current repository shape, likely ownership boundaries, and safe next steps for turning this home-lab platform repository into a reusable DevSecOps baseline. No cluster changes, file moves, secret rotation, or destructive cleanup were performed for this report.

## Current Repository Overview

The repository is now centered around a GitOps/platform baseline:

- Kubernetes cluster bootstrap and controller wiring under `clusters/`.
- Reusable infrastructure manifests under `infra/`.
- Platform services under `platform/`.
- Application examples and local application workspaces under `apps/`.
- Flux app wiring under `flux/`.
- Runbooks, audits, and architecture docs under `docs/`.
- Archive placeholder documentation under `archive/`.

Generated cluster exports under `platform/exports/` and `platform/exports-clean/` are ignored and no longer tracked. Local application workspaces such as `apps/kwiki`, `apps/CyberLynxBlog`, and `apps/Cybelynx-blog-content` can stay nested locally, but should be treated as product/application workspaces rather than the public platform source of truth until they are sanitized and documented.

## Current Top-Level Folders

| Folder | Current role | Target role |
| --- | --- | --- |
| `apps/` | Kasm scaffold plus local app workspaces | Public app scaffolds, GitOps app overlays, and documented examples |
| `archive/` | Placeholder doc | Notes for retired/generated/private material, not backup payloads |
| `clusters/` | Production/staging bootstrap and GitOps controller manifests | Cluster entry points and environment-level GitOps wiring |
| `docs/` | Operational and platform docs | Primary public documentation, architecture, decisions, and runbooks |
| `flux/` | Flux app wiring | Flux `Kustomization` and `GitRepository` ownership trees |
| `infra/` | Networking and storage manifests | Cluster-adjacent infrastructure manifests and future IaC handoff docs |
| `platform/` | Argo CD, Flux, Traefik, MetalLB, backup, monitoring, Drone, dashboard | Platform services managed by GitOps with clear controller ownership |

No tracked `tools/`, `security/`, `ansible/`, `terraform/`, or `scripts/` directories exist yet. Those should be introduced intentionally in later commits.

## Important Files Found

- `clusters/production/kustomization.yaml`: current production cluster entry point.
- `clusters/production/flux-system/gotk-components.yaml`: Flux controller component manifest.
- `clusters/production/argocd-app-platform.yaml` and `argocd-app-infra.yaml`: Argo CD app wiring.
- `flux/apps/kasm/kustomization.yaml`: suspended Flux wiring for the Kasm scaffold.
- `apps/kasm/`: safe Kasm Kubernetes scaffold with placeholder-only secret example.
- `platform/argocd/`: Argo CD manifests and ingress routing.
- `platform/backup/minio/` and `platform/backup/velero/`: backup platform manifests and templates.
- `platform/drone-ci/`: Drone server, runner, and sanitized example secrets.
- `platform/monitoring/`: Prometheus/Grafana/Longhorn ingress and values.
- `platform/k8s-admin/`: dashboard-related experiments and variants.
- `.gitignore`: now excludes generated exports, nested app checkouts, runtime data, secrets, and local metadata.
- `.gitattributes`: suppresses diffs for removed unsafe historical secret paths.

## Duplicate, Outdated, Misplaced, Or Unclear Files

These are findings only. Do not move or delete them without a separate migration commit.

- `platform/k8s-admin/` contains several dashboard variants with overlapping names such as `dashboard-kong.yaml`, `dashboard-split.yaml`, `dashboard-web-plus-kong.yaml`, `k8s-dashboard.yaml`, and `20-dashboard-ingressroute.yaml`. TODO: pick one supported dashboard pattern and archive the rest as examples or notes.
- `platform/monitoring/old-backup/` contains old ingressroute files. TODO: decide whether these are historical references or should become archive documentation.
- `platform/drone-ci/drone.txt` is unclear as a tracked platform artifact. TODO: review and convert to README/runbook content if useful.
- `infra/networking/*iperf*` looks like benchmark/test workload material. TODO: decide whether it belongs in `tools/`, `apps/examples/`, or `infra/networking/examples/`.
- `infra/storage/local-storage-provisioner.txt` may be notes rather than a manifest. TODO: convert to Markdown if it is documentation.
- `apps/helmtest/wikimeida` is an ignored local Helm test tree with a likely typo in the directory name. TODO: keep local, sanitize, or replace with a clean Helm chart example later.
- `apps/kwiki` includes app code, Kubernetes manifests, Traefik manifests, BGP files, uploads, logs, and a nested Git repo. It can stay nested locally, but public GitOps wiring should be introduced separately and deliberately.
- `apps/CyberLynxBlog` and `apps/Cybelynx-blog-content` are nested app/content repos. Keep as application workspaces or document them as external repos rather than absorbing raw local repo state into the platform baseline.

## Backup And Archive Folders

- `archive/README.md` correctly states that real backups and live exports should not be stored in this public repository.
- `platform/exports/` and `platform/exports-clean/` exist locally but are ignored and untracked. Treat them as local generated evidence only.
- `platform/backup/` is a valid platform area for MinIO and Velero manifests, provided credentials remain templates/examples only.
- `QloudK-Backup/` is referenced by ignore rules but is not present as tracked content. If restored locally, it should stay private until audited.

## Possible Secret-Risk Files

Do not print or copy values from these files into issues, PRs, or docs.

- `apps/CyberLynxBlog/.env`: local environment file. Must not be committed.
- `apps/CyberLynxBlog/.env.example`: example file; verify placeholders before public use.
- `apps/kwiki/traefik/auth` and `apps/kwiki/traefik/basic-atuh.txt`: local auth-looking files. Keep ignored and review manually before any future public commit.
- `apps/kwiki/traefik/traefik.json` and `apps/kwiki/traefik/ns.json`: local runtime/config exports. Review before use.
- `platform/backup/minio/secret.template.yaml`: acceptable only as a placeholder template.
- `platform/backup/velero/credentials.secret.template.yaml`: acceptable only as a placeholder template.
- `platform/drone-ci/server/droneserver-secret.example.yaml`: acceptable only as a placeholder example.
- `apps/kasm/kustomize/base/secrets.example.yaml`: acceptable only as a placeholder example.

## GitOps Readiness Findings

- The repo already contains both Flux and Argo CD patterns. That is acceptable for a lab, but public baseline documentation must define controller boundaries to avoid dual ownership.
- `apps/kasm` is a good example of safe GitOps-first scaffolding: namespace, PVCs, ingress placeholders, suspended Flux wiring, and docs.
- `clusters/production` currently mixes Argo CD and Flux bootstrap concepts. TODO: document which controller owns each subtree.
- `platform/backup`, `platform/monitoring`, `platform/argocd`, `platform/flux`, `platform/metallb`, and `platform/traefik` are candidates for GitOps management after ownership is formalized.
- `platform/k8s-admin` needs consolidation before it is production-style GitOps.

## IaC Readiness Findings

- There is no tracked Terraform baseline yet. DNS, object storage, registry, cloud firewall, and provider IAM should be modeled in `terraform/` later if those resources are external to the cluster.
- There is no tracked Ansible baseline yet. Linux node hardening, SSH, firewall, auditd, fail2ban, ClamAV, package baselines, and Kubernetes node prerequisites should be modeled in `ansible/`.
- Shell scripts currently exist inside app/platform subtrees. Scripts should become wrappers or validation tools, not the source of truth for infrastructure state.

## Security Baseline Readiness Findings

- Secret examples are moving in the right direction, but a repository-wide secret scanning gate is still needed.
- No tracked Kyverno/Falco/Trivy baseline exists yet.
- NetworkPolicies are present in generated local exports but not curated as a public baseline.
- Backup docs and Velero/MinIO examples exist; restore validation and schedule policy need clearer runbooks.
- Kubernetes RBAC exists in several places, but a documented RBAC review process is still needed.

## Risks

- Historical Git commits may still contain values that were later sanitized. Treat old secrets as exposed before publishing broadly.
- Nested app workspaces can contain runtime data, generated dependencies, local env files, and nested `.git` directories.
- Live cluster exports can expose topology and operational state if re-added.
- Multiple GitOps controllers without ownership boundaries can drift or fight over resources.
- Dashboard and admin ingress examples can expose sensitive UIs if copied without access controls.

## Recommended Next Commits

1. Add documentation-only ownership and security baseline docs. This commit.
2. Add empty/safe folder scaffolds for `tools/`, `security/`, `ansible/`, `terraform/`, and `scripts/` with README files only.
3. Add CI linting and secret-scan configuration after local noisy paths are excluded.
4. Add a curated `policies/` or `security/kyverno/` baseline with audit-mode policies.
5. Add Ansible node baseline roles in check-mode friendly form.
6. Add Terraform examples with no state and no real provider credentials.
7. Consolidate `platform/k8s-admin` into one documented dashboard deployment pattern.
8. Choose Flux or Argo CD ownership per platform subtree and document it in code-adjacent README files.
