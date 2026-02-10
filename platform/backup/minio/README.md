# MinIO (Backup Storage)

This folder deploys a minimal MinIO instance for Velero backups.

## Files
- `namespace.yaml`: creates `backup`
- `pvc.yaml`: 50Gi storage (uses `longhorn`)
- `deployment.yaml`: MinIO server
- `service.yaml`: ClusterIP for S3 + console
- `ingressroute.yaml`: exposes console at `minio.kwiki.it.com`
- `secret.template.yaml`: credentials template (do NOT commit real secrets)

## Setup
1. Create secret from template:
```bash
kubectl apply -f platform/backup/minio/secret.template.yaml
```
2. Apply MinIO stack:
```bash
kubectl apply -k platform/backup/minio/
```

## Notes
- Change `storageClassName` if you don’t use Longhorn.
- Replace `minio.kwiki.it.com` with your chosen domain.
