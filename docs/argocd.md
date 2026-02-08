# ArgoCD (argo.kwiki.it.com)

## Purpose
ArgoCD will manage **platform + infra** resources from this repo. It provides a UI that is excellent for demos, visibility, and audits.

## Pros
- UI with sync/health visibility
- Clear Application model
- Easy to demo in a portfolio

## Cons
- More components to secure
- Requires careful ingress/TLS setup

## Install (Official)
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

## Wait for readiness
```bash
kubectl -n argocd get pods
```

## Access the UI
ArgoCD is not exposed by default. You can either port-forward or expose with Traefik.

### Option A: Port-forward (quick test)
```bash
kubectl -n argocd port-forward svc/argocd-server 8080:443
```

### Option B: Traefik + TLS (recommended)
Two options are provided:

1. **TLS termination at Traefik** (simple)
   - Use `platform/argocd/ingressroute.yaml`
   - Enable HTTP on ArgoCD server via `argocd-cmd-params-cm.yaml`

2. **TLS passthrough** (ArgoCD handles TLS)
   - Use `platform/argocd/ingressroute-tcp.yaml`

Apply (TLS termination):
```bash
kubectl apply -f platform/argocd/argocd-cmd-params-cm.yaml
kubectl apply -f platform/argocd/ingressroute.yaml
kubectl -n argocd rollout restart deployment argocd-server
```

Apply (TLS passthrough):
```bash
kubectl apply -f platform/argocd/ingressroute-tcp.yaml
```

## Initial Admin Password
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

## Create Applications (platform + infra)
Manifests are provided:
- `platform/argocd/app-platform.yaml`
- `platform/argocd/app-infra.yaml`

Apply:
```bash
kubectl apply -f platform/argocd/app-platform.yaml
kubectl apply -f platform/argocd/app-infra.yaml
```

## DNS
Point `argo.kwiki.it.com` to the Traefik external IP (MetalLB).
