# Ansible Private Repo Plan

Real node hardening and host security automation should live in a separate private infra-security repository. This public repo can document the pattern and hold safe examples, but real inventory, host variables, enrollment secrets, and operational logs must stay private.

## Boundary

Do not commit the following to the public repo:

- real inventories
- private host variables
- Ansible vault files or vault passwords
- SSH private keys
- Wazuh enrollment credentials
- private scan logs
- environment-specific firewall allowlists

## Suggested Private Repo Structure

```text
inventory/
ansible/
  playbooks/
  roles/
scripts/
systemd/
docs/
```

## First Recommended Playbooks

- `baseline-hardening.yml`
- `node-validation.yml`
- `malware-scanners.yml`
- `auditd.yml`
- `fail2ban.yml`
- `wazuh-agent.yml`

## Suggested Workflow

1. Keep inventory and host variables private.
2. Use Ansible check mode before changing nodes.
3. Roll out to staging or one node at a time.
4. Document rollback steps for every role.
5. Keep Wazuh enrollment, SSH keys, and secret variables in a private secret manager or Ansible Vault.
6. Export sanitized role structure and SOPs back to this public repo only when useful.

TODO: Decide whether the public `infra-security/` scaffold remains here long term or becomes a separate public example extracted from the private automation repo.
