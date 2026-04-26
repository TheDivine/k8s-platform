# Repository Public Safety Audit

Date: 2026-04-26

Scope: local repository inspection only. No cluster commands, no `kubectl apply`, no secret rotation, no deletion, and no Git history rewrite were performed.

## Executive Summary

This repository is close to a useful public B2B GitOps and platform engineering reference, but it should not be treated as clean until risky local app checkouts, live cluster exports, and secret-shaped manifests are reviewed and either removed from the public tree or replaced with sanitized examples.

The safest public-facing story is a curated GitOps/IaC baseline: `clusters/`, `infra/`, `platform/`, `flux/`, selected `apps/`, and `docs/` should contain reusable manifests, examples, runbooks, and diagrams. Generated exports, backups, nested application repos, runtime uploads, local `.env` files, and raw Kubernetes Secrets should stay out of Git.

## Current Folder Structure

Observed top-level areas:

- `apps/`: contains the tracked `apps/kasm` scaffold plus untracked app checkouts and app artifacts.
- `clusters/`: production/staging GitOps bootstrap and cluster-level wiring.
- `docs/`: platform documentation and diagrams.
- `flux/`: app-level Flux wiring, currently including Kasm.
- `infra/`: storage and networking infrastructure manifests.
- `platform/`: platform components such as Argo CD, Flux, Traefik, MetalLB, backup, monitoring, Drone CI, and cluster exports.
- `archive/`: public-facing archive placeholder.
- `QloudK-Backup/`: not present in the current checkout, but referenced as a historical backup area.

## Public-Safe Areas

These areas are generally suitable for public GitHub after normal review:

- `README.md`
- `docs/` runbooks, diagrams, public checklists, and architecture notes.
- `clusters/` GitOps bootstrap manifests when domains, repo URLs, and cluster names are intentionally public lab examples.
- `infra/storage/` and `infra/networking/` when they contain generic lab manifests only.
- `platform/argocd/`, `platform/flux/`, `platform/traefik/`, and `platform/metallb/` after confirming they contain no private hostnames, auth material, or internal-only ranges.
- `platform/backup/` only when secrets remain templates and object storage endpoints are placeholders.
- `platform/monitoring/` only when ingress hostnames and values are sanitized.
- `apps/kasm/` because it is a scaffold with placeholders and no real Kasm credentials.

## Risk Findings

### High Risk

- `apps/CyberLynxBlog/.env` exists locally and includes sensitive variable names such as API keys, admin token, admin user, and admin password. Values were not printed during this audit. Keep this file ignored and do not commit it.
- Nested Git repositories were found at:
  - `apps/Cybelynx-blog-content/.git`
  - `apps/CyberLynxBlog/.git`
  - `apps/CyberLynxBlog/content/.git`
  - `apps/kwiki/.git`
- `apps/kwiki/backend/node_modules` and nested `node_modules` directories exist locally. These are generated dependencies and should not be committed.
- `apps/kwiki/backend/uploads` contains runtime upload assets and logs. Treat as application data, not IaC.
- `platform/drone-ci/server/droneserver-secret.yaml` is a Kubernetes `Secret` manifest. It appears structured as a secret template/commented example, but the file name and kind are risky for public review. TODO: replace with `droneserver-secret.example.yaml` or SOPS/SealedSecrets documentation before public release.

### Medium Risk

- `platform/exports/` and `platform/exports-clean/` contain live cluster export-style manifests, including `events`, `endpoints`, generated `all.yaml`, RBAC, CRDs, configmaps, and namespace snapshots. These can reveal internal topology, domains, IPs, service names, operational history, and overly broad RBAC. They should be treated as evidence/reference artifacts, not production GitOps source.
- `platform/exports/_cluster/crds.yaml` and `platform/exports-clean/_cluster/crds.yaml` are large generated CRD exports. Keep out of the curated public tree unless there is a specific reason to show them.
- `platform/monitoring/old-backup/` contains old ingress backups. TODO: review for hostnames and remove or archive after documentation.
- `apps/kwiki/traefik/auth`, `apps/kwiki/traefik/basic-atuh.txt`, and `apps/kwiki/traefik/traefik.json` require manual review before any public commit.
- `apps/kwiki/crd-backup.yaml` appears to be a backup/export artifact and should not be public without sanitization.

### Lower Risk / Needs Review

- Real domains or lab domains appear in several ingress examples. Public exposure may be acceptable for portfolio material, but TODO: decide whether to replace with `example.com` or intentionally keep as lab branding.
- `platform/backup/minio/secret.template.yaml`, `platform/backup/velero/credentials.secret.template.yaml`, and `apps/kasm/kustomize/base/secrets.example.yaml` are acceptable only if they keep placeholder values.
- `docs/` may contain operational commands and hostnames. TODO: review docs for private IPs, internal DNS names, usernames, and provider details.

## Negative Findings

The filename scan did not find:

- kubeconfig files
- `.key`, `.pem`, `.p12`, or `.pfx` files
- `.crt` files
- archive dumps such as `.tgz`, `.tar`, `.gz`, or `.sql`
- Terraform state directories

This does not prove the repository is free of secrets. Run the manual secret scanning commands in the checklist before publishing.

## Recommended Ownership Model

| Area | Recommended manager | Notes |
| --- | --- | --- |
| `clusters/` bootstrap | Manual bootstrap scripts, then Flux or Argo CD | Keep bootstrap small and reproducible. |
| `flux/` | Flux | Use for app/platform reconciliation where Flux is the selected controller. |
| `platform/argocd/` | Argo CD | Manage Argo CD itself carefully; avoid controller conflicts with Flux. |
| `platform/traefik/`, `platform/metallb/`, `platform/monitoring/`, `platform/backup/` | Flux or Argo CD | Pick one controller per subtree. Document ownership. |
| `infra/` | Terraform for external/cloud resources, Ansible for host setup, GitOps for cluster manifests | Keep cloud state and Ansible inventories private. |
| Host hardening | Ansible | Linux, SSH, firewall, auditd, fail2ban, ClamAV, and selected Maldet setup. |
| Kubernetes policies | GitOps | Kyverno, NetworkPolicies, RBAC, Falco, and Trivy policy checks. |
| App workloads | GitOps | `apps/kasm` can be Flux-managed after official Kasm details are validated. |

## Required Decisions

- TODO: Decide whether `platform/exports/` and `platform/exports-clean/` should be moved to a private archive repo or replaced with sanitized summaries.
- TODO: Decide whether `apps/kwiki` should become a sanitized portfolio app, remain private, or be replaced with a clean example app.
- TODO: Decide whether `apps/CyberLynxBlog` and `apps/Cybelynx-blog-content` remain separate repos and are referenced as submodules/docs only.
- TODO: Decide whether Flux or Argo CD is the primary GitOps controller for each subtree.
- TODO: Decide public domain policy: real lab domains vs `example.com` placeholders.
