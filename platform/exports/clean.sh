#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="/home/k8s-home-lab/platform/exports"
DST_DIR="/home/k8s-home-lab/platform/exports-clean"

mkdir -p "${DST_DIR}"

clean_expr='del(.metadata.managedFields,.metadata.creationTimestamp,.metadata.resourceVersion,.metadata.uid,.metadata.selfLink,.metadata.generation,.metadata.annotations."kubectl.kubernetes.io/last-applied-configuration",.status) | (.items[]? |= (del(.metadata.managedFields,.metadata.creationTimestamp,.metadata.resourceVersion,.metadata.uid,.metadata.selfLink,.metadata.generation,.metadata.annotations."kubectl.kubernetes.io/last-applied-configuration",.status)))'

# Copy non-yaml files (like scripts) and create dirs
rsync -a --exclude='*.yaml' --exclude='*.yml' "${SRC_DIR}/" "${DST_DIR}/"

# Clean yaml files
while IFS= read -r -d '' file; do
  rel="${file#${SRC_DIR}/}"
  out="${DST_DIR}/${rel}"
  out_dir="$(dirname "${out}")"
  mkdir -p "${out_dir}"
  yq eval "${clean_expr}" "${file}" > "${out}"
done < <(find "${SRC_DIR}" -type f \( -name '*.yaml' -o -name '*.yml' \) -print0)

echo "Cleaned exports written to ${DST_DIR}"
