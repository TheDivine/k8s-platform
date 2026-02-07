# Repository Structure Guide

This document explains the purpose of each top-level folder and how it maps to your DevOps workflow.

## Top-Level Folders
- `platform/`
  - Cluster-wide services: ingress, monitoring, CI, admin tooling
  - These are the shared building blocks of your platform
- `infra/`
  - Foundational cluster resources: storage classes, networking tools
  - Low-level, cluster-specific manifests
- `docs/`
  - Runbooks, onboarding, GitOps guidance, and roadmap
- `clusters/`
  - GitOps entry points for each environment
  - ArgoCD/Flux should watch these paths
- `apps/`
  - Local clones of app repos
  - Not tracked in this repo

## How it Fits Together
1. `platform/` and `infra/` define reusable, stable components.
2. `clusters/` declares the desired state for each environment.
3. Apps are separate repos; their versions are referenced by manifests in `clusters/` or `platform/`.
