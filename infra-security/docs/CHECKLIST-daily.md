# Daily Security Checklist

- [ ] Review failed SSH logins and unexpected privileged logins.
- [ ] Check `auditd`, `fail2ban`, Wazuh agent, containerd, and kubelet health.
- [ ] Review monitoring alerts and unresolved log alerts.
- [ ] Confirm recent backups completed.
- [ ] Review new critical image or OS vulnerability alerts.
- [ ] Check disk pressure on Kubernetes and storage nodes.
- [ ] Review suspicious files found by scheduled scanners.

Suggested command:

```bash
infra-security/scripts/collect-security-status.sh
```
