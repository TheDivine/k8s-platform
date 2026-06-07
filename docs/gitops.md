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

### Register Applications

Flux installs the production Argo CD ApplicationSet from
`clusters/production/argocd-apps`. Argo creates one Application for each
reviewed file under `clusters/production/app-registry`.

### App Repos

Register each deployable app repository through the app registry. Do not point
one broad recursive Application at all of `platform/` or `infra/`; those trees
contain alternatives and incomplete packages.

See `docs/argocd-app-onboarding.md`.

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
