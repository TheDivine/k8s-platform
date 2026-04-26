# Apps

This directory is for application deployment surfaces and public-safe app scaffolds.

Tracked app content should be clean, documented, and deployable through GitOps. Local application workspaces may remain nested here for development, but they should stay ignored until they are sanitized and given a clear public deployment boundary.

Use `apps/kasm` as the current scaffold pattern:

- app README
- app docs
- namespace and storage placeholders
- Kustomize base and overlays
- placeholder-only secret examples
- suspended GitOps wiring until validated

Do not commit real `.env` files, nested `.git` directories, dependency folders, runtime uploads, logs, database files, or real secrets.
