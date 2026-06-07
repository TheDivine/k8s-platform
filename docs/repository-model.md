# Repository Model

This document defines where content belongs in this public Kubernetes platform repository and what should stay private.

## `apps/`

Belongs here:

- public-safe app deployment scaffolds
- app-specific Kustomize bases and overlays
- app runbooks and architecture docs
- placeholder-only secret examples

Should stay private:

- application source code from private products
- nested `.git` repositories
- uploads, logs, runtime data, and `.env` files
- real app secrets or customer data

## `platform/`

Belongs here:

- shared Kubernetes platform services
- Argo CD, Flux, Traefik, MetalLB, monitoring, backup, Drone CI, dashboard examples
- Helm values and Kustomize manifests that are sanitized
- README files explaining ownership, secrets, and rollback
- approved public routes and ExternalDNS annotations

Should stay private:

- internal-only domains and private addresses
- real credentials
- environment-specific node selectors unless documented as examples
- generated cluster exports

## `infra/`

Belongs here:

- cluster-adjacent storage and networking examples
- benchmark or test manifests when documented
- non-provider Kubernetes infrastructure manifests

Should stay private:

- provider credentials
- private storage endpoints
- hostnames, private IPs, or node-specific values that identify real infrastructure

## `clusters/`

Belongs here:

- cluster GitOps entry points
- environment-level references into `platform/`, `apps/`, and `flux/`
- bootstrap documentation and controller wiring examples

Should stay private:

- kubeconfigs
- cluster admin credentials
- private bootstrap tokens
- unreviewed live exports

## `flux/`

Belongs here:

- Flux `Kustomization`, `GitRepository`, and app wiring examples
- suspended or placeholder app wiring for incomplete workloads
- clear paths into public-safe app overlays

Should stay private:

- credentials for private Git sources
- deploy keys
- provider tokens

## `docs/`

Belongs here:

- architecture
- operating model
- public/private boundary decisions
- runbooks
- migration plans
- safety checklists
- public-safe references and diagrams

Should stay private:

- incident evidence with sensitive values
- customer data
- raw secrets or command outputs exposing private topology

## `archive/`

Belongs here:

- sanitized historical notes
- README files that explain where retired or private content moved

Should stay private:

- real backups
- generated exports
- database dumps
- unreviewed tarballs

## Supporting Folders

- `infra-security/`: public-safe security automation examples and SOPs. Real inventories and host data belong in a private repo.
- `terraform/`: public examples only. Real Terraform belongs in a private repo with private state.
- `ansible/`: public scaffold only. Real playbook execution should use private inventories and vault material.
- `security/`: future policy examples such as Kyverno, Falco, NetworkPolicies, RBAC review, and Trivy config.
- `tools/` and `scripts/`: helper commands and local checks, not the source of truth for infrastructure state.
