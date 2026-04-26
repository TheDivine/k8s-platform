# Scripts

This directory is for operator scripts and bootstrap wrappers.

Scripts should support documented workflows and should not replace GitOps, Terraform, or Ansible as the source of truth.

Rules:

- Prefer dry-run modes.
- Avoid embedded credentials.
- Document prerequisites.
- Keep destructive behavior explicit and guarded.
