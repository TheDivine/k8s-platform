# Platform And Application Status

Last verified from Git and the production cluster on 2026-06-07.

This document separates four states that must not be confused:

- **GitOps managed**: a controller continuously reconciles the resource from Git.
- **Running but unmanaged**: the workload exists, but Git is not its confirmed
  source of truth.
- **Scaffolded**: files exist in Git but are intentionally not deployed.
- **Broken or incomplete**: an action is required before the component should be
  treated as production-ready.

## GitOps Controllers

| Component | Current state | Owner | Required work |
| --- | --- | --- | --- |
| Flux | Running and reconciling `main` | Bootstrap GitOps controller | Keep as owner of `clusters/production` and network automation |
| Argo CD | Controller and production ApplicationSet are healthy | Flux bootstraps Argo configuration; Argo owns registered apps | Add reviewed app registry entries as applications are onboarded |
| Production app registry | Deployed and intentionally empty | Argo CD ApplicationSet | Onboard the first application after checking live-versus-Git drift |
| Weave GitOps UI | Running | Flux HelmRelease | Replace `flux.example.com` or remove the public route |

The old empty `platform` and `infra` Applications were removed on 2026-06-07.
The production ApplicationSet now reads
`clusters/production/app-registry/*.app.yaml`. No Application is generated
until a reviewed registry file exists.

## Network And Edge

| Component | Current state | Owner | Required work |
| --- | --- | --- | --- |
| Traefik | Running from Helm | Manual Helm history | Move the Helm release into one GitOps owner before changing it |
| MetalLB | Running | Unclear/manual | Capture its active configuration in a reviewed GitOps package |
| ExternalDNS | Ready | Flux HelmRelease | Continue using explicit zone filters and `upsert-only` |
| cert-manager | Ready; both ClusterIssuers Ready | Flux HelmRelease | Migrate routes from Traefik ACME one hostname at a time |
| Cloudflare | Active for managed public routes | ExternalDNS plus manual provider records | Keep mail, wildcard, and legacy records outside automatic deletion |

## Platform Services

| Component | Current state | Git representation | Required work |
| --- | --- | --- | --- |
| Monitoring | Running Helm release | Partial values and ingress manifests | Move the full Helm release to one GitOps controller |
| Longhorn | Running Helm release | Only UI ingress is represented | Add reviewed Helm desired state and backup policy |
| Kubernetes Dashboard | API/auth/web are running; Kong is in `CrashLoopBackOff` | Several competing historical manifests | Diagnose Kong, select one canonical package, archive alternatives |
| AWX | Running through AWX Operator | Not represented as a complete GitOps package | Export only the desired operator/CR configuration, excluding secrets |
| Drone | Server and runner running | Partial manifests | Add Kustomize or Helm ownership and move credentials to External Secrets |
| External Secrets | Controller package staged, not installed | Complete controller package and examples | Select a backend and authentication method before enabling |
| MinIO and Velero | Manifests and runbooks exist | Scaffold/manual package | Verify live installation, backup schedules, restore test, and credentials |
| Metrics Server | Deployment scaled to zero | Not clearly owned | Decide whether to repair and enable it or remove it |

## Applications

| Application | Current state | Source location | Required work |
| --- | --- | --- | --- |
| CyberLynx Blog | Running in `websites` | Separate local Git repo at `apps/CyberLynxBlog`, remote `TheDivine/CyberLynxBlog` | Onboard its `k8s` path through the Argo registry after reviewing the image change it would apply |
| CyberLynx content | Runtime content source, not a Kubernetes app | Separate repo `TheDivine/Cybelynx-blog-content` | Keep separate; publishing content should not create an Argo Application |
| Law firm | Running in `law-firm` | Separate application repository | Add it to Argo only after its production overlay and secret boundary are reviewed |
| Kasm | Scaffolded and suspended | Tracked under `apps/kasm` | Add official supported Kasm resources, real secret flow, final hostname, and tests |
| Kwiki/Qwiki | Incomplete; Flux source has historical failure status | Local repo remote is `TheDivine/qwiki`, while Flux references `TheDivine/kwiki` | Choose the correct repository, sanitize the deployment path, then use either Argo or Flux, not both |
| Hello Node | Running diagnostic workload | No canonical tracked package found | Add a small GitOps package or remove the test workload |
| Whoami | Running diagnostic workload | Local Kwiki/Qwiki workspace contains related files | Move to a clean tracked test app or remove public exposure |
| Wikimedia Helm test | Incomplete chart experiment | `apps/helmtest/wikimeida` | Correct naming and add templates, or archive/remove it |

Nested application repositories under `apps/` are local workspaces. Their
contents are not pushed as part of `k8s-platform` because each contains its own
`.git` directory. The only tracked application deployment scaffold currently
under `apps/` is Kasm.

## Operational Problems

The following live problems were still visible during the latest 2026-06-07
inventory:

- Six recent `law-firm-postgres-backup` pods were in `Error`.
- Kubernetes Dashboard Kong was not available.
- The Flux UI still used `flux.example.com`.
- Several running Helm releases had no declarative GitOps owner.
- The default Argo `AppProject` allowed every source repository, destination,
  and cluster-scoped resource. New production apps use the restricted
  `production-apps` project, but the default project should remain unused or
  be restricted.
- Administrative endpoints remain internet-facing without Cloudflare Access
  and direct-origin filtering.
- Human-managed secrets still live directly in Kubernetes until an External
  Secrets backend is selected.

Address backup failures first because a backup job that exists but fails can
create false confidence.

## Recommended Order

1. Repair the law-firm PostgreSQL backup job.
2. Diagnose Kubernetes Dashboard Kong.
3. Replace or remove the Flux UI placeholder route.
4. Put administrative endpoints behind Cloudflare Access and restrict the
   origin to Cloudflare traffic.
5. Onboard CyberLynx Blog as the first real Argo-managed app.
6. Select an External Secrets backend and migrate human-managed credentials.
7. Restrict or stop using the broad default Argo AppProject.
8. Move monitoring, Traefik, Longhorn, and other Helm releases into explicit
   GitOps ownership one release at a time.
9. Decide whether to repair or remove Kwiki/Qwiki, Hello Node, Whoami, and the
   Wikimedia chart experiment.
