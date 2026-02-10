# Backup Setup: MinIO + Velero

This is a beginner-friendly, step-by-step guide to set up backups using **MinIO (S3-compatible)** and **Velero**.

For a full “from scratch on the server” runbook, see `docs/deploy-backups-from-scratch.md`.

## Step 1: Deploy MinIO
MinIO provides S3 storage for Velero backups.

1. Create secret (change credentials):
```bash
kubectl apply -f platform/backup/minio/secret.template.yaml
```

2. Apply MinIO stack:
```bash
kubectl apply -k platform/backup/minio/
```

3. Confirm pods:
```bash
kubectl -n backup get pods
```

4. Access console:
```
https://minio.kwiki.it.com
```

---

## Step 2: Install Velero
Velero needs its CRDs and server components.

1. Install Velero CLI on your admin machine.
2. Create a credentials file (local only):
```
[default]
aws_access_key_id=<minio-user>
aws_secret_access_key=<minio-password>
```

3. Install Velero server:
```bash
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.9.2 \
  --bucket velero \
  --secret-file ./credentials-velero \
  --backup-location-config region=us-east-1,s3ForcePathStyle=true,s3Url=http://minio.backup.svc.cluster.local:9000 \
  --use-volume-snapshots=false
```

---

## Step 3: Apply Velero Configs
These are in your repo:
```bash
kubectl apply -k platform/backup/velero/
```

---

## Step 4: Validate
```bash
kubectl -n velero get pods
kubectl -n velero get backupstoragelocation
kubectl -n velero get schedules
```

---

## Notes
- If you use CSI snapshots, enable snapshot support later.
- Keep secrets out of Git. Use templates only.
