# Production Cluster

This folder should contain the exact manifests or overlays that define your production cluster state.

## Ownership

- Flux reconciles this directory from `main`.
- Flux installs network automation and Argo CD registration resources.
- The Argo CD ApplicationSet reads `app-registry/*.app.yaml`.
- Each registry entry produces one independently visible Argo Application.

## Add An Application

Follow `docs/argocd-app-onboarding.md`. Normal onboarding is performed through
GitHub and does not require a repository checkout on the cluster server.
