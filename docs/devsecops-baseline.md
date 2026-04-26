# DevSecOps Baseline

This baseline defines the professional security posture expected for future repositories and projects built from this home-lab platform. It is intentionally generic and should be implemented through Ansible, GitOps, Terraform, and documented manual bootstrap steps over time.

## Linux Node Hardening

- Use supported OS releases with unattended security updates where appropriate.
- Disable unused services and packages.
- Enforce time synchronization.
- Configure least-privilege sudo.
- Set kernel and sysctl hardening after Kubernetes compatibility review.
- Use separate users for human administration and automation.
- Keep node baseline changes in Ansible and test with check mode first.

## SSH Hardening

- Disable root SSH login.
- Disable password authentication where key-based access is available.
- Use modern ciphers and MACs.
- Set idle timeout and connection limits.
- Restrict SSH by firewall or VPN where possible.
- Use separate deploy/admin keys and rotate through documented process outside Git.

## Firewall Baseline

- Default deny inbound.
- Allow only documented Kubernetes, SSH, ingress, storage, and monitoring paths.
- Restrict management ports to admin networks or VPN.
- Document any MetalLB address pools and exposed services.
- Keep host firewall rules in Ansible and cloud/provider firewalls in Terraform.

## `auditd` Baseline

- Enable `auditd` on Linux nodes.
- Monitor authentication, sudo, privilege changes, key system paths, and container runtime config.
- Ship audit logs to centralized logging where available.
- Tune rules to avoid excessive noise before enforcing alerting.

## `fail2ban` Recommendation

- Use `fail2ban` for SSH and exposed authentication endpoints where applicable.
- Keep jail config in Ansible.
- Avoid banning Kubernetes node-to-node traffic.
- Document allowlists for admin networks.

## ClamAV Recommendation

- Use ClamAV on nodes that store or process files, backups, uploads, or shared content.
- Prefer scheduled scans with resource limits.
- Exclude Kubernetes runtime paths, container storage, Longhorn engine directories, and pseudo filesystems.
- See `docs/security-scan-paths.md` for scan path guidance.

## Maldet Recommendation

- Use Linux Malware Detect only on web, upload, or file-ingest nodes.
- Do not blanket-scan all Kubernetes nodes by default.
- Avoid scanning container runtime overlays, Longhorn internals, and database volumes without maintenance windows.

## Trivy Recommendation

- Use Trivy for:
  - container image scanning
  - Kubernetes manifest misconfiguration scanning
  - repository filesystem secret/misconfiguration scanning
  - IaC scanning once Terraform is introduced
- Run locally before public commits and later in CI.

## Falco Recommendation

- Deploy Falco or an equivalent runtime detection tool after baseline workloads are stable.
- Start in alerting mode.
- Tune noisy rules for Kubernetes nodes, storage components, and backup jobs.
- Document expected privileged workloads such as CNI, storage, and ingress controllers.

## Kyverno Recommendation

- Introduce Kyverno policies in audit mode first.
- Baseline policies should cover:
  - privileged pods
  - hostPath usage
  - host networking and host PID/IPC
  - required resource requests/limits
  - image registry allowlists
  - disallowed latest tags
  - required labels
  - secret mounting patterns
- Move policies from audit to enforce only after exceptions are documented.

## Kubernetes Admission And Security Policy Baseline

- Use Pod Security Admission labels by namespace.
- Require least-privilege service accounts.
- Review ClusterRole and ClusterRoleBinding use.
- Prefer NetworkPolicies for app and platform namespace isolation.
- Require explicit ingress exposure.
- Keep admin UIs behind VPN, IP allowlist, or additional authentication.

## Container Image Scanning Baseline

- Scan images before promotion.
- Pin versions where possible.
- Track upstream image provenance.
- Avoid private registry credentials in Git.
- Document image exception and risk acceptance process.

## Secrets Management Baseline

- Never commit real Kubernetes Secret values.
- Acceptable public files:
  - `*.example.yaml`
  - `*.template.yaml`
  - encrypted SOPS files without private keys
  - SealedSecrets when controller key management is understood
  - ExternalSecrets references without provider credentials
- Bootstrap secrets manually or through a private secret manager.
- Treat historical committed secrets as exposed.

## Backup And Restore Baseline

- Use Velero for Kubernetes resource and volume backups where appropriate.
- Use MinIO or S3-compatible storage with private credentials.
- Test restore procedures regularly.
- Document RPO/RTO targets.
- Keep backup payloads and credentials out of public Git.
- Include database-specific backups for stateful applications.

## Logging And Monitoring Baseline

- Use Prometheus/Grafana or equivalent for metrics.
- Collect Kubernetes events and application logs.
- Alert on:
  - node pressure
  - PV/PVC issues
  - ingress/TLS failures
  - backup failures
  - crash loops
  - high privilege changes
- Keep dashboards and alert rules sanitized before public release.
