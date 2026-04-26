# ClamAV Baseline

ClamAV is recommended for file-processing, upload, shared storage, backup staging, and web-content paths.

Avoid direct scans of:

- `/proc`
- `/sys`
- `/dev`
- `/run`
- `/var/lib/kubelet`
- `/var/lib/containerd`
- `/var/lib/docker`
- `/var/lib/longhorn`
- `/var/lib/etcd`

Use Trivy for container images and IaC instead of scanning container runtime internals.

