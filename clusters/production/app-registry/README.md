# Production App Registry

Each `*.app.yaml` file in this directory creates one Argo CD Application
through `clusters/production/argocd-apps/applicationset.yaml`.

Adding a registry file does not require cloning a repository onto the cluster
server. Create the application manifests and this file through a reviewed
GitHub pull request.

Example:

```yaml
app:
  name: example-api
  repoURL: https://github.com/TheDivine/example-api.git
  revision: main
  path: deploy/overlays/production
  namespace: example-api
```

Requirements:

- `name` must be unique and valid as a Kubernetes resource name.
- `repoURL` must be allowed by the `production-apps` AppProject.
- `revision` should be a protected branch, release tag, or immutable commit.
- `path` must contain valid plain YAML, Kustomize, Helm, or Jsonnet content.
- `namespace` is created automatically when it does not exist.
- Private repositories must be registered with Argo CD before merging the
  registry entry.

Safety:

- Pull requests that add registry files require infrastructure-owner review.
- The ApplicationSet may create and update Applications but does not
  automatically delete them when a registry file disappears.
- Removing an application is a separate, deliberate decommissioning workflow.
