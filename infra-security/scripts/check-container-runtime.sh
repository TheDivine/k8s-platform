#!/usr/bin/env bash
set -u

section() {
  printf '\n== %s ==\n' "$1"
}

section "containerd"
if command -v containerd >/dev/null 2>&1; then
  containerd --version || true
else
  printf 'WARN: containerd binary not found.\n'
fi

section "runc"
if command -v runc >/dev/null 2>&1; then
  runc --version || true
else
  printf 'INFO: runc binary not found in PATH.\n'
fi

section "crictl"
if command -v crictl >/dev/null 2>&1; then
  crictl --version || true
  crictl info || true
else
  printf 'WARN: crictl binary not found.\n'
fi

section "/etc/crictl.yaml"
if [ -f /etc/crictl.yaml ]; then
  sed -n '1,120p' /etc/crictl.yaml
else
  cat <<'EOF'
WARN: /etc/crictl.yaml not found.
Recommended containerd configuration:
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
EOF
fi

