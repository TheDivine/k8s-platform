# Tools

This directory is for local helper tools that support audit, validation, scanning, and operator workflows.

Tools may wrap commands such as `kustomize`, `helm`, `trivy`, `gitleaks`, or YAML linters, but they should not become the source of truth for infrastructure state.

Rules:

- Prefer read-only or dry-run behavior by default.
- Do not embed credentials, kubeconfigs, tokens, or host-specific secrets.
- Document required environment variables and expected working directory.
- Keep destructive actions out unless guarded by explicit operator confirmation.
