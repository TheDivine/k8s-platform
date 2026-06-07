# App Onboarding Guide

Application source code should normally remain in its own Git repository and
be deployed through immutable images and a reviewed Argo CD registry entry.

The complete production procedure is:

- [Add A New Application With Argo CD](argocd-app-onboarding.md)
- [Platform And Application Status](component-status.md)

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

## Production Deployment Model

1. The application repository contains source code and its production
   Kubernetes package.
2. CI publishes an immutable image.
3. `k8s-platform` contains one
   `clusters/production/app-registry/*.app.yaml` registration file.
4. The Argo CD ApplicationSet generates an Application.
5. Argo CD pulls the app repository directly.

No application repository needs to be downloaded onto the cluster server.

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

## DNS And Ingress

An app repo may own its route when the platform team reviews the hostname and
annotations. ExternalDNS creates records only for approved zone filters.
