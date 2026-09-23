# LFCE private staging

Prepared for owner-operated bootstrap. Flux registers only the namespace and
encrypted credentials. The application bundle is NOT registered with Argo;
workload deployment waits for successful decryption and server validation.

## Ownership

Flux owns namespace and SealedSecrets through
`platform/app-bootstrap/lfce-staging`. Argo will read this public platform
repository at `apps/lfce-staging`. No private LFCE Git deploy key is needed.
The application source remains private in TheDivine/lfce_app; only reviewed
manifests and the standalone credential helper are exported here.

The host is `lfce-app.xn--cyberlnx-ykb.com`. ExternalDNS owns the proxied
record; cert-manager uses `letsencrypt-production-cloudflare` for a trusted
origin certificate. The issuer's name does not make this a production app.
Providers remain mock, with a single operator login. No client accounts.

## Owner bootstrap

The owner's encrypted bootstrap has been returned and added to Git. Do not
regenerate credentials. Preserve the matching private operator credentials
on the admin server; proceed to the verification section below after merge.
The generation instructions remain here for reference, not for routine reruns.

Run the standalone `prepare_credentials.py` on the admin server with Python 3,
kubectl and kubeseal. Supply an explicit context. The helper checks API access,
Longhorn, the Ready issuer and node, existing LFCE data/secrets, and the exact
backend/frontend registry digests before generating credentials.

```bash
python3 platform/app-bootstrap/lfce-staging/prepare_credentials.py \
  --context "$(kubectl config current-context)"
```

It prompts privately for a GHCR read:packages token and the dashboard email.
Alternatively, add
`--registry-source landing-page-service/landing-page-ghcr-read` to reuse only
that Secret's GHCR entry. The helper verifies access to BOTH LFCE packages;
access to the landing-page package alone is insufficient.

Return only `lfce-bootstrap-private/lfce-bootstrap.sealed.json`.
Keep `operator-credentials.PRIVATE.json` in the private server directory and
password manager. Do not paste or commit it. Existing output is refused to
prevent accidental password regeneration. The helper never applies resources.

## Activation after returned credentials

1. Completed in the bootstrap change: validated exactly `lfce-staging-secrets`
   and `ghcr-pull`, scoped strictly to `lfce-staging`, with encrypted values only.
2. Completed in the bootstrap change: registered Flux Kustomization
   `lfce-staging-bootstrap`, path `./platform/app-bootstrap/lfce-staging`,
   source `flux-system`, `prune: false`, `wait: true`.
3. After merge, require Flux Ready and both SealedSecrets Synced using the
   commands below. Do not add application registration before decryption.
4. From this reviewed checkout, run server dry-runs for `apps/lfce-staging`
   and `apps/lfce-staging/migration`. Also server-dry-run rendered Pod
   templates to catch admission policies that are not autogen-enabled.
5. Add `clusters/production/app-registry/lfce-staging.app.yaml`:
   repoURL `https://github.com/TheDivine/k8s-platform.git`, revision `main`,
   path `apps/lfce-staging`, name/namespace `lfce-staging`.
6. Merge application registration, wait for PostgreSQL Ready, then run:

```bash
kubectl -n lfce-staging rollout status statefulset/lfce-postgres --timeout=5m
kubectl apply --dry-run=server -k apps/lfce-staging/migration
kubectl apply -k apps/lfce-staging/migration
kubectl -n lfce-staging wait --for=condition=complete job/lfce-migrate --timeout=5m
kubectl -n lfce-staging logs job/lfce-migrate
kubectl -n lfce-staging rollout status deployment/lfce-backend --timeout=5m
kubectl -n lfce-staging rollout status deployment/lfce-worker --timeout=5m
kubectl -n lfce-staging rollout status deployment/lfce-frontend --timeout=5m
kubectl -n lfce-staging get pods,pvc,certificate,ingress
```

Do not rerun a failed migration blindly. It is excluded from normal Argo sync.
These PostgreSQL settings initialize a NEW database under `data/pgdata`.
Existing LFCE PVCs require inspection and backup, never automatic reinitialization.

## Verify the bootstrap on the admin server

First confirm `kubectl config current-context` is the intended cluster. Flux
will pick up main automatically. If the Flux CLI is installed, this optional
command requests an immediate refresh of the existing root reconciliation:

```bash
flux reconcile kustomization flux-system --with-source
```

Wait until `lfce-staging-bootstrap` appears, then run these checks in order.
Stop and investigate if a wait fails; do not continue to application activation.

```bash
kubectl -n flux-system get kustomization lfce-staging-bootstrap
kubectl -n flux-system wait --for=condition=Ready kustomization/lfce-staging-bootstrap --timeout=5m
kubectl -n lfce-staging wait --for=condition=Synced sealedsecret/lfce-staging-secrets sealedsecret/ghcr-pull --timeout=2m
kubectl -n lfce-staging get sealedsecrets
kubectl -n lfce-staging get secret lfce-staging-secrets ghcr-pull
kubectl -n lfce-staging get pods,pvc
```

The last command should show no application Pods or PVCs at this stage.
The two Secrets should exist with types `Opaque` and
`kubernetes.io/dockerconfigjson`. Share only this status output, never Secret
YAML, decoded values, or `operator-credentials.PRIVATE.json`.

If decryption fails, inspect the SealedSecret status on the server and confirm
the correct controller key is still present. Do not regenerate the database
password or delete controller keys. Kyverno validates admission; the
SealedSecrets controller decrypts credentials; Flux applies the encrypted
objects from Git. These are separate responsibilities.

## Acceptance and maintenance

Require Argo Synced/Healthy, Certificate Ready, Longhorn PVCs Bound, HTTPS
`/health` and `/readyz`, successful login/logout, unauthenticated API rejection,
and one create-profile -> mock draft -> approval workflow. Confirm the contact
mailbox before accepting applications. Use an access policy for private beta.
Back up PostgreSQL AND the founder-profile PVC and test restoration before
storing valuable client data.

Current indexes: backend `sha256:0c247e953580f3adbbd06fdf93419f71a5c204662e991e9cdd684bf9a32920e5`;
frontend `sha256:31386e72decf718533af79afdf6f650fc3dee5059af9fdaa556c1cbd0ebf5a24`.
Both contain amd64/arm64 images from LFCE commit
`71059fcf5f1885d259b6bcf355985b8f9e955bc1`. Fresh scan evidence and live
admission validation are required before activation.

LFCE `scripts/export_staging.py <platform-checkout>` regenerates only the
application/migration bundles and helper. Review the public diff before pushing.
Deployed desired state is this platform bundle; merging LFCE source alone
does not update the deployment. Do not also register the private LFCE overlay.

Backend uses Recreate to avoid simultaneous writers and cross-node attachment
of the founder-profile ReadWriteOnce volume. Brief staging downtime is expected.
PVCs are protected from Argo prune; StatefulSet claims use Kubernetes' default
retention. Rollback later releases through a reviewed digest revert, considering
schema compatibility. Removing a registry entry does not stop or delete this
application; the ApplicationSet uses create-update and preserves resources.
