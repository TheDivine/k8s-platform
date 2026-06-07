# Cloudflare DNS And Certificate Automation

## Source Of Truth

The checkout `/home/k8s-home-lab` maps to
`git@github.com:TheDivine/k8s-platform.git`. Flux follows the repository's
`main` branch.

State is intentionally split:

- Git tracks controller versions, allowed zones, ownership IDs, route
  annotations, and issuer definitions.
- Kubernetes temporarily stores the Cloudflare token in two Secrets.
- Cloudflare stores authoritative DNS and proxy state.
- cert-manager stores ACME account keys and generated TLS Secrets.
- A future external secret backend will become the source of sensitive values.

## Request Flow

```text
Ingress or IngressRoute
  -> ExternalDNS
  -> Cloudflare A record and ownership TXT record
  -> Cloudflare proxy
  -> Traefik
  -> Kubernetes Service

Certificate
  -> cert-manager
  -> temporary Cloudflare _acme-challenge TXT record
  -> Let's Encrypt validation
  -> Kubernetes TLS Secret
  -> Traefik
```

## ExternalDNS

Tracked configuration:

- chart `1.21.1`
- application `0.21.0`
- sources `ingress` and `traefik-proxy`
- policy `upsert-only`
- TXT owner `kubernetes-production`
- zones `xn--cyberlnx-ykb.com` and `getuntoldstory.com`

Published routes use:

```yaml
metadata:
  annotations:
    external-dns.alpha.kubernetes.io/cloudflare-proxied: "true"
    external-dns.alpha.kubernetes.io/target: "69.30.233.178"
```

`upsert-only` allows create and update operations but avoids automatic record
deletion. Existing mail, validation, and legacy records remain manual.

## cert-manager

Tracked configuration:

- chart/application `v1.20.2`
- CRDs installed by the Helm release
- staging and production Let's Encrypt ClusterIssuers
- Cloudflare DNS-01 restricted to the two managed zones

DNS-01 works with proxied records and does not expose an HTTP challenge path.
The live ACME account contact is not recorded in this public repository.

### Current TLS Ownership

Most existing routes still contain Traefik's
`traefik.ingress.kubernetes.io/router.tls.certresolver: le` annotation or an
IngressRoute `tls.certResolver: le`. Those certificates are currently owned by
Traefik, not cert-manager.

cert-manager is installed, its Cloudflare DNS-01 issuers are Ready, and staging
issuance was tested successfully. Migrate existing routes one at a time:

1. Create a cert-manager `Certificate`.
2. Wait for its TLS Secret to become Ready.
3. Change the route from `certResolver: le` to `secretName`.
4. Verify origin TLS through Cloudflare.
5. Remove obsolete Traefik ACME state only after every route is migrated.

Do not let Traefik and cert-manager issue the same hostname concurrently.

### Standard Ingress

```yaml
metadata:
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-production-cloudflare
    external-dns.alpha.kubernetes.io/cloudflare-proxied: "true"
    external-dns.alpha.kubernetes.io/target: "69.30.233.178"
spec:
  tls:
    - hosts:
        - app.getuntoldstory.com
      secretName: app-getuntoldstory-com-tls
```

### Traefik IngressRoute

cert-manager does not infer a Certificate from an IngressRoute. Create one:

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: app-getuntoldstory-com
  namespace: example
spec:
  dnsNames:
    - app.getuntoldstory.com
  issuerRef:
    kind: ClusterIssuer
    name: letsencrypt-production-cloudflare
  secretName: app-getuntoldstory-com-tls
---
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: example
  namespace: example
  annotations:
    external-dns.alpha.kubernetes.io/cloudflare-proxied: "true"
    external-dns.alpha.kubernetes.io/target: "69.30.233.178"
spec:
  entryPoints:
    - websecure
  routes:
    - kind: Rule
      match: Host(`app.getuntoldstory.com`)
      services:
        - name: example
          port: 80
  tls:
    secretName: app-getuntoldstory-com-tls
```

Use the staging issuer for the first test, then change to production.

## Add Another Domain

1. Add and activate the Cloudflare zone.
2. Add only that zone to the Cloudflare token resource scope.
3. Add the domain to ExternalDNS `domainFilters`.
4. Add the domain to both ClusterIssuer `dnsZones`.
5. Merge through GitOps.
6. Verify controller reconciliation.
7. Issue and delete a staging test certificate.

Avoid account-wide DNS permission unless every account zone is intentionally
managed by this cluster.

## Verification

```bash
kubectl -n external-dns logs deploy/external-dns --tail=100
kubectl get clusterissuer
kubectl get certificate,certificaterequest,order,challenge -A
```

Both ClusterIssuers were Ready and a staging certificate for
`cm-test.getuntoldstory.com` was issued successfully on 2026-06-07.
