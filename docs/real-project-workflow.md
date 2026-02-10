# Real Project Workflow (ArgoCD + Flux + Drone CI)

This guide explains how to use:
- **ArgoCD** for platform and infra (this repo)
- **Flux + Weave GitOps** for apps (separate repos)
- **Drone CI** to build/test/push images and trigger GitOps deploys

## 0) The Big Picture (Why the split)

Keep ownership clear to avoid tools fighting each other:
- ArgoCD manages `platform/` and `infra/` (cluster services and foundations).
- Flux manages application repos (your portfolio apps, blog, APIs).
- Drone CI builds artifacts (container images) and updates Git (or publishes immutable tags).

Rule:
- A Kubernetes resource should be managed by **one** controller (ArgoCD or Flux), not both.

## 1) What you change day to day

Platform changes (rare):
- Update files in this repo under `platform/` or `infra/`
- Commit and push
- ArgoCD applies them

App changes (often):
- Update app code in app repo
- Drone CI builds and pushes an image
- Flux applies new manifests (or updated image tag) to the cluster

## 2) Start a new “real project” (example: `cyberlynx-api`)

### Step A: Create an app repo
Create a new GitHub repo for the app, for example:
- `TheDivine/cyberlynx-api`

Recommended structure:
```
cyberlynx-api/
  Dockerfile
  k8s/
    namespace.yaml
    deployment.yaml
    service.yaml
    ingressroute.yaml
    kustomization.yaml
  .drone.yml
  README.md
```

### Step B: Build and push container images (Drone CI)
Drone should:
1. Run tests/lint
2. Build the Docker image
3. Push image with an immutable tag (commit SHA or semver)

Two common tagging strategies:
- `:sha-<gitsha>` (simple, always unique)
- `:vX.Y.Z` (release driven)

### Step C: GitOps deploy (Flux)
Flux needs two things for each app:
1. `GitRepository` pointing at the app repo
2. `Kustomization` pointing at `./k8s` (or your chosen path)

You can store those Flux objects in this repo under `clusters/production/`
OR store them in a dedicated “apps” folder and include it from `clusters/production/kustomization.yaml`.

## 3) The “Deploy” loop (how it actually happens)

1. You merge code to `main` in the app repo.
2. Drone CI builds and pushes image `registry/app:sha-...`.
3. Drone CI updates `k8s/deployment.yaml` image tag in Git (commit) OR you use Flux Image Automation later.
4. Flux reconciles Git and applies the new Deployment.
5. Weave GitOps UI shows reconciliation status.

## 4) How to check what is working

ArgoCD:
- UI: `https://argo.kwiki.it.com`
- Cluster check:
```bash
kubectl -n argocd get applications
```

Flux:
- UI: `https://flux.kwiki.it.com`
- Cluster checks:
```bash
kubectl -n flux-system get pods
kubectl -n flux-system get gitrepositories,kustomizations
kubectl -n flux-system get helmreleases,helmrepositories
```

Drone CI:
- UI: `https://drone.kwiki.it.com`
- Runner must exist for pipelines to run.

## 5) Secrets (beginner-safe rule)

Do not commit plaintext secrets into Git.
Use one of:
- Kubernetes Secrets applied manually
- SOPS (encrypted secrets in Git)
- External Secrets Operator (recommended long term)

## 6) Next improvement (optional)

After your first app works end-to-end, add Flux Image Automation so Drone does not need to commit image tag changes.

