# Roadmap

This roadmap captures the next phases for building a professional DevOps portfolio around the k8s platform.

## Phase 1: Platform Baseline (Now)
- Ensure platform repo structure is stable and documented
- Centralize ingress and networking policies
- Lock versions of key platform components
- Add GitOps scaffolding

## Phase 2: Storage & Data Services
- Add MinIO for S3-compatible object storage
- Define storage classes and backup policies
- Evaluate Longhorn vs. NFS for persistence
- Add Velero (or equivalent) for cluster backup

## Phase 3: Observability
- Expand Prometheus + Grafana dashboards
- Add Loki for logs and Tempo or Jaeger for traces
- Create alerting policies and SLO baselines

## Phase 4: CI/CD & Delivery
- Standardize CI templates for apps
- Use GitOps for production deploys
- Add preview environments for PRs

## Phase 5: Portfolio Apps
- Blog site (separate repo)
- 1–2 reference apps with Helm charts
- Public demo endpoints

## Phase 6: Security & Reliability
- Network policies and RBAC hardening
- Secret management (SOPS, External Secrets, or Vault)
- Disaster recovery runbook
