#!/usr/bin/env bash
set -u

check_unit() {
  local unit="$1"
  if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files "$unit.service" >/dev/null 2>&1; then
    printf '%-20s %s\n' "$unit" "$(systemctl is-active "$unit" 2>/dev/null || true)"
  else
    printf '%-20s %s\n' "$unit" "not-installed"
  fi
}

check_command() {
  local label="$1"
  local cmd="$2"
  if command -v "$cmd" >/dev/null 2>&1; then
    printf '%-20s %s\n' "$label" "available"
  else
    printf '%-20s %s\n' "$label" "not-installed"
  fi
}

printf 'Security status summary for %s\n' "$(hostname 2>/dev/null || printf unknown)"
printf '%-20s %s\n' "component" "status"
printf '%-20s %s\n' "---------" "------"

check_unit auditd
check_unit fail2ban
check_unit clamav-daemon
check_unit clamav-freshclam
check_unit freshclam
check_unit wazuh-agent

check_command clamscan clamscan
check_command freshclam freshclam
check_command maldet maldet

