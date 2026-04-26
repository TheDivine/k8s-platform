# Platform Architecture Diagrams

## 1. High-Level Repository Architecture

```mermaid
flowchart TB
    github[Public GitHub repository]
    privateTf[Private Terraform repo]
    privateAnsible[Private Ansible/security repo]
    privateApps[Private app repos]

    github --> gitops[GitOps controller: Flux or Argo CD]
    privateTf --> infra[Infrastructure resources]
    privateAnsible --> nodes[Linux and Kubernetes nodes]
    privateApps --> images[Container images and charts]

    infra --> cluster[Kubernetes cluster]
    nodes --> cluster
    images --> cluster
    gitops --> cluster

    cluster --> monitoring[Monitoring stack]
    cluster --> security[Security stack]
    cluster --> workloads[Application workloads]
```

## 2. GitOps Deployment Flow

```mermaid
flowchart LR
    commit[Developer commit] --> repo[GitHub repository]
    repo --> checks[Lint render secret scan]
    checks --> controller[Flux or Argo CD]
    controller --> cluster[Kubernetes cluster]
    cluster --> traefik[Traefik ingress]
    cluster --> workloads[Platform and app workloads]
    cluster --> monitoring[Monitoring feedback]
    monitoring --> developer[Operator review]
```

## 3. Infrastructure Provisioning And Configuration Flow

```mermaid
flowchart TB
    tf[Private Terraform repo] --> provision[Provision VMs DNS object storage firewall]
    ansible[Private Ansible/security repo] --> harden[Configure and harden nodes]
    bootstrap[kubeadm or bootstrap docs] --> join[Initialize or join nodes]
    gitops[GitOps from public repo] --> platform[Deploy platform components]
    validation[Monitoring and security validation] --> review[Operator review]

    provision --> nodes[Nodes and external resources]
    harden --> nodes
    nodes --> join
    join --> cluster[Kubernetes cluster]
    platform --> cluster
    cluster --> validation
```

## 4. Security And Observability Architecture

```mermaid
flowchart TB
    nodes[Linux and Kubernetes nodes]
    nodes --> auditd[auditd]
    nodes --> scanners[ClamAV and Maldet]
    nodes --> wazuh[Wazuh agent]
    nodes --> logs[Promtail or Fluent Bit]
    nodes --> metrics[Prometheus exporters]

    auditd --> logs
    scanners --> logs
    wazuh --> wazuhMgr[Wazuh manager]
    logs --> loki[Loki]
    metrics --> prometheus[Prometheus]
    prometheus --> alertmanager[Alertmanager]
    prometheus --> grafana[Grafana]
    loki --> grafana
    alertmanager --> operator[Operator notification]
    grafana --> operator
    wazuhMgr --> securityReview[Security review]
```

## 5. Public And Private Repo Boundary

```mermaid
flowchart LR
    public[Public repo]
    private[Private repos]

    public --> docs[docs diagrams runbooks]
    public --> examples[examples templates placeholders]
    public --> gitops[GitOps structure]
    public --> sanitized[Sanitized manifests]

    private --> secrets[secrets credentials kubeconfigs]
    private --> inventories[real inventories host vars]
    private --> tfvars[tfvars state backend config]
    private --> apps[private app source]
    private --> exports[generated cluster exports]
```
