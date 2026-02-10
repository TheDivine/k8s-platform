# Backup and Reproducibility Plan

This guide explains how to **capture the current cluster state**, keep it in Git, and back up runtime data so you can rebuild the cluster when needed.

## 1) Desired State vs Runtime State

### Desired State (in Git)
- Kubernetes manifests (Deployments, Services, IngressRoutes, RBAC, etc.)
- This is what ArgoCD/Flux reconciles

### Runtime State (data)
- Databases, PVCs, object storage
- Needs separate backup tooling (Velero/MinIO)

You need **both** to fully recover a cluster.

---

## 2) Export What’s Already Running
We exported all namespaces into:
```
platform/exports/
```

### What’s included
- Deployments, Services, Ingress, IngressRoute, RBAC, ConfigMaps, PVCs, etc.
- Cluster-scoped objects: CRDs, ClusterRoles, StorageClasses

### What’s excluded
- Secrets (by design)

### Why exclude Secrets
- Secrets often include credentials and tokens
- Safer to manage them separately (External Secrets, SOPS, Vault)

---

## 3) How to Manage Secrets Safely
Recommended approaches:

### Option A: External Secrets Operator
- Store secrets in a secure backend (e.g., AWS/GCP/HashiCorp/1Password)
- K8s pulls them at runtime

### Option B: SOPS + Git
- Encrypt secrets in Git using age or GPG
- Decrypt only at deploy time

If you want, we can add External Secrets or SOPS next.

---

## 4) Cleaning Exported YAML (Important)
Exported YAML includes runtime fields like:
- `status`
- `metadata.creationTimestamp`
- `metadata.resourceVersion`
- `metadata.uid`

These should be removed before using them as clean GitOps sources.

### Recommended cleanup tool
Use `kubectl-neat` (or `kubeconform` + `yq`) to strip runtime fields.
If you want, I can install and run it across `platform/exports/`.

---

## 5) Backing Up Runtime Data

### Velero (recommended)
- Backs up resources + PVC snapshots
- Works with object storage (MinIO is perfect)

### MinIO (local S3)
- Provides an S3 API endpoint for backups
- Works well for homelabs

If you want, I can prepare manifests for:
- MinIO
- Velero
- Scheduled backups

---

## 6) Recovery Playbook
1. Install Kubernetes
2. Install ArgoCD + Flux
3. Apply GitOps manifests
4. Restore Velero backups
5. Verify services

---

## 7) Current Export Location
```
platform/exports/
```

This is a snapshot of the cluster state as of export time. Use it as a migration guide, not as production GitOps source until cleaned.
