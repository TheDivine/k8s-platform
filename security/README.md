# Security

This directory is for Kubernetes and platform security baselines.

Expected subareas:

- `kyverno/` for admission policies
- `falco/` for runtime detection rules and docs
- `trivy/` for scanner configuration
- `networkpolicies/` for namespace isolation examples
- `rbac/` for RBAC review guidance and examples

Start policies in audit/reporting mode where possible before enforcing them in a live cluster.
