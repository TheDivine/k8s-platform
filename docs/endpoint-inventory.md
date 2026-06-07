# Production Endpoint Inventory

Last verified from Kubernetes and Cloudflare on 2026-06-07.

This file tracks public names and access methods, not passwords, tokens,
private keys, password hashes, or provider identifiers.

## Kubernetes Web Endpoints

| Endpoint | Purpose | Namespace | Access | DNS ownership |
| --- | --- | --- | --- | --- |
| `https://xn--cyberlnx-ykb.com/` | Cyberlynx website | `websites` | Public | ExternalDNS annotation present |
| `https://xn--cyberlnx-ykb.com/admin` | Cyberlynx administration | `websites` | Application login and rate limit | ExternalDNS annotation present |
| `https://argo.xn--cyberlnx-ykb.com` | Argo CD | `argocd` | Argo CD login | ExternalDNS managed |
| `https://awx.xn--cyberlnx-ykb.com` | AWX | `awx` | AWX login | ExternalDNS managed |
| `https://drone.xn--cyberlnx-ykb.com` | Drone CI | `drone` | GitHub OAuth | ExternalDNS managed |
| `https://grafana.xn--cyberlnx-ykb.com` | Grafana | `monitoring` | Traefik BasicAuth, then Grafana login | ExternalDNS managed |
| `https://prometheus.xn--cyberlnx-ykb.com` | Prometheus | `monitoring` | Traefik BasicAuth | ExternalDNS managed |
| `https://longhorn.xn--cyberlnx-ykb.com` | Longhorn UI | `longhorn-system` | Traefik BasicAuth | ExternalDNS managed |
| `https://k8s.xn--cyberlnx-ykb.com` | Kubernetes Dashboard | `kubernetes-dashboard` | Kubernetes bearer token | ExternalDNS managed |
| `https://traefik.xn--cyberlnx-ykb.com` | Traefik dashboard | `traefik` | Traefik BasicAuth | ExternalDNS managed |
| `https://hello.xn--cyberlnx-ykb.com` | hello-node test application | `default` | Public test endpoint | ExternalDNS managed |
| `https://whoami.xn--cyberlnx-ykb.com` | Traefik diagnostic endpoint | `default` | Public diagnostic endpoint | Route annotated; DNS record remains manual |
| `https://filipovikjlaw.com` | Law firm website and `/api` | `law-firm` | Public application | Outside current ExternalDNS filters |
| `https://www.filipovikjlaw.com` | Redirect to law firm apex | `law-firm` | Public redirect | Outside current ExternalDNS filters |

## Incomplete Or Reserved Endpoints

| Name | Current state | Required decision |
| --- | --- | --- |
| `flux.example.com` | A live IngressRoute still uses a placeholder hostname | Replace with an approved production name or remove the route |
| `getuntoldstory.com` | DNS apex points to the cluster, but no Kubernetes route currently claims it | Add an application route before treating it as deployed |

## Cloudflare-Only Or Legacy DNS Names

These records exist in Cloudflare but do not currently match an active
Kubernetes Ingress or IngressRoute. They must be reviewed before deletion
because some may serve external systems.

| Name | Record role | Current ownership |
| --- | --- | --- |
| `*.xn--cyberlnx-ykb.com` | Wildcard A record | Manual |
| `awxcentral.xn--cyberlnx-ykb.com` | Legacy or alternate AWX name | Manual |
| `email.xn--cyberlnx-ykb.com` | Mail-related host | Manual |
| `kasm.xn--cyberlnx-ykb.com` | Kasm endpoint | Manual |
| `kasm2.xn--cyberlnx-ykb.com` | Alternate Kasm endpoint | Manual |
| `qwiki.xn--cyberlnx-ykb.com` | Legacy application name | Manual |
| `www.xn--cyberlnx-ykb.com` | Cyberlynx `www` name | Manual |
| `wp-avrm.xn--cyberlnx-ykb.com` | External certificate validation CNAME | Manual; do not remove without identifying the owner |
| `_acme-challenge.kasm...` | Historical ACME validation records | Manual; review with Kasm certificate ownership |

`whoami.xn--cyberlnx-ykb.com` is an active Kubernetes route backed by a
pre-existing manual DNS record. ExternalDNS will not attach ownership to an
unowned record merely because the route is annotated.

The `getuntoldstory.com` zone also contains registrar mail-forwarding MX and
SPF records. ExternalDNS is configured with `upsert-only` and must not replace
or remove those records.

## Network Entry Point

Traefik is the public Kubernetes entry point:

| Service | Type | Public ports |
| --- | --- | --- |
| `traefik/traefik` | `LoadBalancer` | TCP 80 and TCP 443 |

The current ExternalDNS target is `69.30.233.178`. This is a public address and
is also discoverable from DNS; no private node address is recorded here.

## Security Boundary

Cloudflare proxying hides the origin address from normal DNS answers and adds
edge protections, but it is not an authentication control by itself.

Administrative endpoints should move behind Cloudflare Access or an
identity-aware equivalent:

- Argo CD
- AWX
- Grafana
- Prometheus
- Longhorn
- Kubernetes Dashboard
- Traefik dashboard

Keep application-level login and least-privilege RBAC even after adding
Cloudflare Access. Restrict direct origin traffic to Cloudflare address ranges
before relying on Access as the outer security boundary.

## Ownership Rules

- Names with ExternalDNS TXT owner `kubernetes-production` are cluster-owned.
- Manual Cloudflare records are not automatically deleted.
- `xn--cyberlnx-ykb.com` and `getuntoldstory.com` are the only ExternalDNS
  filters.
- `filipovikjlaw.com` remains outside this automation until its ownership is
  explicitly added.
- A DNS record does not prove that an application is healthy. Validate the
  route, certificate, Service, and pods separately.

## Refresh Commands

```bash
kubectl get ingress -A
kubectl get ingressroute.traefik.io -A
kubectl get svc -A
kubectl -n external-dns logs deploy/external-dns --tail=100
```

Cloudflare-only records should be reviewed in the Cloudflare dashboard or
through an authorized read-only API workflow. Never print the API token.
