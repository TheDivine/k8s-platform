# SOP: ImagePullBackOff

This SOP documents a safe diagnostic pattern for image pull failures.

## Diagnosis

1. Identify the namespace, workload, container name, image, node, and event message.
2. Determine if the failure is registry auth, DNS, tag not found, rate limit, TLS, or architecture mismatch.
3. Check whether the image tag is pinned and still published.
4. Avoid changing manifests until the correct image source is known.

## Safe Host-Side Test

On the affected node:

```bash
crictl pull IMAGE_REFERENCE
```

Replace `IMAGE_REFERENCE` with the exact image from the pod event.

## GitOps Fix Pattern

- Patch Git, not the cluster, when a workload is managed by Argo CD or Flux.
- Use an explicit image tag.
- Document why the registry or tag changed.
- Let GitOps reconcile after review.

TODO: Add controller-specific examples for Argo CD and Flux ownership paths.
