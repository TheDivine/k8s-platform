# External Secrets Migration

## Decision

Move human-managed credentials out of ad hoc Kubernetes Secrets and into a
dedicated secret management platform through External Secrets Operator (ESO).

The backend is not selected yet. Do not enable the production ESO Flux
Kustomization until the backend, authentication method, backup, recovery, and
access model are approved.

The repository includes a controller package pinned to the official chart
`2.6.0`, but it is intentionally not referenced from
`clusters/production/kustomization.yaml`.

The package was Helm-rendered successfully during review. Its namespaced
HelmRelease cannot be independently server-dry-run before the namespace exists;
Flux handles this by applying Namespace resources before namespaced resources
within the same Kustomization.

## Desired Model

```text
Secret platform
  -> ClusterSecretStore or SecretStore
  -> ExternalSecret
  -> Kubernetes Secret
  -> Application
```

Git tracks:

- controller version
- Store and ExternalSecret metadata
- remote logical paths
- target Secret names and keys
- refresh and ownership policy

The secret platform tracks:

- values
- versions
- access policy
- audit history
- rotation dates
- recovery workflow

## Backend Requirements

Evaluate Infisical, HashiCorp Vault, 1Password Connect, or a cloud secret
manager against:

- workload identity or short-lived authentication
- high availability and backup
- audit logging
- version history and rollback
- operator access control
- disaster recovery without the cluster
- support for binary values and registry credentials
- operational effort for a home-lab

Do not select a backend only because it has a convenient UI.

## Migrate

These are good ESO candidates:

| Current Kubernetes Secret | Suggested external path |
| --- | --- |
| `cert-manager/cloudflare-api-token` | `production/cloudflare/api-token` |
| `external-dns/cloudflare-api-token` | `production/cloudflare/api-token` |
| `drone/drone-server-secret` | `production/drone/server` |
| `monitoring` Grafana admin credentials | `production/grafana/admin` |
| `traefik/traefik-dashboard-auth` | `production/traefik/dashboard-basic-auth` |
| `flux-system/cluster-user-auth` | `production/flux/ui` |
| `websites/cyberlynx-blog-env` | `production/cyberlynx-blog/runtime` |
| `law-firm/law-firm-app-secrets` | A private app-specific backend path |
| registry pull Secrets | Registry-specific backend paths |

AWX needs a deliberate operator integration. Pre-create an externally managed
admin password Secret and configure the AWX custom resource to use it rather
than racing the AWX operator's generated Secret.

Grafana should use an `existingSecret` configured in Helm values. Do not let
Helm and ESO both own `monitoring-grafana`.

## Do Not Migrate

Leave controller-generated state under controller ownership:

- Helm release Secrets
- cert-manager ACME account keys
- issued TLS Secrets
- webhook CA and serving certificates
- Longhorn internal webhook certificates
- MetalLB memberlist and webhook state
- Kubernetes Dashboard CSRF key
- generated Prometheus and Alertmanager runtime Secrets
- Argo CD password hash and server signing key unless following an
  Argo-specific migration procedure

Moving generated state into an external platform usually creates ownership
conflicts and weakens controller recovery.

## Bootstrap Problem

ESO needs credentials to reach the secret backend. Prefer, in order:

1. workload identity or machine identity
2. Kubernetes authentication with short-lived tokens
3. a narrowly scoped bootstrap Secret created manually

Never solve secret management by committing the backend credential to Git.

## Migration Sequence

1. Select and deploy the backend outside the cluster failure domain.
2. Configure backup, recovery, audit logging, and operator access.
3. Install ESO from `platform/external-secrets/controller`.
4. Create a Store using a non-static identity where possible.
5. Test with a new low-risk Secret and disposable workload.
6. Migrate the Cloudflare token into both target namespaces.
7. Confirm ExternalDNS and cert-manager continue reconciling.
8. Migrate Drone, Flux UI, BasicAuth, and app runtime credentials.
9. Rotate every value after migration.
10. Remove manual Secret creation instructions once no longer needed.

For each migration:

1. Create the value in the backend.
2. Apply an ExternalSecret targeting a new Secret name.
3. Point the application at the new name.
4. Verify application health and secret refresh.
5. Rotate the value.
6. Delete the old Kubernetes Secret only after rollback time expires.

## Example

The examples under `platform/external-secrets/examples` assume a
`ClusterSecretStore` named `platform-secrets`. They are not included in any
Kustomization and cannot deploy until the backend-specific Store exists.

## Validation

```bash
kubectl get externalsecret,secretstore,clustersecretstore -A
kubectl describe externalsecret <name> -n <namespace>
kubectl get events -A --sort-by=.lastTimestamp
```

Never use `kubectl get secret -o yaml` as a routine validation step.
