# Maldet Baseline

Maldet is intended only for web, upload, and file-ingest nodes. It should not be enabled blindly on every Kubernetes node.

Use `scan_paths` for candidate scan roots and `ignore_paths` for paths that should not be scanned. Validate both files on each node before scheduling scans.

Recommended defaults:

- quarantine suspicious hits
- do not auto-clean files
- do not suspend users automatically
- use ClamAV integration when available
- keep CPU and IO impact low

