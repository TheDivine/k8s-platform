# Infra Security Baseline

This directory contains public-safe scaffolding for Linux and Kubernetes node security automation. It is designed for future Ansible, systemd, and local validation workflows, but none of these files are applied automatically.

Scope:

- SSH, firewall, auditd, fail2ban, ClamAV, Maldet, and Wazuh agent baselines.
- Container runtime and Kubernetes node validation helpers.
- Safe malware scan path examples.
- SOPs and checklists for future operations.

Rules:

- Do not store real inventories, credentials, Wazuh enrollment secrets, webhooks, kubeconfigs, or host-specific private values here.
- Treat inventory and host vars as examples only.
- Run scripts manually and review their output before turning them into scheduled jobs.
- Test Ansible in check mode before applying to nodes.

## Suggested Manual Validation

```bash
./infra-security/scripts/check-node-health.sh
./infra-security/scripts/check-container-runtime.sh
./infra-security/scripts/collect-security-status.sh
./infra-security/scripts/collect-k8s-node-status.sh
```

