# SOP: Kubernetes Node Validation

This SOP validates a Kubernetes node from the host side without requiring `kubectl`.

## Commands

```bash
infra-security/scripts/check-node-health.sh
infra-security/scripts/check-container-runtime.sh
infra-security/scripts/collect-k8s-node-status.sh
```

## Checks

- `containerd` is installed and active.
- `kubelet` is active when the node is joined to a cluster.
- `crictl` can connect to the runtime.
- `/etc/crictl.yaml` points to containerd.
- `br_netfilter` is available.
- `net.bridge.bridge-nf-call-iptables` is `1`.
- `net.ipv4.ip_forward` is `1`.
- Swap is disabled for Kubernetes nodes.

## Manual Review

- Confirm kernel version and CNI compatibility.
- Confirm node labels and taints after joining the cluster.
- Confirm Longhorn or local storage requirements before scheduling stateful workloads.

TODO: Add a cluster-side validation SOP after GitOps ownership is finalized.
