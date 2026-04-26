# Architecture

This document describes the inferred current architecture and a proposed target architecture for a reusable DevSecOps platform baseline.

## Intended Portfolio Architecture

This repository is the public portfolio/reference layer. It shows how the Kubernetes platform is organized, how GitOps ownership should work, and how security and operating standards are documented without publishing private environment data.

The intended split is:

- Public `k8s-home-lab` repo: sanitized GitOps examples, platform manifests, docs, runbooks, and public-safe scaffolds.
- Private Terraform repo: real infrastructure provisioning, provider configuration, DNS, firewall, object storage, and state.
- Private Ansible/security repo: real inventories, host hardening, Wazuh enrollment, SSH hardening, firewall automation, and node validation.
- Private app repos: application source code, CI pipelines, and release workflows.
- Kubernetes cluster: reconciles approved platform and app desired state through Argo CD or Flux.

## Workload Direction

Kasm is being treated as the example application migration path: the previous host-managed Docker Compose model should be replaced by a Kubernetes-native, GitOps-friendly deployment after upstream chart or manifest details are validated. The public repo keeps only scaffolded namespace, storage, ingress, documentation, and placeholder secrets.

Drone CI is positioned as a CI system for builds and automation, with real OAuth, RPC, and database secrets managed outside public Git. AWX is positioned as an optional Ansible execution layer for node and host automation, but real inventories and credentials belong in the private Ansible/security repo.

Terraform owns infrastructure provisioning in a private repo. Ansible owns node configuration in a private repo. Argo CD or Flux owns Kubernetes desired state from this public-safe GitOps surface.

## Repository Separation Diagram

```mermaid
flowchart TB
    dev[Developer or operator] --> forge[GitHub or Gitea]

    forge --> publicRepo[Public k8s-home-lab repo]
    forge --> privateTf[Private Terraform provisioning repo]
    forge --> privateAnsible[Private Ansible security repo]
    forge --> privateApps[Private app repos]

    publicRepo --> gitops[Argo CD or Flux]
    privateApps --> ci[CI builds images or charts]
    ci --> registry[Container registry]
    privateTf --> infraResources[DNS firewall object storage compute]
    privateAnsible --> nodes[Linux and Kubernetes nodes]

    gitops --> cluster[Kubernetes cluster]
    registry --> cluster
    infraResources --> cluster
    nodes --> cluster
```

## GitOps Flow Diagram

```mermaid
flowchart LR
    commit[Developer commit] --> git[Git repository]
    git --> checks[CI lint secret scan render checks]
    checks --> controller[Argo CD or Flux]
    controller --> cluster[Kubernetes cluster]
    cluster --> ingress[Traefik ingress]
    cluster --> storage[Longhorn storage]
    cluster --> monitoring[Monitoring stack]

    ingress --> users[Users and admins]
    storage --> stateful[Stateful workloads]
    monitoring --> alerts[Grafana and Alertmanager]
```

## Node Security And Monitoring Diagram

```mermaid
flowchart TB
    nodes[Linux and Kubernetes nodes]

    nodes --> auditd[auditd]
    nodes --> scanners[ClamAV and Maldet]
    nodes --> wazuh[Wazuh agent]
    nodes --> shipper[Promtail or Fluent Bit]
    nodes --> metrics[Node and kube metrics]

    auditd --> shipper
    scanners --> shipper
    wazuh --> wazuhMgr[Wazuh manager]
    shipper --> loki[Loki]
    metrics --> prometheus[Prometheus]
    prometheus --> alertmanager[Alertmanager]
    prometheus --> grafana[Grafana]
    loki --> grafana
    wazuhMgr --> securityReview[Security review]
    grafana --> opsReview[Operations review]
    alertmanager --> opsReview
```

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
- Terraform owns external infrastructure resources in a private repo.
- Ansible owns OS and node configuration in a private repo.
- Helm packages reusable deployments.
- Scripts are wrappers and validation helpers.
- Manual actions are reduced, documented, and reviewed.
- Secrets are never committed as real values.

## Repository Responsibility Split

```mermaid
flowchart LR
    baseline[Public DevSecOps baseline repo]

    baseline --> k8s[infra-k8s-cluster]
    baseline --> security[infra-security]
    baseline --> monitoring[infra-monitoring]
    baseline --> apps[infra-apps]
    baseline --> docs[infra-docs]

    k8s --> clusters[clusters/]
    k8s --> platform[platform/]
    k8s --> flux[flux/]

    security --> nodeSecurity[infra-security/]
    security --> policies[security/]
    security --> scans[tools/audit and validation]

    monitoring --> prom[Prometheus]
    monitoring --> grafana[Grafana]
    monitoring --> loki[Loki]

    apps --> appScaffolds[apps/]
    apps --> examples[public examples]

    docs --> runbooks[docs/]
    docs --> diagrams[docs/diagrams/]
```

## Runtime Security Architecture

```mermaid
flowchart TB
    git[Git repository] --> awx[AWX running Ansible from Git]
    awx --> nodes[Linux and Kubernetes nodes]

    subgraph cluster[Kubernetes cluster]
        cp[control-plane services]
        workers[worker nodes]
        traefik[Traefik]
        metallb[MetalLB]
        prom[Prometheus]
        grafana[Grafana]
        loki[Loki]
    end

    nodes --> auditd[auditd]
    nodes --> fail2ban[fail2ban]
    nodes --> clamav[ClamAV]
    nodes --> maldet[Maldet on web/upload/file nodes]
    nodes --> wazuhAgent[Wazuh agent]
    nodes --> containerd[containerd and crictl]
    nodes --> kubelet[kubelet]

    wazuhAgent --> wazuhMgr[Wazuh manager outside cluster]
    auditd --> loki
    containerd --> loki
    kubelet --> loki
    prom --> grafana
    loki --> grafana
```

## Security Event Flow

```mermaid
flowchart LR
    hostLogs[Host logs] --> auditd[auditd]
    scanLogs[ClamAV and Maldet scan logs] --> shipper[promtail or fluent-bit]
    runtimeLogs[containerd and kubelet logs] --> shipper
    auditd --> wazuhAgent[Wazuh agent]
    auditd --> shipper

    shipper --> loki[Loki]
    loki --> grafana[Grafana alerts]
    wazuhAgent --> wazuhManager[Wazuh manager]
    wazuhManager --> wazuhDashboard[Wazuh dashboard]

    grafana --> operator[Operator review]
    wazuhDashboard --> operator
```
