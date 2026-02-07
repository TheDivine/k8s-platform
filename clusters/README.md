# GitOps Clusters

This folder is a scaffold for GitOps. Each environment (production, staging) should contain the manifests or Kustomize overlays that a GitOps controller syncs to the cluster.

## Suggested Structure
```
clusters/
  production/
    kustomization.yaml
    platform.yaml
    apps.yaml
  staging/
    kustomization.yaml
    platform.yaml
    apps.yaml
```

## How to Use
- Keep platform manifests (ingress, monitoring, storage) in `platform/` and `infra/`.
- In each cluster folder, reference those manifests using Kustomize or HelmRelease objects.
- GitOps controllers (ArgoCD or Flux) should target these directories.
