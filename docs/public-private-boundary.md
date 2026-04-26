# Public And Private Boundary

This repository is public-safe by design. It may show structure, patterns, templates, and examples, but it must not expose private infrastructure state.

## Public-Safe Files

Allowed:

- architecture and runbook Markdown
- sanitized Kubernetes manifests
- placeholder-only examples
- `*.example.yaml`
- `*.template.yaml`
- public-safe Kustomize and Helm examples
- diagrams using `example.com`, `example.local`, or generic names
- non-destructive validation scripts

## Private-Only Files

Do not commit:

- real secrets, passwords, OAuth credentials, API tokens, webhook secrets, or registry auth
- kubeconfigs or admin certificates
- private SSH keys, TLS keys, `*.pem`, `*.key`, `*.p12`, or `*.pfx`
- `.env` files
- Terraform state, real `*.tfvars`, backend credentials, or provider credentials
- Ansible vault files, vault passwords, private inventories, or host-specific secret variables
- Wazuh enrollment credentials
- generated cluster exports
- logs, uploads, database dumps, backup archives, or customer data

## Examples And Templates Policy

Examples must use obvious placeholders:

- `CHANGE_ME`
- `example.com`
- `example.local`
- `k8s-node-01.example.com`
- `REPLACE_WITH_PRIVATE_VALUE`

If an example would require real upstream details that are not validated, add a TODO instead of guessing.

## Secrets Policy

Real secrets should be managed through one of:

- SOPS
- SealedSecrets
- ExternalSecrets
- manual `kubectl create secret` outside Git

Do not commit unencrypted Kubernetes `Secret` manifests with real values. Historical committed secrets should be treated as exposed.

## Generated Exports Policy

Generated exports such as `platform/exports/` and `platform/exports-clean/` must remain ignored and untracked. They can expose service names, labels, annotations, topology, and operational state.

## Nested Repositories Policy

Nested app repositories under `apps/` are local/private by default and ignored by `.gitignore`. To make an app public, create a clean deployment surface with docs, examples, and sanitized manifests instead of committing the raw nested repo.
