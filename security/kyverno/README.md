# Kyverno — Kubernetes Policy Engine

## Structure

```
kyverno/
├── controller/     ← HelmRelease installs Kyverno + CRDs
│   ├── namespace.yaml
│   ├── helm-repository.yaml
│   └── helm-release.yaml
├── policies/       ← ClusterPolicies (applied AFTER controller)
│   ├── require-non-root.yaml
│   ├── require-resources.yaml
│   └── require-security-context.yaml
└── kustomization.yaml
```

## Flux deploys in order

1. `kyverno-controller` — installs Kyverno + CRDs
2. `kyverno-policies` — applies policies (depends on controller)

## Verify

```bash
kubectl get clusterpolicy
kubectl -n kyverno get pods
kubectl get policyreport -A | grep -v Pass
```

## App-Specific Policies

ProcessLayer-specific policies (GHCR registry restriction) live in:
`github.com/TheDivine/processlayer-ai/infra/k8s/policies/`

## Longhorn policy boundary

The three generic Pod hardening policies exclude only the `longhorn-system`
namespace. Longhorn manager, CSI, instance-manager, upgrade, and helper Pods
legitimately require combinations of root, privilege, host access, mount
propagation, or chart-managed resource settings that are incompatible with
these generic rules.

This exception does not disable Kyverno, does not change enforcement mode, and
does not exempt application namespaces. Other current or future policies still
apply to `longhorn-system` unless they declare their own reviewed exception.

Run the boundary checks with a pinned Kyverno CLI:

```bash
kyverno apply security/kyverno/policies \
  --resource security/kyverno/tests/longhorn-system-pods.yaml
kyverno apply security/kyverno/policies \
  --resource security/kyverno/tests/application-noncompliant-pod.yaml
kyverno apply security/kyverno/policies \
  --resource security/kyverno/tests/application-compliant-pod.yaml
```

Expected results are zero failures for the excluded Longhorn fixtures, three
failures for the noncompliant application Pod, and three passes for the
compliant application Pod.
