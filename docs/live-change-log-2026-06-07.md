# Production Change Log: 2026-06-07

## Argo CD Recovery

- Found Argo CD `v3.3.0` in namespace `argocd`.
- `argocd-repo-server` was unavailable because its init container repeatedly
  failed on an existing pod-local symlink.
- Deleted only the failed repo-server pod.
- Kubernetes recreated it successfully.
- Confirmed `infra` and `platform` are `Synced` and `Healthy`.

## Domain Migration

Replaced expired `kwiki.it.com` UI routes with names under
`xn--cyberlnx-ykb.com`. Updated Argo CD, AWX, Drone, Longhorn, Grafana,
Prometheus, Kubernetes Dashboard, Traefik, hello-node, and related application
settings.

`xn--cyberlnx-ykb.com` is the ASCII DNS form of `cyberlınx.com`.

## DNS Automation

- Installed ExternalDNS chart `1.21.1`, application `0.21.0`.
- Enabled Kubernetes Ingress and Traefik IngressRoute discovery.
- Restricted management to `xn--cyberlnx-ykb.com` and
  `getuntoldstory.com`.
- Selected `upsert-only`, TXT ownership, and owner
  `kubernetes-production`.
- Reviewed dry-run output before enabling writes.
- Created nine missing proxied A records and ownership TXT records.
- Left unrelated mail, validation, wildcard, and legacy records unchanged.

## Certificate Automation

- Installed cert-manager `v1.20.2` with CRDs.
- Created staging and production Cloudflare DNS-01 ClusterIssuers.
- Confirmed both issuers report Ready.
- Successfully issued and removed a staging certificate for
  `cm-test.getuntoldstory.com`.

This proved API token access, challenge creation, DNS propagation, ACME
validation, and Kubernetes certificate storage.

## Secret Handling

- The active Cloudflare token is stored only in Kubernetes Secrets in
  `cert-manager` and `external-dns`.
- An initially disclosed token was replaced before controllers were enabled.
- No token or provider account identifier is tracked in Git.
- External Secrets migration is documented but not enabled until a backend is
  selected.

## Scheduling

The controllers select:

```text
platform.cyberlynx.io/control-workloads=true
```

This records scheduling intent without committing a machine-specific hostname.

## Monitoring Rollout

The Grafana hostname change triggered a ReadWriteOnce Longhorn volume
multi-attach condition. The old Grafana pod was deleted, Longhorn reattached
the existing volume, and the Helm upgrade completed as monitoring revision 4.
No persistent data was deleted.

## Tracking Boundary

Before this change, ExternalDNS and cert-manager configuration existed only in
live Helm release state. The repository now contains Flux HelmRelease and
Kustomization definitions, endpoint and credential inventories, and migration
runbooks.

Existing application routes still have mixed ownership across Helm, operators,
GitOps, and historical manual applies. Consolidate them gradually; do not
introduce two active controllers for the same resource.
