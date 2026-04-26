#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SCAN_PATHS_FILE="${SCAN_PATHS_FILE:-$BASE_DIR/maldet/scan_paths}"
LOG_DIR="${LOG_DIR:-/var/log/security-scans}"
LOG_FILE="$LOG_DIR/clamav-scan.log"

mkdir -p "$LOG_DIR"

if ! command -v clamscan >/dev/null 2>&1; then
  printf 'ERROR: clamscan is not installed.\n' >&2
  exit 1
fi

if [ ! -f "$SCAN_PATHS_FILE" ]; then
  printf 'ERROR: scan paths file missing: %s\n' "$SCAN_PATHS_FILE" >&2
  exit 1
fi

EXCLUDES=(
  '--exclude-dir=^/proc'
  '--exclude-dir=^/sys'
  '--exclude-dir=^/dev'
  '--exclude-dir=^/run'
  '--exclude-dir=^/var/lib/kubelet'
  '--exclude-dir=^/var/lib/containerd'
  '--exclude-dir=^/var/lib/docker'
  '--exclude-dir=^/var/lib/longhorn'
  '--exclude-dir=^/var/lib/rancher'
  '--exclude-dir=^/var/lib/etcd'
  '--exclude-dir=^/snap'
  '--exclude-dir=^/mnt/longhorn'
)

while IFS= read -r path; do
  [ -z "$path" ] && continue
  if [ -e "$path" ]; then
    printf 'Scanning with ClamAV: %s\n' "$path"
    clamscan -r --infected --log="$LOG_FILE" "${EXCLUDES[@]}" "$path"
  else
    printf 'SKIP missing path: %s\n' "$path"
  fi
done < "$SCAN_PATHS_FILE"

