# Zero Trust / SOC 2 Lab — Phase 1

This phase applies a small set of real controls to the personal hybrid Kubernetes cluster without introducing a new identity platform or a large service mesh.

The goals are:

1. reduce implicit network trust between workloads;
2. reduce the blast radius of the GitOps deployment identity;
3. detect workloads which bypass the intended ingress or pod isolation boundaries;
4. create repeatable evidence that the controls are present and operating.

## Scope

Phase 1 changes only the currently registered `landing-page-service` workload and the existing Kyverno / Argo CD security baseline.

It does **not** change Cloudflare, node firewalls, SSH, the Kubernetes API endpoint, or the public administrative endpoints. Those belong to later phases because they require current runtime/provider information which is not fully represented in this public repository.

## Controls

| Zero Trust idea | Implementation | Mode | Evidence |
| --- | --- | --- | --- |
| Deny by default | `landing-page-service` default-deny ingress and egress NetworkPolicy | Enforcing when the CNI supports NetworkPolicy | `kubectl get networkpolicy -n landing-page-service -o yaml` |
| Explicit service path | Only the `traefik` namespace may reach the landing page on TCP/8080 | Enforcing when the CNI supports NetworkPolicy | connectivity test plus NetworkPolicy YAML |
| Least-privilege deployment identity | Argo `production-apps` trusts only the current platform repo and `landing-page-service` namespace | Enforcing | `kubectl -n argocd get appproject production-apps -o yaml` |
| Immutable delivery | Audit Pods using missing or `latest` image tags | Audit | Kyverno PolicyReports |
| Workload-to-node isolation | Audit host namespace sharing and privileged containers | Audit | Kyverno PolicyReports |
| No ingress bypass | Audit NodePort Services | Audit | Kyverno PolicyReports and `kubectl get svc -A` |
| Existing workload hardening | Non-root, seccomp, no privilege escalation, drop ALL capabilities and resource limits | Enforcing via existing Kyverno policies | ClusterPolicy + PolicyReport |

The new Kyverno controls intentionally start in `Audit`. Promote each one to `Enforce` only after its current PolicyReport is reviewed and legitimate exceptions are documented.

## Required pre-merge check: NetworkPolicy enforcement

Kubernetes accepts `NetworkPolicy` objects even when the installed CNI does not enforce them. Before merging this phase, identify the live CNI:

```bash
kubectl -n kube-system get pods -o wide
kubectl -n kube-system get daemonset
```

Look for the active networking implementation (for example Calico, Cilium, Antrea, or kube-router) and confirm that the installed mode supports Kubernetes NetworkPolicy.

Do not treat the presence of the API object alone as evidence of segmentation.

## Connectivity validation

After the policy is reconciled:

```bash
kubectl -n landing-page-service get networkpolicy
kubectl -n landing-page-service get pods -o wide
kubectl -n landing-page-service get svc landing-page-service
```

Validate the external path through Traefik:

```bash
curl -fsS https://pages.processlayerai.com/ >/dev/null
```

Then validate that a Pod outside the `traefik` namespace cannot connect directly to the Service. Use a temporary test Pod which satisfies the enforced Kyverno security-context and resource policies. The direct request should time out or fail while the Traefik-backed public request remains healthy.

## Kyverno evidence

```bash
kubectl get clusterpolicy
kubectl get policyreport -A
kubectl get clusterpolicy disallow-latest-tag -o yaml
kubectl get clusterpolicy disallow-host-namespaces -o yaml
kubectl get clusterpolicy disallow-privileged-containers -o yaml
kubectl get clusterpolicy disallow-nodeport -o yaml
```

Findings from the audit policies are remediation input, not automatic proof that the affected workload is malicious or misconfigured. Review the workload owner and technical requirement before creating an exception.

## Argo CD trust-boundary validation

The `production-apps` AppProject is intentionally restricted to the only application currently registered in production. When a new application is onboarded, the same review must add its exact source repository and destination namespace to the AppProject.

```bash
kubectl -n argocd get appproject production-apps -o yaml
kubectl -n argocd get applications
```

This prevents a newly registered application from automatically inheriting trust to every repository and every namespace.

## Rollback

All Phase 1 changes are GitOps-managed and reversible through Git.

If the landing page becomes unreachable after NetworkPolicy reconciliation:

1. verify that Traefik is running in namespace `traefik`;
2. verify the Service target port is TCP/8080;
3. verify the live CNI and its NetworkPolicy implementation;
4. revert `apps/landing-page-service/networkpolicy.yaml` from the app Kustomization if immediate rollback is required;
5. let Argo CD reconcile the reverted desired state.

Do not work around the policy by changing the Service to NodePort.

## Next phases

Phase 2 should protect administrative web surfaces (Argo CD, AWX, Grafana, Prometheus, Longhorn, Kubernetes Dashboard, Traefik dashboard) with an identity-aware outer control and prevent direct-origin bypass.

Phase 3 should address the hybrid node trust boundary: encrypted node-to-node transport, host firewall allowlists, Kubernetes API/kubelet exposure, SSH access, and node hardening evidence.

Phase 4 should migrate application delivery away from CI-held production kubeconfigs and toward GitOps-only deployment identities, beginning with CyberLynx Blog.

Phase 5 should centralize secret lifecycle and rotation once the preferred external secret backend is selected.
