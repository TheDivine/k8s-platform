# Proposed Public Repository Tree

This is the target public tree for a clean GitOps/IaC/DevSecOps portfolio repository.

```text
.
├── README.md
├── .gitignore
├── apps/
│   ├── README.md
│   ├── kasm/
│   │   ├── README.md
│   │   ├── docs/
│   │   └── kustomize/
│   └── examples/
│       └── TODO-public-demo-app/
├── archive/
│   └── README.md
├── clusters/
│   ├── README.md
│   ├── production/
│   └── staging/
├── docs/
│   ├── diagrams/
│   ├── public-safety-checklist.md
│   ├── repo-audit.md
│   ├── repo-restructure-plan.md
│   └── proposed-tree.md
├── flux/
│   └── apps/
├── infra/
│   ├── networking/
│   └── storage/
├── platform/
│   ├── argocd/
│   ├── backup/
│   ├── flux/
│   ├── metallb/
│   ├── monitoring/
│   └── traefik/
├── policies/
│   ├── kyverno/
│   ├── networkpolicies/
│   └── rbac/
├── security/
│   ├── ansible/
│   │   ├── linux-hardening/
│   │   ├── ssh-hardening/
│   │   ├── firewall/
│   │   ├── auditd/
│   │   ├── fail2ban/
│   │   ├── clamav/
│   │   └── maldet-web-upload-nodes/
│   ├── falco/
│   └── trivy/
├── terraform/
│   ├── dns/
│   ├── object-storage/
│   └── registry/
└── scripts/
    ├── bootstrap/
    ├── validate/
    └── audit/
```

## Excluded From Public Tree

```text
apps/CyberLynxBlog/.env
apps/*/.git/
apps/*/node_modules/
apps/*/uploads/
apps/*/logs.txt
QloudK-Backup/
platform/exports/
platform/exports-clean/
*.tfstate
*.key
*.pem
*.p12
*.pfx
*.kubeconfig
```

## Management Model

- Argo CD: platform app-of-apps examples and Argo CD-managed platform workloads.
- Flux: `flux/` app wiring, Kustomizations, and image automation if added later.
- Ansible: host hardening, package baselines, SSH, firewall, auditd, fail2ban, ClamAV, and selected Maldet installs.
- Terraform: DNS, object storage, registries, IAM, cloud firewalls, and provider-managed infrastructure.
- Manual bootstrap scripts: first controller install, repository bootstrap, one-time cluster prerequisites, and documented break-glass operations.

## TODOs

- TODO: Decide if `platform/exports-clean` belongs in public as examples or private as generated output.
- TODO: Decide whether to add `policies/`, `security/`, and `terraform/` now or when real examples are ready.
- TODO: Create a sanitized public demo app or clean `apps/kwiki` before exposing it.
