# Kasm Kubernetes Scaffold

This app directory prepares a Kubernetes-native GitOps scaffold for Kasm Workspaces in the home lab. It is not a complete production deployment yet: it defines the namespace, storage placeholders, Traefik ingress placeholders, example secret shape, and documentation needed before introducing the official Kasm Kubernetes deployment.

The current migration goal is to keep the old host-managed Docker Compose Kasm stack disabled and introduce Kasm on Kubernetes from scratch. The previous `/opt/kasm` installation should be treated as migration source material only until the Kubernetes deployment has been validated.

## Target Components

- Kasm web, proxy, and API layer exposed through Kubernetes services.
- Database layer for application state and user/workspace metadata.
- Redis session and cache layer.
- Guacamole, RDP, and websocket-related services required by browser-based workspace access.
- Workspace runtime, agent, or worker concept for launching user sessions.
- Traefik ingress through `IngressRoute` on the `websecure` entry point.
- Persistent storage through `local-path` by default, with Longhorn available later by changing PVC `storageClassName` values.

Exact upstream Kasm Kubernetes deployment details must be validated before any production apply. Do not add guessed Kasm container images, deployment arguments, database schemas, or runtime permissions here without confirming the official Kasm manifests or Helm chart for the target version.

## Deployment Phases

1. Phase 0: stop the old Docker Compose Kasm stack.
2. Phase 1: back up the old `/opt/kasm` configuration, certificates, Docker Compose files, and relevant runtime data.
3. Phase 2: scaffold the Kubernetes namespace, storage, secrets strategy, and Traefik ingress placeholders.
4. Phase 3: install the official Kasm Kubernetes manifests or Helm chart after validating upstream requirements.
5. Phase 4: expose Kasm through Traefik using the final hostname, TLS settings, and websocket-safe route configuration.
6. Phase 5: validate login, admin access, workspace image pulls, workspace launch, remote desktop/websocket behavior, persistence, and logs.
7. Phase 6: archive and then remove the old `/opt/kasm` data only after successful Kubernetes validation and a rollback window.

## GitOps Notes

The Flux wiring in `flux/apps/kasm/kustomization.yaml` is suspended by default. Enable it only after replacing placeholder hostnames, replacing the example secret with a real secret management flow, and adding the official Kasm deployment resources.

