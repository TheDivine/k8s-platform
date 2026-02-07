# GitOps Plan (ArgoCD or Flux)

This guide outlines how to evolve the platform into GitOps with either ArgoCD or Flux.

## Option A: ArgoCD (Recommended for visibility)
### Install
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### Access the UI (port-forward)
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

### Register the Platform Repo
Create an ArgoCD Application pointing to:
- Repo: your `k8s-platform` GitHub repo
- Path: `platform/` and/or `infra/`
- Destination: target cluster and namespace

### App Repos
Create separate Applications for each app repo (e.g., `kwiki`).
Pin versions in the app repo and sync from ArgoCD.

## Option B: Flux (Recommended for automation-first)
### Install
```bash
curl -s https://fluxcd.io/install.sh | sudo bash
flux check --pre
```

### Bootstrap
```bash
flux bootstrap github \
  --owner=<your-user> \
  --repository=k8s-platform \
  --branch=main \
  --path=./clusters/production
```

### App Repos
Define `HelmRepository` and `HelmRelease` objects in `k8s-platform` to reference app repos.

## Recommended Directory for GitOps
If you adopt GitOps, add:
```
clusters/
  production/
  staging/
```

## Best Practices
- Use immutable tags
- Lock manifests with commit hashes or version tags
- Separate platform and app lifecycles
- Keep secrets in a secret manager (not Git)
