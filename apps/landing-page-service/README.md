# Landing-page service

Canonical production manifests for the static agency offer and fictional Still Detail sample.
The private application source is TheDivine/landing-page-service. Only its public demo assets
enter the image; no campaign, mail, credentials or repository root is served.

## Ownership and deployment

- Flux owns the namespace bootstrap at `platform/app-bootstrap/landing-page-service`.
- The existing production ApplicationSet creates the dedicated `landing-page-service` Argo application.
- Argo reads this public platform repository at `apps/landing-page-service`; no new private Git credential is needed.
- Argo owns the Deployment, Service, Ingress and Certificate in that namespace.
- The image is private GHCR, immutable by digest, built for linux/amd64. The pod selects amd64 nodes.
- ExternalDNS creates pages.processlayerai.com using the existing processlayerai.com zone configuration.
- cert-manager issues landing-page-service-tls through letsencrypt-production-cloudflare.

Homepage: https://pages.processlayerai.com/

Fictional sample: https://pages.processlayerai.com/sample.html

These addresses are intended deployment endpoints, not evidence of live health.

## One-time private image credential

Provision `landing-page-service/landing-page-ghcr-read` as type `kubernetes.io/dockerconfigjson`,
with GHCR read access to TheDivine/landing-page-service. No credential values belong in this repository.
The platform's external secret backend is not enabled, so use the documented manual bootstrap
until an approved backend exists. DNS and TLS do not need manual records or certificate files.

The private source repository provides `scripts/bootstrap_registry.py`. Run it from an authorized
administrative terminal with an explicit production context. It can copy only the GHCR entry
from an existing authorized pull secret, or prompt privately for a read:packages token. It refuses
to overwrite an existing target and does not write credentials to files or command arguments.
Existing credentials must grant access to this package; access to another package alone is insufficient.

## Verification

Build source: application commit 08fa49ff595445233d35f94e630f421e3920af2d.
Build and private visibility check: https://github.com/TheDivine/landing-page-service/actions/runs/34418875590

Before merge: render this directory and clusters/production, check the three existing Kyverno
requirements (container non-root, hardened security context, CPU/memory resources), inspect the
public diff for secrets and run YAML checks. No policy exceptions are needed.

After reconciliation: require Argo Synced/Healthy, a Ready pod, certificate Ready and anonymous HTTPS.
Run the private source repository's `scripts/verify_hosted_demo.py https://pages.processlayerai.com`:
all seven assets must match and private paths must return 403/404. Check desktop/phone navigation.
No outreach worker or mail credentials are deployed with this application.

## Updates and rollback

Build and verify a new image in the private source repository, then update the digest here by PR.
This directory is the production source of truth; the source repo's deploy/k8s is a reference copy.
Rollback subsequent releases by reverting the image digest through Git. On first-release failure,
diagnose and fix the new app; do not alter other production applications. Removing its registry entry
does not delete resources because the ApplicationSet preserves them. Any decommissioning is explicit.
