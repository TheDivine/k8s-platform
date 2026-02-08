# Flux (flux.kwiki.it.com)

## Purpose
Flux will manage **apps** (e.g., `kwiki` and future portfolio apps). It is automation-first and great for GitOps pipelines.

## Pros
- Lightweight and Git-native
- Easy bootstrap workflow
- Strong automation and reconciliation

## Cons
- No built-in UI (use Weave GitOps for UI)

## Install Flux CLI (local)
Follow the official Flux install instructions for your OS, then verify:
```bash
flux version
```

## Bootstrap Flux
```bash
export GITHUB_TOKEN=<your-token>
export GITHUB_USER=TheDivine

flux bootstrap github \
  --owner=$GITHUB_USER \
  --repository=k8s-platform \
  --branch=main \
  --path=./clusters/production \
  --personal
```

## Weave GitOps UI (for flux.kwiki.it.com)
Flux itself has no UI. Weave GitOps provides a dashboard.

### Install Weave GitOps CLI (local)
Follow the Weave GitOps OSS docs and verify:
```bash
gitops version
```

### Create the dashboard
Weave GitOps OSS recommends creating a dashboard in `flux-system`:
```bash
gitops create dashboard ww-gitops \
  --password=<admin-password> \
  --export > clusters/production/weave-gitops-dashboard.yaml
```

Apply it (GitOps):
```bash
kubectl apply -f clusters/production/weave-gitops-dashboard.yaml
```

### Expose UI with Traefik
Check the service name:
```bash
kubectl -n flux-system get svc
```

Then apply:
```bash
kubectl apply -f platform/flux/ingressroute.yaml
```

## DNS
Point `flux.kwiki.it.com` to the Traefik external IP (MetalLB).

## App GitOps Strategy
- Apps publish container images or Helm charts.
- Flux reconciles them into the cluster from Git.
- Pin versions explicitly (avoid `latest`).
