# SOP: Security Incident

This SOP is a public-safe starting point for host and Kubernetes node security events.

## Immediate Actions

1. Preserve evidence before changing the host.
2. Record hostname, IPs, user sessions, running services, and recent logs.
3. Do not delete suspicious files until reviewed.
4. If containment is needed, prefer network isolation over ad hoc file deletion.

## Local Collection

```bash
infra-security/scripts/check-node-health.sh
infra-security/scripts/collect-security-status.sh
infra-security/scripts/collect-k8s-node-status.sh
```

## Evidence Sources

- `auditd` logs.
- SSH and auth logs.
- Wazuh agent events.
- ClamAV and Maldet scan logs.
- Container runtime logs.
- Kubernetes node service logs.
- Application logs routed through Loki or another log backend.

## Follow-Up

- Identify root cause and blast radius.
- Rotate credentials only after containment and with a documented plan.
- Restore from known-good backups when integrity is uncertain.
- Create a post-incident task list for hardening gaps.

TODO: Define incident severity levels and notification contacts outside public Git.
