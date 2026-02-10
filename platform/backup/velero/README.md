# Velero (Cluster Backups)

This folder contains the **Velero backup configuration** (BackupStorageLocation, VolumeSnapshotLocation, Schedule). It assumes MinIO is running in the `backup` namespace.

## Important
Velero server and CRDs must be installed before applying these files.

## Install Velero Server (CLI)
Use the Velero CLI on your admin machine:
```bash
velero install \
  --provider aws \
  --plugins velero/velero-plugin-for-aws:v1.9.2 \
  --bucket velero \
  --secret-file ./credentials-velero \
  --backup-location-config region=us-east-1,s3ForcePathStyle=true,s3Url=http://minio.backup.svc.cluster.local:9000 \
  --use-volume-snapshots=false
```

## Apply Configs
```bash
kubectl apply -k platform/backup/velero/
```

## Notes
- Replace the secret with real credentials (do not commit them).
- Update the bucket name if you use something other than `velero`.
