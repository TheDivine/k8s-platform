# Production Cluster

This folder should contain the exact manifests or overlays that define your production cluster state.

## Example
- `kustomization.yaml` that references:
  - `../../platform/`
  - `../../infra/`
  - app releases pinned to versions

## Deployment
- ArgoCD or Flux watches this folder and reconciles the cluster.
