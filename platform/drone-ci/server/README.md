# Drone Server Secrets

`droneserver-secret.example.yaml` is an example only. It documents the keys expected by the Drone server deployment, but it must not be applied as-is and must never contain real secrets in public Git.

Create real Drone secrets through one of these approaches:

- SOPS-encrypted Kubernetes Secret manifests.
- SealedSecrets.
- ExternalSecrets backed by a real secret manager.
- Manual `kubectl create secret ...` commands outside Git.

Generate high-entropy shared secrets locally:

```bash
openssl rand -hex 32
```

Use generated values for `DRONE_RPC_SECRET` and any other shared secret. GitHub or Gitea OAuth client IDs and client secrets must be stored outside public Git. Database usernames and passwords should come from a secret manager, SOPS/SealedSecrets, or another approved private secret workflow.

The deployment references the Kubernetes Secret named `drone-server-secret`. The example file keeps that name so the shape is clear, but the real Secret should be created by the private secret-management flow used for the cluster.

TODO: choose the long-term secret workflow for Drone CI: SOPS, SealedSecrets, ExternalSecrets, or manual break-glass creation.
