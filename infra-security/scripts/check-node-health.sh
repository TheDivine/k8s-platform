#!/usr/bin/env bash
set -u

failures=0

section() {
  printf '\n== %s ==\n' "$1"
}

run_optional() {
  local label="$1"
  shift
  section "$label"
  if ! "$@"; then
    printf 'WARN: command failed: %s\n' "$*" >&2
  fi
}

check_service() {
  local svc="$1"
  if command -v systemctl >/dev/null 2>&1; then
    if systemctl list-unit-files "$svc.service" >/dev/null 2>&1; then
      systemctl is-active "$svc" || {
        printf 'WARN: service is not active: %s\n' "$svc" >&2
        case "$svc" in
          containerd|kubelet) failures=$((failures + 1)) ;;
        esac
      }
    else
      printf 'INFO: service not installed or not managed by systemd: %s\n' "$svc"
    fi
  fi
}

run_optional "Host identity" hostnamectl
run_optional "Kernel" uname -a
run_optional "Architecture" uname -m
run_optional "IP addresses" ip addr show
run_optional "Routes" ip route show
run_optional "Disk usage" df -h
run_optional "Memory" free -h
run_optional "Swap" swapon --show

section "Systemd services"
check_service ssh
check_service sshd
check_service containerd
check_service kubelet

section "Summary"
if [ "$failures" -gt 0 ]; then
  printf 'CRITICAL: %s critical runtime service check(s) failed.\n' "$failures" >&2
  exit 1
fi

printf 'Node health check completed without critical runtime failures.\n'

