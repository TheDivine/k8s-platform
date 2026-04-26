# Checklist: Before Adding A Node

- [ ] Node role and owner are documented.
- [ ] OS version is approved.
- [ ] Hostname and DNS are correct.
- [ ] SSH uses keys and named users.
- [ ] Firewall rules are documented.
- [ ] Time sync is active.
- [ ] Disk layout is appropriate for node role.
- [ ] Container runtime is installed when needed.
- [ ] `crictl` endpoint is configured when needed.
- [ ] Security agent plan is documented: auditd, fail2ban, Wazuh, ClamAV, optional Maldet.
- [ ] Backup impact and monitoring labels are planned.

TODO: Add environment-specific node acceptance criteria outside public Git.
