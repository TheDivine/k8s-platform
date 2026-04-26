# Trivy

Place Trivy configuration and scan profiles here.

Expected uses:

- repository filesystem scans
- Kubernetes manifest scans
- container image scans
- IaC scans after Terraform is introduced

Do not commit scan outputs if they contain private paths, hostnames, or dependency metadata that should stay private.
