# Kasm Security Notes

Do not expose the Kasm admin UI publicly without additional protection. Prefer VPN access, private DNS, IP allowlists, or another trusted access layer for administrative paths.

Use Traefik middleware for secure headers, compression, and future access controls. Validate framing requirements before enabling strict frame protections because remote desktop and browser workspace flows may need embedded content.

Use a strong generated admin password. Do not store real passwords, tokens, license keys, or private values in plain Git.

Manage Kubernetes secrets through SOPS, SealedSecrets, ExternalSecrets, or a manual break-glass process. The checked-in example secret is documentation only.

Add NetworkPolicies later to restrict database, Redis, control-plane, and workspace runtime communication after the official service labels and ports are known.

Separate workspace runtime permissions from the Kasm control plane. Workspace launchers should not receive broad cluster permissions unless official Kasm documentation requires them and the risk is accepted.

Back up the database and persistent Kasm data. Test restore steps before deleting `/opt/kasm` or treating the Kubernetes deployment as the only source of truth.

