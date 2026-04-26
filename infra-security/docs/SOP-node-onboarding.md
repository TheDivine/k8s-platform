# SOP: Node Onboarding

This SOP keeps new Linux or Kubernetes nodes consistent before they join production-style workloads.

## Prechecks

1. Confirm the node purpose: Kubernetes worker, control-plane, Docker host, file/upload node, or management host.
2. Confirm the OS version is supported by the baseline.
3. Confirm SSH access uses named users and keys, not shared passwords.
4. Confirm the node has a documented owner, role, and recovery path.

## Safe Validation

Run local checks before applying any automation:

```bash
infra-security/scripts/check-node-health.sh
infra-security/scripts/check-container-runtime.sh
infra-security/scripts/collect-security-status.sh
```

For Kubernetes nodes:

```bash
infra-security/scripts/collect-k8s-node-status.sh
```

## Configuration Ownership

- Ansible should manage OS packages, SSH, firewall, auditd, fail2ban, ClamAV, optional Maldet, Wazuh agent, and container runtime checks.
- GitOps should manage Kubernetes workloads after the node is part of the cluster.
- Terraform should manage external infrastructure resources such as DNS, object storage, firewall objects, and provider resources where applicable.

## TODO

- TODO: Decide supported OS families and versions.
- TODO: Define a required node labeling and tainting standard.
- TODO: Document the manual approval step before any new node joins a cluster.
