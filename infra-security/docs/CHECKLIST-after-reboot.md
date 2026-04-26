# Checklist: After Reboot

- [ ] Host responds over SSH.
- [ ] Time sync is healthy.
- [ ] Disk mounts are present.
- [ ] `containerd` is active where expected.
- [ ] `kubelet` is active where expected.
- [ ] `auditd` is active.
- [ ] `fail2ban` is active where configured.
- [ ] Wazuh agent is active where configured.
- [ ] No unexpected swap is active on Kubernetes nodes.
- [ ] Monitoring and log forwarding have resumed.

Suggested commands:

```bash
infra-security/scripts/check-node-health.sh
infra-security/scripts/collect-k8s-node-status.sh
infra-security/scripts/collect-security-status.sh
```
