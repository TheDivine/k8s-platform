# k8s-platform

This repository tracks the Kubernetes platform and infrastructure setup for the homelab cluster. Application code lives in separate repositories (e.g., `kwiki`, blog) and is referenced from this repo via versioned images/Helm charts.

## Scope
- Cluster platform components: ingress, DNS, monitoring, admin tooling
- Infra manifests: storage classes, provisioners, networking tools
- Documentation for platform operations and app onboarding

## Layout
```
apps/                # local app repos (not tracked here)
platform/            # shared cluster services (ingress, monitoring, etc.)
infra/               # cluster-level manifests (storage, networking)
docs/                # operational docs
QloudK-Backup/        # legacy repo (not tracked here)
```

## How To Use
- Apply platform components from `platform/` as needed.
- Apply infra manifests from `infra/`.
- Track apps separately; publish images/Helm charts from app repos and reference them here.

## App Repos (Separate)
- `kwiki` lives in its own Git repository.
- Blog site lives in its own Git repository.
- Legacy `QloudK-Backup` will be moved to a separate repo.

See `docs/apps.md` for app onboarding guidance.

## GitHub Guidance
- This repo is intended to be pushed as a standalone GitHub repo (platform/infra).
- App repos are linked in docs (not as submodules).

## Next Steps
- Move `QloudK-Backup` to its own repo.
- Add GitOps (ArgoCD or Flux) to reconcile platform and app deployments.
