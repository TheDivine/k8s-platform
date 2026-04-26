# Weekly Security Checklist

- [ ] Run or review ClamAV scans for selected safe paths.
- [ ] Run Maldet only on web/upload/file nodes where enabled.
- [ ] Review users, sudoers, SSH keys, and service accounts.
- [ ] Review Kubernetes RBAC changes and cluster-admin usage.
- [ ] Review NetworkPolicy coverage for platform and app namespaces.
- [ ] Review Trivy or equivalent image and manifest scan results.
- [ ] Validate restore procedures for one backup class.
- [ ] Check for stale generated exports, archives, and secret-like files before public pushes.
