#!/usr/bin/env bash
set -u

section() {
  printf '\n== %s ==\n' "$1"
}

section "Services"
for svc in containerd kubelet; do
  if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files "$svc.service" >/dev/null 2>&1; then
    printf '%s: %s\n' "$svc" "$(systemctl is-active "$svc" 2>/dev/null || true)"
  else
    printf '%s: not-installed\n' "$svc"
  fi
done

section "crictl"
if command -v crictl >/dev/null 2>&1; then
  crictl --version || true
  crictl info || true
else
  printf 'WARN: crictl not found.\n'
fi

section "Kernel modules"
if command -v lsmod >/dev/null 2>&1; then
  lsmod | grep -E '^(br_netfilter|overlay)' || true
fi

section "Sysctl"
for key in net.bridge.bridge-nf-call-iptables net.ipv4.ip_forward; do
  sysctl "$key" 2>/dev/null || printf 'WARN: sysctl unavailable: %s\n' "$key"
done

section "Swap"
swapon --show || true

