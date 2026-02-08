# ArgoCD Platform Manifests

This folder contains manifests to expose ArgoCD using Traefik.

## Files
- `argocd-cmd-params-cm.yaml`: enables HTTP mode for TLS termination at Traefik
- `ingressroute.yaml`: Traefik TLS termination (recommended)
- `ingressroute-tcp.yaml`: TLS passthrough to ArgoCD

## Apply
```bash
kubectl apply -f platform/argocd/argocd-cmd-params-cm.yaml
kubectl apply -f platform/argocd/ingressroute.yaml
kubectl -n argocd rollout restart deployment argocd-server
```

## Alternate (TLS passthrough)
```bash
kubectl apply -f platform/argocd/ingressroute-tcp.yaml
```
