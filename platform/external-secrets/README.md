# External Secrets

This directory contains a staged External Secrets Operator migration.

It is not referenced by the production cluster Kustomization because no
external secret backend or `ClusterSecretStore` has been approved. Adding it
to production before that decision would install an idle controller and create
an incomplete ownership model.

The controller is pinned to the official chart `2.6.0`. Example
ExternalSecrets use placeholder logical paths and are not included in a
Kustomization.

Read:

- `docs/external-secrets-migration.md`
- `docs/credential-access.md`
- `docs/secret-management.md`
