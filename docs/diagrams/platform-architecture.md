# Platform Architecture Diagrams

These Mermaid diagrams render as visual architecture images in GitHub while
remaining reviewable text in Git.

## Production Request And Automation Flow

```mermaid
flowchart TB
    operator[Operator] -->|commit and review| github[GitHub k8s-platform]
    users[Users and administrators] --> cf[Cloudflare DNS and proxy]
    acme[Let's Encrypt] -->|DNS-01 validation| cf

    subgraph cluster[Kubernetes production cluster]
        flux[Flux]
        argo[Argo CD]
        externaldns[ExternalDNS]
        certmanager[cert-manager]
        traefik[Traefik ingress]
        apps[Websites and applications]
        admin[Argo AWX Drone dashboards]
        observability[Prometheus Grafana]
        storage[Longhorn persistent storage]
        secrets[Kubernetes Secrets]

        flux -->|reconciles network automation| externaldns
        flux -->|reconciles issuers| certmanager
        argo -->|reconciles owned workloads| apps
        argo -->|reconciles owned platform paths| admin
        traefik --> apps
        traefik --> admin
        traefik --> observability
        apps --> storage
        observability --> storage
        secrets --> externaldns
        secrets --> certmanager
    end

    github --> flux
    github --> argo
    externaldns -->|A and TXT records| cf
    certmanager -->|challenge records| cf
    certmanager -->|TLS Secrets| traefik
    cf -->|HTTPS to origin| traefik

    classDef edge fill:#f2f7ff,stroke:#2563eb,color:#0f172a;
    classDef control fill:#ecfdf5,stroke:#059669,color:#0f172a;
    classDef runtime fill:#fff7ed,stroke:#ea580c,color:#0f172a;
    classDef data fill:#faf5ff,stroke:#9333ea,color:#0f172a;
    class cf,acme,github edge;
    class flux,argo,externaldns,certmanager control;
    class traefik,apps,admin,observability runtime;
    class storage,secrets data;
```

Current boundaries:

- ExternalDNS manages only `xn--cyberlnx-ykb.com` and
  `getuntoldstory.com`, with TXT ownership and `upsert-only` policy.
- cert-manager uses Cloudflare DNS-01 with separate staging and production
  ClusterIssuers.
- Existing routes continue using Traefik ACME until each certificate is
  migrated deliberately.
- Cloudflare tokens currently live in Kubernetes Secrets. External Secrets is
  staged but not enabled until a backend is selected.
- Flux and Argo CD must not own the same Kubernetes resource.

## Repository And Ownership Structure

```mermaid
flowchart LR
    repo[k8s-platform repository]

    repo --> clusters[clusters]
    repo --> platform[platform]
    repo --> apps[apps]
    repo --> infra[infra]
    repo --> docs[docs]
    repo --> security[security and infra-security]

    clusters --> entry[Production GitOps entry points]
    platform --> network[Network automation]
    platform --> shared[Shared platform services]
    platform --> secretplan[External Secrets package]
    apps --> workloads[Application deployment interfaces]
    infra --> adjacent[Storage and networking manifests]
    docs --> runbooks[Runbooks inventories diagrams]
    security --> controls[Policies host baselines validation]

    privateTf[Private Terraform repo] --> provider[Provider infrastructure]
    privateAnsible[Private Ansible repo] --> nodes[Node configuration]
    secretBackend[Future secret backend] -.-> secretplan

    provider --> entry
    nodes --> entry

    classDef public fill:#eff6ff,stroke:#2563eb,color:#0f172a;
    classDef private fill:#fef2f2,stroke:#dc2626,color:#0f172a;
    classDef planned fill:#f8fafc,stroke:#64748b,color:#0f172a,stroke-dasharray: 5 5;
    class repo,clusters,platform,apps,infra,docs,security,entry,network,shared,workloads,adjacent,runbooks,controls public;
    class privateTf,privateAnsible,provider,nodes private;
    class secretBackend,secretplan planned;
```

## Change Promotion Flow

```mermaid
sequenceDiagram
    participant Engineer
    participant GitHub
    participant Checks
    participant GitOps
    participant Cluster
    participant Cloudflare

    Engineer->>GitHub: Push branch and open pull request
    GitHub->>Checks: Render YAML and scan for secrets
    Checks-->>GitHub: Review result
    Engineer->>GitHub: Merge approved change
    GitOps->>GitHub: Read main branch
    GitOps->>Cluster: Reconcile desired state
    Cluster->>Cloudflare: Reconcile DNS or DNS-01 challenge
    Cluster-->>GitOps: Report health and readiness
```
