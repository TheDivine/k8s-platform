# Manual Deploy Checklist

Use this when GitOps is not yet installed or when you need to troubleshoot manually.

## 1) Confirm Context
```bash
kubectl config current-context
kubectl get nodes -o wide
```

## 2) Apply Platform/Infra Manifests
```bash
kubectl apply -f platform/
kubectl apply -f infra/
```

## 3) Deploy App Manifests
For apps with Kustomize folders:
```bash
kubectl apply -k <app-repo>/k8s/
```

## 4) Validate Deployments
```bash
kubectl get pods -A
kubectl get svc -A
kubectl get ingress -A
```

## 5) Rollback (Manual)
- Revert to the previous manifest version
- Re-apply with `kubectl apply -f ...`

## 6) Cleanup / Prune
If you removed resources:
```bash
kubectl delete -f <manifest-path>
```

## 7) Secrets Handling
- Do NOT store real secrets in Git
- Use templates in Git and apply real secrets manually or via External Secrets

## 8) Log Collection
```bash
kubectl -n <ns> logs <pod>
```

## 9) Common Mistakes
- Wrong namespace
- Wrong context
- Missing CRDs
- Traefik ingress uses incorrect entrypoint or certResolver
