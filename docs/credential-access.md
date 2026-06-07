# Credential Source And Access Map

This runbook documents usernames, authentication methods, Secret locations,
and safe retrieval or reset procedures. It never records credential values.

## Rules

- Run retrieval commands only from an authorized administrative terminal.
- Avoid screenshots, shell tracing, shared terminals, tickets, and chat.
- Prefer reset or rotation over repeatedly revealing an existing password.
- Kubernetes Secret values are base64 encoded, not encrypted at rest by
  default.
- Do not commit command output.

## Login Map

| Endpoint | Username or identity | Credential source |
| --- | --- | --- |
| Argo CD | `admin` | `argocd/argocd-initial-admin-secret`; changed passwords are represented by a hash in `argocd/argocd-secret` |
| AWX | `admin` | `awx/awx-kwiki-admin-password` |
| Drone | GitHub OAuth identity; configured admin username is `admin` | OAuth client material and user policy in `drone/drone-server-secret` |
| Grafana | `admin` | `monitoring/monitoring-grafana`; outer BasicAuth is separate |
| Prometheus | BasicAuth username `admin` | Hash stored in `traefik/traefik-dashboard-auth` |
| Longhorn | BasicAuth username `admin` | Hash stored in `traefik/traefik-dashboard-auth` |
| Traefik dashboard | BasicAuth username `admin` | Hash stored in `traefik/traefik-dashboard-auth` |
| Kubernetes Dashboard | Kubernetes ServiceAccount identity | Generate a short-lived token for `kubernetes-dashboard/admin-user` |
| Weave GitOps | `admin` | `flux-system/cluster-user-auth` |
| Cyberlynx admin | Key `ADMIN_USER` | Password/token keys in `websites/cyberlynx-blog-env` |
| Law firm application | Application-specific bootstrap flow | `law-firm/law-firm-app-secrets` |

The hello-node and whoami routes are public diagnostic endpoints and currently
have no application login.

## Safe Retrieval Commands

### Argo CD

The initial admin password can be displayed with:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath='{.data.password}' | base64 -d
echo
```

If the admin password was changed, the initial value may no longer work.
`argocd-secret` contains only the password hash and cannot reveal the new
plaintext password. Reset it through the documented Argo CD account process
rather than trying to decode the hash.

### AWX

```bash
kubectl -n awx get secret awx-kwiki-admin-password \
  -o jsonpath='{.data.password}' | base64 -d
echo
```

The AWX custom resource reports both the admin username and the generated
password Secret name.

### Grafana

```bash
kubectl -n monitoring get secret monitoring-grafana \
  -o jsonpath='{.data.admin-user}' | base64 -d
echo

kubectl -n monitoring get secret monitoring-grafana \
  -o jsonpath='{.data.admin-password}' | base64 -d
echo
```

Grafana is also behind the shared Traefik BasicAuth middleware, so both layers
may be requested.

### Traefik BasicAuth

The Secret stores an htpasswd hash, not a recoverable password:

```bash
kubectl -n traefik get secret traefik-dashboard-auth \
  -o jsonpath='{.data.users}' | base64 -d | cut -d: -f1
```

The current username is `admin`. Reset the BasicAuth Secret with a newly
generated htpasswd entry when the password is lost or rotated.

### Drone

Drone uses GitHub OAuth; there is no local Drone password to retrieve. The
Secret contains:

- GitHub OAuth client ID and client secret
- RPC secret
- database connection string
- public server hostname
- admin user policy

Do not decode these values for routine login. Rotate OAuth material in GitHub
and the selected external secret backend.

### Kubernetes Dashboard

Generate a short-lived token:

```bash
kubectl -n kubernetes-dashboard create token admin-user --duration=1h
```

Treat the token as a cluster-admin credential. Do not save it in Git or a
password manager as a long-lived password.

### Weave GitOps

```bash
kubectl -n flux-system get secret cluster-user-auth \
  -o jsonpath='{.data.username}' | base64 -d
echo

kubectl -n flux-system get secret cluster-user-auth \
  -o jsonpath='{.data.password}' | base64 -d
echo
```

The live route still uses `flux.example.com`; see
`docs/endpoint-inventory.md`.

### Cyberlynx Administration

```bash
kubectl -n websites get secret cyberlynx-blog-env \
  -o jsonpath='{.data.ADMIN_USER}' | base64 -d
echo
```

`ADMIN_PASSWORD` and `ADMIN_TOKEN` are sensitive. Retrieve them only for an
authorized incident or migration. The Secret currently contains an anomalous
unidentified key name; review and remove it after confirming it is unused.

## Non-Login Secrets

The following are operational credentials but are not normal UI passwords:

| Secret | Purpose |
| --- | --- |
| `cert-manager/cloudflare-api-token` | Cloudflare DNS-01 challenges |
| `external-dns/cloudflare-api-token` | Cloudflare DNS record management |
| `law-firm/law-firm-app-secrets` | Application database, bootstrap, and cloud credentials |
| `law-firm/law-firm-postgres-postgresql` | PostgreSQL passwords |
| `websites/dockerhub-creds` | Registry pull credentials |
| `law-firm/ghcr-pull-secret` | Registry pull credentials |
| `flux-system/flux-system` | Flux Git deploy key |

Controller-generated TLS keys, webhook certificates, Helm release Secrets,
CSRF keys, and ACME account keys should not be treated as user credentials.

## Rotation Register

Track rotation metadata in the external secret platform, not plaintext values:

- secret owner
- application and namespace
- external secret path
- target Kubernetes Secret
- date created
- date last rotated
- next rotation due
- incident or change reference
- recovery owner

The repository should track the mapping and policy. The secret platform should
track the value and version history.
