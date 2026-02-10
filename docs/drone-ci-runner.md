# Drone CI Runner (Required for Pipelines)

Your Drone server is running, but pipelines will not execute unless a **runner** is deployed and connected.

## Why a runner is required

- Drone server provides the UI, webhooks, scheduling, and pipeline orchestration.
- A runner executes the steps (build, test, docker build, etc.).

In your cluster, the recommended option is the **Kubernetes runner**.

## Current manifests

Runner manifests live in:
- `platform/drone-ci/runner/dronerunner-rbac.yaml`
- `platform/drone-ci/runner/dronerunner.yaml`

The runner is configured to talk to the Drone server via the internal service:
- `DRONE_RPC_HOST=droneserver.drone.svc.cluster.local`
- `DRONE_RPC_PROTO=http`

It reads `DRONE_RPC_SECRET` from:
- Secret `drone/drone-server-secret`

## Deploy the runner

```bash
kubectl apply -f platform/drone-ci/runner/dronerunner-rbac.yaml
kubectl apply -f platform/drone-ci/runner/dronerunner.yaml
kubectl -n drone get pods
```

You should see a pod like:
- `drone-runner-...` Running

## Verify runner connectivity

1. Check logs:
```bash
kubectl -n drone logs deploy/drone-runner --tail=200
```

2. Trigger a pipeline run from Drone UI:
- `https://drone.kwiki.it.com`

## Security note

`platform/drone-ci/server/droneserver-secret.yaml` contains plaintext credentials. That is not a good long-term practice.
Recommended next step:
- Replace it with a `*.template.yaml` and manage secrets via SOPS or External Secrets.

