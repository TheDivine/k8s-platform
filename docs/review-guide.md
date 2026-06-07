# Repository Review Guide

Use this guide when reviewing the repository before applying any manifest or turning the repo into a long-term public portfolio baseline.

## Review Order

1. Read `README.md` for the public-facing story.
2. Read `docs/architecture.md` for the target platform model.
3. Read `docs/repository-model.md` and `docs/public-private-boundary.md` to confirm the public/private split.
4. Read `docs/secret-management.md` and `docs/public-safety-checklist.md` before reviewing manifests.
5. Review platform manifests under `platform/` and cluster entry points under `clusters/`.
6. Review app examples under `apps/kasm/`.
7. Review operational runbooks under `docs/`.
8. Review example security automation under `infra-security/`.

## Manifest Review Checklist

- Confirm hostnames are placeholders or intentionally updated to the new domain.
- Confirm no real passwords, tokens, kubeconfigs, private keys, or `.env` values are present.
- Confirm Kubernetes `Secret` files are examples/templates only.
- Confirm generated exports are ignored and untracked.
- Confirm any node selector uses generic labels rather than one real host.
- Confirm ingress exposure is intentional and protected.
- Confirm storage classes and PVC sizes match the target environment.

## Decision Process

For each platform component, document:

- owner: Argo CD, Flux, Terraform, Ansible, manual, or private repo
- purpose: why the component exists
- inputs: secrets, domains, storage, image tags, CRDs, dependencies
- rollout: how it is applied or reconciled
- validation: what commands prove it works
- rollback: how to back out safely
- public boundary: what must never be committed

## Before Applying Anything

Run local checks:

```bash
git status --short --untracked-files=all
git diff --check
make public-check
```

Optional scanners:

```bash
gitleaks detect --no-git --redact
trivy fs --scanners secret,misconfig .
```

Then apply only through the documented GitOps or private automation path.
