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
