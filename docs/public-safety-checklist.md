# Public Repository Safety Checklist

This repository is intended to be a public DevSecOps and Kubernetes platform reference. Use this checklist before every public commit, pull request, or portfolio push.

## Blockers

- [ ] No kubeconfig files, admin kubeconfigs, or cluster client certs.
- [ ] No private keys, SSH keys, TLS keys, `.pem`, `.key`, `.p12`, or `.pfx` files.
- [ ] No real passwords, API tokens, webhook secrets, OAuth client secrets, or license keys.
- [ ] No cloud access keys, Terraform state, Ansible vault passwords, or provider credentials.
- [ ] No registry credentials or Docker auth config.
- [ ] No production `.env` files.
- [ ] No unencrypted Kubernetes `Secret` manifests with real values.
- [ ] No raw backup dumps, database dumps, tarballs, volume exports, or object store credentials.
- [ ] No nested `.git` directories from imported projects.
- [ ] No generated `node_modules`, build outputs, runtime uploads, logs, or cache directories.
- [ ] No customer data or private business data.
- [ ] No internal-only IP ranges, hostnames, or domains. Use `example.com`, `example.local`, or generic placeholders.
- [ ] No generated cluster exports from `platform/exports/` or `platform/exports-clean/`.
- [ ] No nested local app repositories from ignored `apps/` workspaces.

## Allowed Public Content

- [ ] Sanitized Kubernetes manifests.
- [ ] Example Secret templates with placeholder values only.
- [ ] Placeholder hostnames such as `k8s-node-01.example.com` and `service.example.com`.
- [ ] SOPS, SealedSecrets, or ExternalSecrets examples without private keys.
- [ ] GitOps `Application` and `Kustomization` examples.
- [ ] Architecture diagrams and runbooks.
- [ ] Terraform and Ansible examples without state, inventories, private vars, or vault material.
- [ ] Security policy examples such as Kyverno, NetworkPolicies, Falco rules, and Trivy config.

## Manual Commands To Run Before Publishing

Run these locally and review output without pasting secret values into tickets or PRs:

```bash
git status --short --untracked-files=all
git ls-files
find . -path './.git' -prune -o -path '*/.git' -type d -print
find . -path './.git' -prune -o -type f -name '.env*' -print
find . -path './.git' -prune -o -type f \( -name '*.key' -o -name '*.pem' -o -name '*.p12' -o -name '*.pfx' -o -name '*kubeconfig*' \) -print
rg -l -S 'BEGIN .*PRIVATE KEY|AWS_SECRET_ACCESS_KEY|client_secret|password|token|api[_-]?key|secret' .
rg -n -S 'kwiki\.it\.com|wholesaleinternet\.net|admin123|postgresadmin' .
```

Recommended optional tools:

```bash
gitleaks detect --no-git --redact
trufflehog filesystem . --no-update --only-verified
trivy fs --scanners vuln,secret,misconfig .
```

Repository-local helpers:

```bash
make public-check
make secret-grep
make validate-yaml
make security-scripts-check
```

## Security Baseline Checklist

- [ ] Linux hardening documented and automated where possible.
- [ ] SSH hardening: no password auth, no root login, modern ciphers, short idle timeouts.
- [ ] Firewall baseline: default deny inbound, explicit Kubernetes/control-plane allowances, documented admin paths.
- [ ] `auditd` enabled for host-level accountability.
- [ ] `fail2ban` enabled for exposed SSH or web authentication paths.
- [ ] ClamAV used where file scanning is required.
- [ ] Maldet used only on web, upload, or file-ingest nodes where it is operationally justified.
- [ ] Trivy scans images, manifests, IaC, and filesystem content in CI.
- [ ] Kyverno policies cover privileged pods, hostPath, host networking, image provenance, and resource constraints.
- [ ] Falco or equivalent runtime detection is deployed and tuned.
- [ ] Kubernetes RBAC reviewed for cluster-admin use, wildcard verbs, and service account sprawl.
- [ ] NetworkPolicies isolate platform services and app namespaces.
- [ ] Backup and restore procedures are documented and periodically tested.

## TODOs

- TODO: Add CI checks for secret scanning and Trivy once the repository is clean enough to avoid noisy failures.
- TODO: Keep real lab domains normalized to `example.com` placeholders in public examples.
- TODO: Move risky generated exports to a private archive or replace them with sanitized documentation.
- TODO: Keep `platform/exports`, `platform/exports-clean`, nested private app repos, and `QloudK-Backup` untracked.
