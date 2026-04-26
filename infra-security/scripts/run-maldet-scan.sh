#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SCAN_PATHS_FILE="${SCAN_PATHS_FILE:-$BASE_DIR/maldet/scan_paths}"
IGNORE_PATHS_FILE="${IGNORE_PATHS_FILE:-$BASE_DIR/maldet/ignore_paths}"
LOG_DIR="${LOG_DIR:-/var/log/security-scans}"

mkdir -p "$LOG_DIR"

if ! command -v maldet >/dev/null 2>&1; then
  printf 'ERROR: maldet is not installed.\n' >&2
  exit 1
fi

if [ ! -f "$SCAN_PATHS_FILE" ]; then
  printf 'ERROR: scan paths file missing: %s\n' "$SCAN_PATHS_FILE" >&2
  exit 1
fi

printf 'Using scan paths: %s\n' "$SCAN_PATHS_FILE"
printf 'Using ignore paths: %s\n' "$IGNORE_PATHS_FILE"

while IFS= read -r path; do
  [ -z "$path" ] && continue
  case "$path" in
    /proc|/sys|/dev|/run|/var/lib/kubelet|/var/lib/containerd|/var/lib/docker|/var/lib/longhorn|/var/lib/rancher|/var/lib/etcd|/snap|/mnt/longhorn)
      printf 'SKIP unsafe path: %s\n' "$path"
      ;;
    *)
      if [ -e "$path" ]; then
        printf 'Scanning with Maldet: %s\n' "$path"
        maldet --scan-all "$path" | tee -a "$LOG_DIR/maldet-scan.log"
      else
        printf 'SKIP missing path: %s\n' "$path"
      fi
      ;;
  esac
done < "$SCAN_PATHS_FILE"

