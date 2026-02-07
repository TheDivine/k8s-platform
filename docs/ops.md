# Platform Ops Guide

This guide explains how to apply and maintain the platform components tracked in this repo.

## Prerequisites
- `kubectl` configured with the target cluster context
- `helm` installed (if you use Helm-based components)
- Access to your DNS provider (for external-dns or manual DNS entries)

## Recommended Order of Operations
1. Storage (provisioners, storage classes)
2. Networking tools (iperf, diagnostics)
3. Ingress controller (Traefik)
4. MetalLB (if on bare metal)
5. Monitoring stack (Prometheus/Grafana)
6. Admin tools (K8s Dashboard)
7. CI/CD (Drone or other tools)

## Storage
Manifests live in `infra/storage/`.

Apply:
```bash
kubectl apply -f infra/storage/local-path-storage.yaml
kubectl apply -f infra/storage/nfs-provisioner.yaml
kubectl apply -f infra/storage/local-storage-provisioner.txt
```

Verify:
```bash
kubectl get storageclass
kubectl get pods -A | grep -i provisioner
```

## Networking Tools
Manifests live in `infra/networking/`.

Apply:
```bash
kubectl apply -f infra/networking/iperf-client.yaml
kubectl apply -f infra/networking/iperf-server.yaml
kubectl apply -f infra/networking/revere-iperf.yaml
kubectl apply -f infra/networking/server-revere-iperf.yaml
```

Verify:
```bash
kubectl get pods -A | grep -i iperf
```

## Ingress Controller (Traefik)
Traefik manifests are currently located inside the app repo (if you standardize, move them to `platform/traefik/`).

If you have Traefik manifests under `platform/traefik/`:
```bash
kubectl apply -f platform/traefik/
```

If you use Helm:
```bash
helm repo add traefik https://helm.traefik.io/traefik
helm repo update
helm install traefik traefik/traefik -n traefik --create-namespace
```

Verify:
```bash
kubectl get pods -n traefik
kubectl get svc -n traefik
```

## MetalLB
If you run on bare metal, apply MetalLB.

If you later centralize MetalLB under `platform/metallb/`:
```bash
kubectl apply -f platform/metallb/
```

Verify:
```bash
kubectl get pods -n metallb-system
```

## Monitoring
Manifests live in `platform/monitoring/`.

Apply:
```bash
kubectl apply -f platform/monitoring/values-kube-prometheus.yaml
kubectl apply -f platform/monitoring/prometheus-ingress.yaml
kubectl apply -f platform/monitoring/grafana-ingress.yaml
kubectl apply -f platform/monitoring/longhorn-ingress.yaml
```

Verify:
```bash
kubectl get pods -n monitoring
kubectl get ingress -n monitoring
```

## K8s Admin Dashboard
Manifests live in `platform/k8s-admin/`.

Apply:
```bash
kubectl apply -f platform/k8s-admin/
```

Verify:
```bash
kubectl get pods -n kubernetes-dashboard
kubectl get svc -n kubernetes-dashboard
```

## Drone CI
Manifests live in `platform/drone-ci/`.

Apply:
```bash
kubectl apply -f platform/drone-ci/postgres/
kubectl apply -f platform/drone-ci/server/
kubectl apply -f platform/drone-ci/runner/
```

Verify:
```bash
kubectl get pods -n drone
kubectl get svc -n drone
```

## Rollback Strategy
- Prefer Git-based rollbacks: revert commits and re-apply.
- For Helm, use `helm rollback <release> <revision>`.

## Troubleshooting Checklist
- Check resource status: `kubectl get pods -A`
- Inspect events: `kubectl get events -A --sort-by=.lastTimestamp`
- Check ingress: `kubectl get ingress -A`
- Validate storage classes: `kubectl get storageclass`
