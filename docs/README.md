# Documentation Index

This directory is organized so a reviewer can understand the repository from architecture to operations without reading every file at once.

## Start Here

1. [Architecture](architecture.md) explains the platform direction, public/private repo split, GitOps flow, and security/monitoring model.
2. [Repository Model](repository-model.md) explains what belongs in each top-level folder.
3. [Public And Private Boundary](public-private-boundary.md) explains what can be public and what must stay private.
4. [Secret Management](secret-management.md) explains how real secrets should be handled outside public Git.
5. [Public Safety Checklist](public-safety-checklist.md) is the pre-commit/pre-push checklist.

## Strategy And Decisions

- [IaC Strategy](iac-strategy.md): Terraform, Ansible, GitOps, and manual/bootstrap ownership.
- [GitOps And IaC Ownership](gitops-ownership.md): ownership matrix for Argo CD, Flux, Terraform, Ansible, Helm, scripts, and manual actions.
- [Repository Restructure Plan](repo-restructure-plan.md): phased migration plan and rollback notes.
- [Proposed Repository Tree](proposed-tree.md): target repository layout.
- [Repository Audit](repo-audit.md): current findings and remaining cleanup work.

## Platform Runbooks

- [Argo CD](argocd.md)
- [Argo CD Beginner Workflow](argocd-workflow.md)
- [Production Endpoint Inventory](endpoint-inventory.md)
- [Credential Source And Access Map](credential-access.md)
- [Cloudflare DNS And Certificates](cloudflare-dns-and-certificates.md)
- [External Secrets Migration](external-secrets-migration.md)
- [Production Change Log: 2026-06-07](live-change-log-2026-06-07.md)
- [Flux](flux.md)
- [Flux UI](flux-ui.md)
- [Drone CI Runner](drone-ci-runner.md)
- [Backup and Reproducibility Plan](backup.md)
- [Deploy Backups From Scratch](deploy-backups-from-scratch.md)
- [Platform Ops Guide](ops.md)

## Security

- [Security Baseline](security-baseline.md)
- [Security Scan Paths](security-scan-paths.md)
- [Ansible Private Repo Plan](ansible-private-repo-plan.md)
- [Terraform Private Repo Plan](terraform-private-repo-plan.md)

## Apps And Delivery

- [App Onboarding Guide](apps.md)
- [Real Project Workflow](real-project-workflow.md)
- [Manual Deploy Checklist](manual-deploy-checklist.md)
- [Repository Strategy](repos.md)
- [Roadmap](roadmap.md)

## References

- [Tooling Reference](tooling-reference.md)
- [Architecture Diagrams](diagrams/platform-architecture.md)
- [Security Observability Diagrams](diagrams/security-observability.md)
- [Kasm Architecture](diagrams/kasm-architecture.md)

## Removed Duplicate Docs

The following pages were reviewed before removal. Their useful content is
retained in the listed canonical pages.

| Removed page | Decision | Canonical replacement |
| --- | --- | --- |
| `docs/reference-links.md` | Remove duplicate link collection | `docs/tooling-reference.md` |
| `docs/repo-operating-model.md` | Split broad policy into clearer ownership boundaries | `docs/repository-model.md` and `docs/public-private-boundary.md` |
| `docs/devsecops-baseline.md` | Consolidate duplicated security guidance | `docs/security-baseline.md`, `docs/secret-management.md`, and `docs/security-scan-paths.md` |
| `docs/structure.md` | Replace the older, incomplete folder description | `docs/repository-model.md` and `docs/proposed-tree.md` |
| `docs/prometheus.md` | Remove stale install notes and an obsolete Grafana Secret name | `docs/ops.md`, `docs/credential-access.md`, and `platform/monitoring/` |
| `docs/backup-setup.md` | Remove the shorter duplicate backup procedure | `docs/backup.md` and `docs/deploy-backups-from-scratch.md` |

Do not recreate a removed page unless it has a distinct owner and purpose that
cannot be represented in the canonical runbook.
