# ProcessLayer registry credentials

Flux owns the image-pull credentials; application overlays reference their names through GitOps. The existing production Secret is `processlayer-registry-pull` in `processlayer-prod`.

The helper accepts only a hidden, interactive TheDivine classic token with exactly `read:packages`. It verifies the fixed reviewed image digests over TLS, refuses redirects, and writes strictly namespace-bound SealedSecret ciphertext. It never performs Docker login, Git writes, or cluster changes. Existing output is never overwritten.

For staging, run `python3 prepare_registry_credential.py --cert <trusted-public-cert> --namespace processlayer`. This writes `staging-processlayer-registry-pull.sealed.json`, with the same Secret name in namespace `processlayer`, preserving the production file. Do not copy production ciphertext into staging: strict sealing binds it to its namespace and name.

Staging repair is prepared because GHCR rejected the legacy `ghcr-pull` credential while pulling the v0.2.4 API image. After the operator creates the new ciphertext, validate it, add it to this package's resources, and add a staging Application prerequisite annotation. Merge the platform change and observe the annotation only after this Flux package reports all SealedSecrets Synced. Then merge the application imagePullSecrets change. Keep production notification activation gated on staging enquiry persistence and actual inbox delivery.

Normal rotation follows the same reviewed process with a new output location; do not overwrite credentials through Argo UI or direct Kubernetes patches.
