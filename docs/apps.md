# App Onboarding Guide

This repo does not contain application code. Each app is managed in its own Git repository and deployed to the cluster via versioned container images and/or Helm charts.

## Standard App Repo Structure (Recommended)
```
repo-root/
├── helm/                # Helm chart for the app (or a /deploy folder)
├── backend/             # if applicable
├── frontend/            # if applicable
├── .github/workflows/   # CI pipeline
└── README.md
```

## CI/CD Recommendations
- Build and push container images on every release tag.
- Publish Helm chart packages or update image tags in chart values.
- Use semantic versioning for app releases.

## Deploying Apps From This Repo
Choose one method:
1. **Helm values override in this repo**
   - Keep a values file under `infra/` or `platform/` that references the image tag from the app repo.
2. **GitOps controller**
   - ArgoCD or Flux watches this repo for platform changes and watches app repos for app releases.

## Version Pinning
Always pin app versions in platform manifests:
- Image tags should be immutable (avoid `latest`).
- Helm chart versions should be explicit.

## Example Values Override
```yaml
image:
  repository: ghcr.io/yourorg/kwiki
  tag: 1.2.3
```

## DNS and Ingress
- Keep DNS and ingress rules in this repo for consistency.
- App repos should only define application services and deployment logic.
