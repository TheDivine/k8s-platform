# Traefik (Ingress Controller)

This folder is the centralized location for Traefik manifests or Helm values used by the cluster.

## What belongs here
- Helm `values.yaml` for Traefik
- CRDs (if not installed via Helm)
- IngressRoute/Middleware definitions that are global

## How to apply (example)
If using Helm:
```bash
helm repo add traefik https://helm.traefik.io/traefik
helm repo update
helm upgrade --install traefik traefik/traefik -n traefik --create-namespace -f platform/traefik/values.yaml
```

## Notes
- Keep app-specific IngressRoute objects in app repos or in `platform/` if shared.
