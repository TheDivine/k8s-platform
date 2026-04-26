# Terraform Private Repo Plan

Real infrastructure provisioning should live in a separate private Terraform repository. This keeps provider credentials, state, environment variables, and production topology out of the public portfolio repo.

## Boundary

This public repository may contain non-sensitive Terraform examples in the future, but it must not contain:

- `.terraform/`
- `*.tfstate`
- real `*.tfvars`
- provider credentials
- private backend configuration
- production DNS zones or private firewall values

## Suggested Private Repo Structure

```text
terraform/
  environments/
    staging/
    production/
  modules/
    proxmox-vm/
    dns/
    object-storage/
    firewall/
  docs/
  README.md
```

## Suggested Ownership

- `environments/staging/`: staging inputs, backend config, and provider wiring.
- `environments/production/`: production inputs, backend config, and provider wiring.
- `modules/proxmox-vm/`: reusable VM provisioning module.
- `modules/dns/`: DNS records and zones.
- `modules/object-storage/`: S3-compatible buckets, lifecycle rules, and backup targets.
- `modules/firewall/`: provider firewall rules, allowlists, and public exposure controls.
- `docs/`: private operational notes, backend setup, and recovery steps.

## Workflow

1. Keep state in a private remote backend.
2. Run `terraform fmt` and `terraform validate`.
3. Review `terraform plan` before every apply.
4. Store sensitive variables in a private secret manager or secure CI/CD variables.
5. Export only sanitized diagrams and lessons back to this public repository.

TODO: Decide provider targets and remote state backend outside this public repo.
