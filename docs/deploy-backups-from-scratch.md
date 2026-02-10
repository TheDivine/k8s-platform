# Deploy Backups From Scratch (MinIO + Velero)

This runbook is written for running commands **from the cluster admin machine** (the server where `kubectl` already works).

Goal:
- Deploy **MinIO** inside the cluster to provide S3-compatible storage.
- Install **Velero** to back up Kubernetes objects (and optionally PVC data later).

Important concepts:
- **Manifests in Git** describe *desired state*, but they do not apply themselves until GitOps is configured to reconcile that folder.
- **Secrets** should not be stored in plaintext in Git. Use templates in Git, apply real credentials manually (or use SOPS/External Secrets).

## Prerequisites

1. Cluster access works on this machine:
```bash
kubectl get nodes -o wide
```

2. Traefik is running and has a working `certResolver` called `le` (your cluster uses `le`).

3. Longhorn is installed (we use `storageClassName: longhorn` for the MinIO PVC).

## Step 1: Deploy MinIO (in-cluster S3)

Why:
- Velero needs an object store to upload backup files.
- MinIO gives you an S3 endpoint inside the cluster (works well for homelabs).

### 1. Create the `backup` namespace
This is included in Kustomize, but it is safe to apply directly:
```bash
kubectl apply -f platform/backup/minio/namespace.yaml
```

### 2. Create MinIO credentials secret
You have a template at `platform/backup/minio/secret.template.yaml`.

Edit it and replace `CHANGE_ME`, then apply:
```bash
kubectl apply -f platform/backup/minio/secret.template.yaml
```

What this does:
- Stores `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` as a Kubernetes Secret.
- The MinIO Deployment reads it via `envFrom`.

### 3. Deploy MinIO resources
```bash
kubectl apply -k platform/backup/minio/
```

### 4. Verify MinIO
```bash
kubectl -n backup get pods
kubectl -n backup get svc
kubectl -n backup get pvc
kubectl -n backup get ingressroute
```

If you are using the provided IngressRoute, the console should be:
- `https://minio.kwiki.it.com`

## Step 2: Create the `velero` bucket in MinIO

Why:
- Velero uploads backups to a specific bucket. The config in this repo expects `bucket: velero`.

How:
1. Log into the MinIO console.
2. Create a bucket named `velero`.

## Step 3: Install Velero (CRDs + server)

Why:
- The YAML in `platform/backup/velero/` contains Velero custom resources (BackupStorageLocation, Schedule, etc.).
- Those custom resources will fail unless Velero CRDs and controllers are installed first.

### 1. Install the Velero CLI on this machine
Pick one approach:

1. If you already have a preferred method/package manager, use it.
2. Otherwise, install from the Velero release tarball (recommended for servers).

After installation, confirm:
```bash
velero version
```

### 2. Create a credentials file (local only)
Create a file like `./credentials-velero` on this machine (do not commit it):
```ini
[default]
aws_access_key_id=<MINIO_ROOT_USER>
aws_secret_access_key=<MINIO_ROOT_PASSWORD>
```

### 3. Install Velero into the cluster
This installs:
- `velero` namespace
- Velero CRDs
- Velero deployment + services
- A secret containing credentials

Command (MinIO S3 endpoint inside the cluster):
```bash
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.9.2 \
  --bucket velero \
  --secret-file ./credentials-velero \
  --backup-location-config region=us-east-1,s3ForcePathStyle=true,s3Url=http://minio.backup.svc.cluster.local:9000 \
  --use-volume-snapshots=false
```

Verify:
```bash
kubectl -n velero get pods
kubectl get crd | grep velero.io
```

## Step 4: Apply Velero configuration from this repo (locations + schedules)

Why:
- This repo defines your backup policies as code (where backups go, schedules, retention).

Apply:
```bash
kubectl apply -k platform/backup/velero/
```

Verify:
```bash
kubectl -n velero get backupstoragelocation
kubectl -n velero get schedules
```

## Step 5: Run a test backup

```bash
velero backup create smoke-test --include-namespaces default
velero backup describe smoke-test
velero backup logs smoke-test
```

## GitOps Note (Why ArgoCD did not deploy MinIO automatically)

Your ArgoCD `platform` Application points at `path: platform` and treats it as a plain directory.
ArgoCD does not automatically recurse into subfolders unless configured to do so.

Recommended approach:
- Keep the `platform` app as-is.
- Add a separate ArgoCD Application specifically for `platform/backup/minio` (and later Velero) when you want GitOps to manage it.

