# Kyverno — Kubernetes Policy Engine

## What Kyverno Does

Kyverno enforces security policies at admission time. When you `kubectl apply` a Pod, Kyverno checks it against these policies BEFORE the Pod is created. If the Pod violates a policy, it's blocked.

## Policies (Cluster-wide, enforced)

| Policy | Scope | What It Blocks |
|--------|-------|---------------|
| `require-non-root` | All namespaces (except kube-system, cert-manager, flux-system, argocd, kyverno) | Root containers |
| `require-resources` | All namespaces (same exceptions) | Pods without CPU/memory limits |
| `require-security-context` | All namespaces (same exceptions) | Missing seccomp + caps drop |

## How to Deploy

Flux auto-deploys from `clusters/production/kyverno.yaml` which watches this directory.

```bash
# Check policies loaded
kubectl get clusterpolicy

# Check violations
kubectl get policyreport -A | grep -v Pass
```

## Adding New Policies

1. Create `.yaml` file in this directory
2. Add to `kustomization.yaml` resources list
3. Commit + push
4. Flux syncs within 10 minutes

## App-Specific Policies

ProcessLayer-specific policies (GHCR registry restriction) live in:
`github.com/TheDivine/processlayer-ai/infra/k8s/policies/`
