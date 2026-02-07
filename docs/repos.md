# Repository Strategy

This document defines how your GitHub repositories are organized for a professional DevOps portfolio.

## Repos and Purpose
- **k8s-platform** (this repo): cluster platform and infra configuration
- **kwiki**: application repo (MediaWiki deployment app)
- **blog**: portfolio/blog website
- **QloudK-Backup**: legacy/backup repo, separate from platform

## Why Separate Repos
- Clear ownership and scope
- Easier CI/CD pipelines
- Recruiter-friendly portfolio separation
- Avoids submodule friction

## Standard Repo Checklist
Each repo should include:
- `README.md` with setup and deployment steps
- CI pipeline config (GitHub Actions or Drone)
- Versioning strategy (tags/releases)
- License (if public)

## App Repo Expectations
- Build and push container images with version tags
- Publish Helm charts or store chart values in the app repo
- Do not deploy directly into the cluster from the app repo

## Platform Repo Expectations
- Only platform/infra manifests
- Ingress and DNS rules centralized here
- App versions pinned explicitly

## Example: Version Pinning
```yaml
image:
  repository: ghcr.io/yourorg/kwiki
  tag: 1.2.3
```

## Commit Conventions (Recommended)
- `platform:` for platform changes
- `infra:` for infra changes
- `docs:` for documentation
- `ops:` for operational scripts

## Release Strategy (Suggested)
- Tag platform releases when stable: `v0.1.0`, `v0.2.0`
- Tag app releases independently
