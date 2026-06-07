# Security Baseline

This baseline describes the recommended host and Kubernetes security posture for projects derived from this repository. It is documentation and example scaffolding, not an instruction to apply changes to live systems without review.

## Host Security

### SSH Hardening

- Disable root SSH login.
- Prefer key-based authentication.
- Disable password authentication where operationally possible.
- Restrict SSH exposure through VPN, firewall allowlists, or bastion access.
- Keep private keys and authorized key ownership outside public Git.

### Firewall

- Default deny inbound traffic.
- Permit only documented management, Kubernetes, ingress, storage, and monitoring paths.
- Keep provider firewall objects in Terraform and host firewall rules in Ansible.
- Document all public ingress exposure.

### auditd

- Enable `auditd` on Linux nodes.
- Monitor authentication, sudo, privilege escalation, key system files, and container runtime configuration.
- Ship audit logs to a central logging or SIEM destination.

### Fail2ban

- Use Fail2ban for SSH and exposed authentication endpoints where appropriate.
- Maintain explicit allowlists for admin networks.
- Avoid banning Kubernetes node-to-node or service traffic.

### ClamAV

- Use ClamAV where nodes store or process files, uploads, backups, or shared content.
- Schedule scans with resource limits.
- Avoid scanning volatile Kubernetes and container runtime internals.

### Maldet

- Use Maldet only on upload, web, CMS, or file-ingest nodes where it is operationally justified.
- Do not blanket-scan every Kubernetes node with Maldet.
- Review findings manually before deletion or quarantine escalation.

### Wazuh Agent

- Use Wazuh agents for host security telemetry where a Wazuh manager exists.
- Keep manager endpoints, enrollment secrets, and auth material outside public Git.
- Correlate Wazuh events with audit logs, SSH logs, runtime logs, and Kubernetes events.

## Kubernetes Security

### Trivy

- Scan container images before promotion.
- Scan Kubernetes manifests and IaC for misconfigurations.
- Run repository secret and misconfiguration scans before public commits.

### Kyverno

- Start policies in audit mode.
- Cover privileged pods, hostPath, host networking, missing resource requests/limits, disallowed `latest` tags, and required labels.
- Move to enforce mode only after exceptions are documented.

### Falco

- Use Falco or equivalent runtime detection after baseline workloads are stable.
- Tune rules for expected privileged components such as CNI, storage, ingress, and backup controllers.

### Secrets Management

Use one of the following for real secrets:

- SOPS
- SealedSecrets
- ExternalSecrets
- Manual secret creation outside Git

Never commit real Kubernetes `Secret` manifests, OAuth secrets, database passwords, registry credentials, kubeconfigs, or private keys.

### Backup And Restore

- Use Velero or equivalent for Kubernetes resource backup where appropriate.
- Use S3-compatible object storage such as MinIO for lab backup targets.
- Keep backup credentials, bucket secrets, and real endpoints outside public Git.
- Test restore procedures before considering backup coverage complete.

### Logging And Monitoring

- Use Prometheus and Alertmanager for metrics and alerting.
- Use Loki with Promtail or Fluent Bit for log aggregation.
- Route security-relevant host logs from auditd, scanners, runtime services, and authentication into a central review path.
- Keep dashboards public-safe by avoiding private hostnames, customer data, or credentials.

## Safe Scan Paths

Recommended include paths:

- `/home`
- `/root`
- `/tmp`
- `/var/tmp`
- `/dev/shm`
- `/opt`
- `/usr/local/bin`
- `/etc`
- `/var/www`
- `/srv`

Recommended exclude paths:

- `/proc`
- `/sys`
- `/dev`
- `/run`
- `/var/lib/kubelet/pods`
- `/var/lib/containerd`
- `/var/lib/docker`
- `/var/lib/longhorn`

## Operational Notes

- Scan images with Trivy rather than antivirus scanning container runtime layers.
- Do not directly scan Longhorn engine or replica internals.
- Scan mounted application upload paths from a controlled scanner host or maintenance workflow.
- Preserve scanner logs and incident evidence before remediation.
