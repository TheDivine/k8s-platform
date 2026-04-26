# IaC Strategy

This repository documents how Infrastructure as Code fits into the platform without publishing private provisioning data.

## Terraform

Real Terraform should live in a private repository because it normally contains provider configuration, backend configuration, state references, DNS zones, firewall details, and environment-specific values.

This public repository may contain only:

- non-sensitive examples
- module interface documentation
- diagrams
- migration plans
- placeholder-only examples

Terraform should manage:

- virtual machines
- DNS records and zones
- object storage and backup buckets
- cloud resources
- firewall or provider resources where applicable

## Ansible

Real Ansible automation should live in a private infra-security repository because it needs inventories, host variables, SSH details, Wazuh enrollment settings, and environment-specific hardening decisions.

Ansible should manage:

- node hardening
- package installation
- SSH hardening
- auditd
- ClamAV
- Maldet on web/upload/file nodes
- Wazuh agent
- Fail2ban
- Kubernetes node prerequisites
- containerd and `crictl` configuration

## GitOps

GitOps should manage Kubernetes desired state:

- application workloads
- platform services
- ingress routes
- monitoring
- backup controllers
- policy controllers
- namespace-level configuration

Argo CD and Flux can both be represented in this repo, but production usage should define clear ownership boundaries so they do not reconcile the same resources.

## Manual And Bootstrap Work

Manual/bootstrap procedures should be reduced and documented. They are still appropriate for:

- first cluster initialization
- first GitOps controller installation
- break-glass operations
- one-time emergency recovery
- secret bootstrap
- hardware, BIOS, or firmware work

Every manual action should have a runbook, expected output, and rollback note before it becomes part of repeatable operations.
