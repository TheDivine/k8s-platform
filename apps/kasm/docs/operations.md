# Kasm Operations

These commands are intended for the future Kubernetes-native Kasm deployment. Some resources will not exist until the official Kasm manifests or Helm chart are installed.

## Inspection

```bash
kubectl get ns kasm
kubectl get all -n kasm
kubectl get pvc -n kasm
kubectl describe ingressroute -n kasm kasm
kubectl logs -n kasm deploy/kasm-web
```

For broad troubleshooting after workloads are added:

```bash
kubectl get events -n kasm --sort-by=.lastTimestamp
kubectl describe pod -n kasm <pod-name>
kubectl logs -n kasm <pod-name>
kubectl logs -n kasm <pod-name> -c <container-name>
```

## Troubleshooting

DNS: confirm the final Kasm hostname resolves to the MetalLB address used by Traefik.

Traefik route: verify the `IngressRoute`, entry point, middleware references, backend service name, backend port, and namespace.

TLS: confirm whether the deployment uses a Traefik certResolver, cert-manager secret, or manually managed TLS secret. Do not enable production access with placeholder TLS settings.

PVC pending: check the selected `storageClassName`, provisioner health, node capacity, access mode, and Longhorn replica requirements if Longhorn is used.

Workspace pods failing: inspect pod events, service account permissions, image pulls, runtime class requirements, node selectors, resource limits, and Kasm agent/worker logs.

Websocket or remote desktop issues: check Traefik logs, websocket upgrade behavior, forwarded headers, backend TLS verification, idle timeouts, and whether Kasm requires additional proxy annotations or middleware.

Image pull errors: verify registry credentials, upstream Kasm image names and tags, image pull policies, network egress, and node DNS.

