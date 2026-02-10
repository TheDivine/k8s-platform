# ArgoCD Applications: Beginner Workflow

This guide explains **what ArgoCD Applications are**, **why they exist**, and **how the workflow works** step by step.

## Why ArgoCD Exists
Kubernetes is powerful, but manual `kubectl apply` quickly becomes risky:
- People apply different versions of YAML.
- Changes are not tracked.
- Clusters drift from what you intended.

ArgoCD solves this by making **Git the source of truth** and continuously syncing the cluster to it.

## Core Idea (Simple Model)
1. **Git = truth**
2. **Application = map to truth**
3. **ArgoCD = enforcer**
4. **Cluster = follows Git**

---

## Step-by-Step Workflow

### 1) Put Manifests in Git
**Why:** Git provides history, review, and repeatability.

**How:** Organize YAML into clear folders, e.g.:
- `platform/` (Traefik, monitoring, admin tools)
- `infra/` (storage, networking basics)

---

### 2) Install ArgoCD in the Cluster
**Why:** ArgoCD runs inside the cluster so it can continuously reconcile Git.

**How:**
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

---

### 3) Create ArgoCD Applications
**Why:** ArgoCD does not guess what to deploy. An **Application** tells it:
- Which repo to watch
- Which folder to deploy
- Which cluster/namespace to target

Example (platform folder):
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: platform
  namespace: argocd
spec:
  source:
    repoURL: https://github.com/TheDivine/k8s-platform.git
    targetRevision: main
    path: platform
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
```

---

### 4) Apply the Applications
**Why:** This registers what ArgoCD should manage.

**How:**
```bash
kubectl apply -f clusters/production/argocd-app-platform.yaml
kubectl apply -f clusters/production/argocd-app-infra.yaml
```

---

### 5) ArgoCD Syncs Git to Cluster
ArgoCD will:
1. Pull Git
2. Compare YAML with the current cluster
3. Apply changes so they match

If you enable:
- **prune** → deletes resources removed from Git
- **selfHeal** → fixes manual changes/drift

---

## Why We Split Applications
We created two separate Applications:
- **platform** → shared cluster services
- **infra** → storage + networking basics

This makes changes safer and easier to reason about.

---

## Summary (Beginner Friendly)
- ArgoCD makes sure your cluster always matches Git.
- Applications are the “map” from Git folders to the cluster.
- Once set, you only change Git, and ArgoCD does the rest.
