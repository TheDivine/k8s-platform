# LFCE staging activation approval

## Approval boundary

This change is prepared for review, not permission to deploy. Keep the PR in
draft and do not merge until the owner explicitly approves staging deployment.
Merging the app-registry entry lets the existing ApplicationSet create LFCE and
Argo auto-sync its resources. No manual Argo sync or direct workload apply is
needed. Flux continues to own only the namespace and encrypted secrets.

## Evidence and scope

- Operator confirmed Flux bootstrap Ready at platform commit 97ab0a6 and both
  SealedSecrets Synced, with the two generated Secrets present.
- Operator confirmed manifest server dry-runs and all six Pod admission
  dry-runs passed. Those checks used the previous image pins.
- Only application image fields change within the workload/migration bundles;
  storage, security contexts, resource requests, networking and credentials
  are unchanged. Recheck admission if live policies have changed.
- LFCE source PR #44 merged as 074fc933c3aefabeb71d6ba85c86588cfff12164.
- [Publication run 35922283349](https://github.com/TheDivine/lfce_app/actions/runs/35922283349)
  successfully built and scanned both exact image indexes and promoted aliases.
  The existing gate checks fixable HIGH/CRITICAL vulnerabilities on amd64;
  it is not an all-platform or zero-vulnerability guarantee.
- The database/cache images and protected Longhorn volumes remain unchanged.
- No unrelated application, AppProject, Kyverno policy or secret is modified.
- Local verification: semantic comparison confirms exactly four image-field
  replacements and no other workload changes; Kustomize renders 18 application,
  one migration, three bootstrap and 15 root platform resources. The rendered
  workloads pass LFCE's container admission contract, and the registration is
  allowed by the current AppProject. Whitespace checks pass.
- New image pulls, final admission under live policies, storage attachment,
  controller reconciliation, migration and application health are not yet
  verified. The owner's prior credential check covered the same GHCR packages.
- Mock providers and a single operator remain the product boundary. No billing,
  client logins, external AI calls or automatic social publishing are enabled.

## Before approving

### Observed first-rollout issues

The owner confirmed Traefik runs in namespace `traefik`, not `kube-system`.
The original frontend/backend ingress peers therefore did not allow this
controller. This repair replaces those two namespace selectors only; default
deny, internal backend access, database/cache rules and ports remain intact.
Frontend loopback GET /login returned 200 while public HTTPS returned 504.
Certificate issuance completed successfully; do not weaken Cloudflare TLS.
After the approved repair merge, retest public /login, /health and /readyz.
Admission dry-runs and Ready Pods do not establish cross-Pod connectivity.

The worker's PostgreSQL 42P01 error (`generation_jobs` does not exist) is a
separate first-migration issue. Backend liveness and database connectivity can
pass before schema initialization. Run the migration below once; do not recreate
PostgreSQL, rotate credentials or delete volumes. After Job completion, inspect
recent worker logs for new errors, not only historical pre-migration entries.

Offline policy regression checks (Python 3 with PyYAML):

```bash
python3 -m unittest discover -s apps/lfce-staging -p 'test_*.py'
```

These assert policy structure, not live CNI enforcement. The source LFCE overlay
also retains the old ingress namespace; do not overwrite the reviewed platform
bundle with an unreviewed source export.

Review this PR's diff and its local validation evidence. The platform repository
has no automated PR checks; source image CI is separate evidence. Confirm the
server is still the intended cluster and credentials have not been rotated:

```bash
kubectl config current-context
kubectl -n flux-system get kustomization lfce-staging-bootstrap
kubectl -n lfce-staging get sealedsecrets
kubectl -n lfce-staging get secret lfce-staging-secrets ghcr-pull
kubectl -n lfce-staging get pods,pvc
```

Unexpected existing LFCE workloads or data require review, not deletion. The
initial database configuration assumes new LFCE PVCs. No secret values need
to be shared. Keep operator-credentials.PRIVATE.json private and backed up.

## After the approved merge

1. Allow a few minutes for ApplicationSet discovery. Confirm the Application
   points to this platform repository, path apps/lfce-staging, revision main.

```bash
kubectl -n argocd get application lfce-staging
kubectl -n lfce-staging get pods,pvc
kubectl -n lfce-staging rollout status statefulset/lfce-postgres --timeout=5m
```

Stop if PostgreSQL fails readiness. Inspect Pod events and PVC status; do not
delete volumes or change database passwords. Backend readiness is not proof
that the initial schema migration has completed.

2. Use a new checkout directory on the server (or an existing clean checkout
   updated with git pull --ff-only). Confirm the checkout contains the approved
   deployment merge before applying the migration.

```bash
git clone --branch main https://github.com/TheDivine/k8s-platform.git ~/lfce-staging-deploy
cd ~/lfce-staging-deploy
git log -1 --oneline
kubectl apply --dry-run=server -k apps/lfce-staging/migration
```

Only after that dry-run succeeds, apply the one-time migration:

```bash
kubectl apply -k apps/lfce-staging/migration
kubectl -n lfce-staging wait --for=condition=complete job/lfce-migrate --timeout=5m
kubectl -n lfce-staging logs job/lfce-migrate
```

Stop if the Job fails. Do not delete/recreate it or retry blindly. Migration
is deliberately excluded from normal Argo reconciliation.

3. Verify workloads and the public route:

```bash
kubectl -n lfce-staging rollout status deployment/lfce-backend --timeout=5m
kubectl -n lfce-staging rollout status deployment/lfce-worker --timeout=5m
kubectl -n lfce-staging rollout status deployment/lfce-frontend --timeout=5m
kubectl -n lfce-staging get pods,pvc,certificate,ingress
kubectl -n argocd get application lfce-staging
curl -fsS https://lfce-app.xn--cyberlnx-ykb.com/health
curl -fsS https://lfce-app.xn--cyberlnx-ykb.com/readyz
curl -I https://lfce-app.xn--cyberlnx-ykb.com/login
```

Expected: Argo Synced/Healthy, Pods Ready, PVCs Bound and Certificate Ready.
ExternalDNS requests the proxied Cloudflare record targeting 69.30.233.178.
cert-manager uses letsencrypt-production-cloudflare for trusted origin TLS.
DNS and certificate reconciliation are independent; check their actual status
instead of assuming an Argo sync proves HTTPS works. Do not create duplicates
manually or weaken TLS if issuance fails.

4. Log in with the dashboard email/key from the private credentials file.
Create a test Founder Profile, generate a mock draft, approve it and log out.
Confirm unauthenticated private API requests are rejected. Back up PostgreSQL
and the founder-profile PVC and test restoration before storing client data.

## Rollback and stop conditions

Before merge, keeping the PR unmerged is sufficient to prevent activation.
After merge, removing the registry entry alone does NOT stop/delete the app:
ApplicationSet uses create-update and preserves resources on deletion. A
rollback or suspension then needs a separately reviewed GitOps change. Do not
delete the Namespace, secrets or PVCs, and do not roll back to an image rejected
by the security gate. Schema compatibility must be considered after migration.
