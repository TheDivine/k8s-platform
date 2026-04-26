# Secret Management

This repository must never contain real secrets. It can document secret patterns and include placeholder-only examples.

## Never Commit

- real Kubernetes `Secret` manifests
- database passwords
- OAuth client secrets
- API tokens
- webhook secrets
- registry credentials
- kubeconfigs
- private keys
- `.env` files
- Ansible vault files or vault passwords
- Terraform state or real `tfvars`

## Example And Template Files

Allowed public patterns:

- `*.example.yaml`
- `*.template.yaml`
- obvious placeholders such as `CHANGE_ME`
- fake domains such as `example.com` or `example.local`

Examples should explain how real values are created outside public Git.

## Recommended Secret Options

### SOPS

Use SOPS when encrypted secret files belong in Git and key management is understood. Private keys and age identities must stay outside public Git.

### SealedSecrets

Use SealedSecrets when the cluster controller owns decryption. Document controller key backup, rotation, and disaster recovery before relying on it.

### ExternalSecrets

Use External Secrets Operator when secrets should come from an external secret manager. Provider credentials must stay outside public Git.

### Manual Bootstrap

Manual `kubectl create secret` is acceptable for bootstrap or small labs when documented, but command history and shell logs must not expose secret values.

## Local Files

Local `.env`, kubeconfig, generated exports, and private inventory files are ignored by `.gitignore`. Do not bypass ignore rules with forced adds unless the file has been reviewed and sanitized.

## Historical Exposure

If a real secret was ever committed, treat it as exposed even if it was later removed. Rotate through a private operational process and avoid documenting the value in public issues or PRs.
