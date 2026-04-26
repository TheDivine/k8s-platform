#!/usr/bin/env bash
set -euo pipefail

cat <<'EOF'
Optional local security tooling for this repository
==================================================

This helper does not install anything automatically. Review the commands below
and run the ones that match your workstation or CI runner.

Ubuntu/Debian examples:

  # shellcheck and yamllint from apt
  sudo apt-get update
  sudo apt-get install -y shellcheck yamllint

  # gitleaks from upstream releases or package manager where available
  # See: https://github.com/gitleaks/gitleaks

  # trivy from Aqua Security packages
  # See: https://aquasecurity.github.io/trivy/

Common validation commands after installation:

  gitleaks detect --no-git --redact
  trivy fs --scanners secret,misconfig .
  shellcheck $(git ls-files '*.sh')
  yamllint .

Keep real credentials, scanner tokens, and private config outside public Git.
EOF
