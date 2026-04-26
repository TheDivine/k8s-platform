# Architecture

This document describes the inferred current architecture and a proposed target architecture for a reusable DevSecOps platform baseline.

## Current Inferred Architecture

The repository represents a Kubernetes home lab with:

- Kubernetes cluster components such as kube-apiserver, etcd, kubelet, and kube-proxy.
- Networking through MetalLB and Traefik.
- GitOps controllers through Flux and Argo CD.
- Platform services including monitoring, backup, Drone CI, and Kubernetes dashboard variants.
- Storage through local-path and Longhorn-related monitoring/ingress.
- Backup components through Velero and MinIO examples.
- Application workspaces under `apps/`, with Kasm scaffolded for Kubernetes and other apps kept as local nested workspaces.
- Local generated cluster exports present on disk but ignored and untracked.

## Proposed Target Architecture

The target architecture keeps the repository as a clean baseline:

- `clusters/` defines cluster entry points and controller bootstrap.
- `platform/` contains curated platform services with clear GitOps ownership.
- `apps/` contains clean app deployment interfaces and documentation.
- `infra/` contains cluster-adjacent manifests.
- `terraform/` manages external/provider infrastructure later.
- `ansible/` manages Linux and Kubernetes node configuration later.
- `security/` contains policy, detection, and scanning baselines later.
- `tools/` and `scripts/` provide wrappers and validation helpers only.

## Current Architecture Diagram

```mermaid
flowchart TB
    repo[Git repository] --> clusters[clusters/production]
    repo --> platform[platform services]
    repo --> apps[apps and local app workspaces]
    repo --> infra[infra manifests]
    repo --> docs[docs and runbooks]

    clusters --> fluxSystem[Flux system manifests]
    clusters --> argoApps[Argo CD app manifests]
    clusters --> fluxUi[Flux UI ingress]

    platform --> argocd[Argo CD]
    platform --> flux[Flux UI/resources]
    platform --> traefik[Traefik]
    platform --> metallb[MetalLB]
    platform --> monitoring[Monitoring]
    platform --> backup[Velero and MinIO]
    platform --> drone[Drone CI]

    apps --> kasm[Kasm scaffold]
    apps --> localApps[Ignored local app workspaces]

    traefik --> metallb
    backup --> storage[Longhorn/local-path/storage]
    monitoring --> cluster[Kubernetes cluster]
```

## Proposed GitOps And IaC Architecture

```mermaid
flowchart TB
    git[Public baseline repo] --> clusterEntry[clusters/]
    git --> platformSrc[platform/]
    git --> appSrc[apps/]
    git --> policySrc[security/]
    git --> ansibleSrc[ansible/]
    git --> terraformSrc[terraform/]

    clusterEntry --> gitops[Argo CD or Flux]
    gitops --> platformServices[Platform services]
    gitops --> appServices[Application services]
    gitops --> policies[Admission and network policies]

    terraformSrc --> externalInfra[DNS/object storage/registry/firewall]
    ansibleSrc --> nodes[Linux and Kubernetes nodes]

    externalInfra --> clusterIngress[Traefik and MetalLB]
    nodes --> k8s[Kubernetes cluster]
    platformServices --> k8s
    appServices --> k8s
    policies --> k8s
```

## Repository Organization Diagram

```mermaid
flowchart LR
    repo[Repository] --> apps[apps/]
    repo --> platform[platform/]
    repo --> clusters[clusters/]
    repo --> infra[infra/]
    repo --> docs[docs/]
    repo --> flux[flux/]
    repo --> future[future folders]

    apps --> appScaffolds[Clean app scaffolds]
    apps --> localWorkspaces[Ignored local workspaces]

    platform --> ingress[Traefik/MetalLB]
    platform --> gitops[Argo CD/Flux]
    platform --> observability[Monitoring]
    platform --> backup[Backup]

    future --> ansible[ansible/]
    future --> terraform[terraform/]
    future --> security[security/]
    future --> tools[tools/]
    future --> scripts[scripts/]
```

## Deployment Flow Diagram

```mermaid
sequenceDiagram
    participant Engineer
    participant Git
    participant CI
    participant GitOps
    participant Cluster

    Engineer->>Git: Commit manifest, docs, or IaC change
    Git->>CI: Run lint, render, secret scan, policy checks
    CI-->>Git: Report pass/fail
    GitOps->>Git: Pull approved desired state
    GitOps->>Cluster: Reconcile owned Kubernetes resources
    Cluster-->>GitOps: Health and sync status
    Engineer->>Cluster: Manual bootstrap or break-glass only when documented
```

## Target Principles

- Git is the desired-state source for Kubernetes resources.
- Terraform owns external infrastructure resources.
- Ansible owns OS and node configuration.
- Helm packages reusable deployments.
- Scripts are wrappers and validation helpers.
- Manual actions are reduced, documented, and reviewed.
- Secrets are never committed as real values.
