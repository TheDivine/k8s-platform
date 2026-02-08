# Flux Platform Manifests

This folder contains manifests for the Flux UI (Weave GitOps) ingress.

## Files
- `ingressroute.yaml`: Traefik route for `flux.kwiki.it.com` to Weave GitOps UI.

## Apply
```bash
kubectl apply -f platform/flux/ingressroute.yaml
```

## Note
Confirm the service name and port after installing Weave GitOps:
```bash
kubectl -n flux-system get svc
```
