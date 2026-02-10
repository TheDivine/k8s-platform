# Flux UI (Weave GitOps) at flux.kwiki.it.com

Flux does not ship a web UI by default. To get a UI for viewing Git sources, Kustomizations, HelmReleases, and reconciliation status, we deploy **Weave GitOps** into `flux-system` and expose it via Traefik.

This repo deploys the UI via Flux itself (GitOps-managed), so you do not manually `kubectl apply` the HelmRelease long-term.

## What Gets Deployed

Files in `clusters/production/`:
- `weave-gitops-dashboard.yaml`
  - `HelmRepository` (OCI chart source at `ghcr.io/weaveworks/charts`)
  - `HelmRelease` named `ww-gitops` (installs the `weave-gitops` chart)
  - Local admin user configuration (bcrypt password hash, not plaintext)
- `flux-ui-ingressroute.yaml`
  - Traefik `IngressRoute` exposing the UI at `https://flux.kwiki.it.com`

`clusters/production/kustomization.yaml` includes both resources, so Flux applies them.

## How It Works (Logic)

1. Flux `GitRepository/flux-system` pulls this `k8s-platform` repo.
2. Flux `Kustomization/flux-system` runs kustomize build on `clusters/production/`.
3. That applies the `HelmRepository` and `HelmRelease` objects.
4. `helm-controller` sees the `HelmRelease` and installs/updates Weave GitOps.
5. Traefik routes `flux.kwiki.it.com` to the Weave GitOps service in `flux-system`.

## DNS and TLS

Prereqs:
- DNS `A` record: `flux.kwiki.it.com` -> Traefik LoadBalancer IP.
- Traefik must have a certificate resolver named `le`.

## Verify Deployment

1. Flux controllers:
```bash
kubectl -n flux-system get pods
```

2. Helm objects:
```bash
kubectl -n flux-system get helmrepositories,helmreleases
kubectl -n flux-system describe helmrelease ww-gitops
```

3. UI pods/services:
```bash
kubectl -n flux-system get pods,svc | grep -i gitops || true
kubectl -n flux-system get ingressroute flux-ui
```

## Login

Default user is `admin`.

Password is not stored in Git in plaintext. A bcrypt hash is stored in the HelmRelease values.

If you generated the dashboard with the `gitops` CLI on the server, the one-time password was stored locally (server-only).

## Rotate Admin Password

1. Generate a new bcrypt hash:
```bash
gitops get bcrypt-hash
```

2. Update `clusters/production/weave-gitops-dashboard.yaml`:
- `spec.values.adminUser.passwordHash: <new-hash>`

3. Commit + push; Flux will reconcile and update the release.

