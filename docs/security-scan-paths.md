# Security Scan Paths

This guide defines safe scan boundaries for ClamAV and Maldet in a Kubernetes home-lab environment. It is documentation only. Validate paths on each node before scheduling scans.

## Safe ClamAV Scan Paths

Candidate paths:

- `/home`
- `/srv`
- `/opt`
- `/var/www`
- `/var/backups`
- documented upload directories
- mounted shared storage intended for user files
- application content directories outside container runtime storage

Use lower priority and IO limits for large scans.

## Safe ClamAV Excluded Paths

Exclude by default:

- `/proc`
- `/sys`
- `/dev`
- `/run`
- `/var/lib/containerd`
- `/var/lib/docker`
- `/var/lib/kubelet`
- `/var/lib/longhorn`
- `/var/lib/etcd`
- database data directories unless scheduled in maintenance windows
- active backup repository internals unless vendor guidance allows scanning

## Safe Maldet Scan Paths

Maldet is most useful on web, upload, and file-ingest nodes. Candidate paths:

- `/var/www`
- application upload directories
- public file share roots
- CMS content directories
- reverse-proxy-served static content directories

Do not deploy Maldet as a blanket scanner for every Kubernetes node without a clear use case.

## Safe Maldet Excluded Paths

Exclude by default:

- container runtime directories
- Kubernetes kubelet directories
- Longhorn engine and replica directories
- etcd data
- database data
- large immutable backup stores
- application dependency caches such as `node_modules`

## Kubernetes Node Notes

- Do not scan pseudo filesystems.
- Avoid scanning container overlay layers while containers are running.
- Avoid scanning kubelet pod volume internals unless the workload and volume type are understood.
- Prefer scanning ingress/upload PVCs through mounted maintenance jobs or storage-level workflows.

## Docker And Containerd Node Notes

- Avoid direct scanning of `/var/lib/docker` and `/var/lib/containerd`.
- Scan images with Trivy instead of antivirus scanning runtime layers.
- Scan bind-mounted host upload paths separately when they exist.

## Longhorn Volume Notes

- Do not scan Longhorn engine or replica internals directly.
- Scan mounted filesystem paths from a controlled pod or maintenance node.
- Coordinate scans with backup windows and replica health checks.
- Watch IO and latency during any scan of large PVC-backed data.

## NFS And Shared Storage Notes

- Scan NFS shares from one controlled scanner host to avoid duplicate load.
- Exclude snapshot directories if present.
- Coordinate scan schedules with backup jobs.
- Document ownership and remediation process for files found on shared storage.

## Web Upload Directory Notes

- Treat upload directories as high-priority scan targets.
- Use extension allowlists and application-level validation.
- Keep uploads outside executable web roots when possible.
- Alert on executable content, archives, scripts, and suspicious renamed files.

## Recommended Scan Schedule

- Daily lightweight scan of upload and web content paths.
- Weekly broader scan of user file paths and shared storage.
- Monthly full review of exclusions and scan logs.
- On-demand scan after suspicious upload, incident, or restored backup.

## Manual Review TODOs

- TODO: identify actual upload paths for `apps/kwiki` if it becomes a public app.
- TODO: identify any NFS mount paths used by the cluster.
- TODO: identify Longhorn-backed PVCs that contain user-uploaded content.
- TODO: define resource limits for scan jobs.
- TODO: decide whether scan results feed into monitoring or ticketing.
