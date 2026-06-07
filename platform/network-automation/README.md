# Network Automation

This package records the desired state for Cloudflare DNS automation and
Let's Encrypt DNS-01 certificate issuance.

## Ownership

- Flux reconciles the two child `Kustomization` objects from
  `clusters/production/network-automation.yaml`.
- Flux Helm Controller owns the `cert-manager` and `external-dns` releases.
- ExternalDNS owns only records carrying the TXT owner
  `kubernetes-production`.
- cert-manager owns ACME account keys, challenge records, and requested
  certificate Secrets.
- Cloudflare remains authoritative for DNS.
- The Cloudflare API token is bootstrapped outside Git until External Secrets
  migration is complete.

## Managed Zones

- `xn--cyberlnx-ykb.com`, the ASCII DNS form of `cyberlınx.com`
- `getuntoldstory.com`

ExternalDNS cannot modify records outside these `domainFilters`. The
cert-manager solvers are restricted to the same zones.

## Bootstrap Dependency

The `cloudflare-api-token` Secret must exist in both `cert-manager` and
`external-dns` before Flux enables these releases. Follow
`docs/credential-access.md`; never commit or paste the token into a manifest.

The live ACME account may have a contact email, but it is intentionally omitted
from this public repository. cert-manager supports ACME accounts without a
committed contact address.

Controllers select a stable node label instead of a literal hostname:

```bash
kubectl label node <healthy-node> \
  platform.cyberlynx.io/control-workloads=true --overwrite
```

## Reconciliation Order

1. Flux installs namespaces, chart repositories, and Helm releases.
2. The `network-automation` Kustomization waits for controller readiness.
3. `network-automation-issuers` applies ClusterIssuers afterward.

This prevents issuer resources from racing cert-manager CRD and webhook
installation.
