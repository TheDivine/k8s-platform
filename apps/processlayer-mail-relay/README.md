# ProcessLayer outbound relay candidate

Prepared 22 September 2026; NOT registered with Argo/Flux and NOT deployed.
There is no change to the website, existing MX or Hestia SMTP routing in this PR.

Owner preflight reports the bare-metal hostname label
`s231226.wholesaleinternet.net`, Ready, internal IP 10.200.0.1; Oracle is
`hcp.kwiki.it.com`, 10.200.0.2. Longhorn is available/default and TCP587 has no
listener. Host TCP25 to two Gmail MX servers previously passed. Pod egress and
Internet reachability to 587 are still unverified.

Candidate built and tested by:
https://github.com/TheDivine/landing-page-service/actions/runs/35712280837
Source commit: 2ef1571d5c8b76eebc0791e9444d70108c69443c.
Nine isolated TLS/authentication/sender/queue checks passed; no external mail.
Image is digest-pinned in resources.yaml, in the existing private package.

## Architecture

Hestia domain relay -> smtp.processlayerai.com:587 STARTTLS + dedicated login ->
non-root Exim pod port1587/hostPort587 on the bare-metal node -> recipient MX25.
One replica, Recreate rollout, Longhorn persistent queue, no service-account
token, no privilege escalation, read-only root and no Linux capabilities.
The PVC is marked Prune=false; never delete it to clear or restart a queue.

Certificate uses the existing production Cloudflare DNS-01 ClusterIssuer.
Mounted certificate changes trigger Exim SIGHUP via the packaged wrapper.
Renewal detection is implemented; actual cluster rotation remains an acceptance check.
No shared Traefik entrypoint or HTTP Ingress is changed. ExternalDNS currently
watches ingress/traefik sources, so this hostPort app does not automatically
create its A record. Publish DNS-only smtp A and relay DKIM TXT from the helper.

Only authenticated TLS submissions with envelope/header From
dalibor@processlayerai.com are accepted. No inbound mailbox or arbitrary
forwarding service is provided. Null envelope submissions are rejected;
Exim-generated local delivery failures are distinct internal bounce traffic.
Verify bounce routing to the Oracle MX during acceptance. No blanket trusted
network is configured. Source-IP filtering must be added only after verifying
the address preserved by Calico hostPort; never trust a broad node/pod subnet.

## One-time private bootstrap

Run platform/app-bootstrap/processlayer-mail-relay/prepare_credentials.py on
the bare-metal admin host. It uses the existing landing-page GHCR Secret,
generates a dedicated SMTP password and new relay DKIM key, and encrypts both
strictly for namespace processlayer-mail-relay using the existing controller.
It performs no apply, DNS edit, mail send or Hestia change.

Return ONLY relay-bootstrap.sealed.json and dns-records.json from its new
private output directory. Keep hestia-settings.PRIVATE.json on the server.
The output folder is 0700, files 0600. Never paste the private file or raw Secret.
Do not rerun after successful generation: reuse the same output to avoid mismatched passwords.

Validate encrypted names relay-auth and relay-ghcr-read in the exact namespace,
then add relay-bootstrap.sealed.json to the bootstrap kustomization. Only then:

1. Add a Flux Kustomization following clusters/production/landing-page-bootstrap.yaml,
   with name processlayer-mail-relay-bootstrap and path
   ./platform/app-bootstrap/processlayer-mail-relay; include it in production kustomization.
2. Add clusters/production/app-registry/processlayer-mail-relay.app.yaml with:

```yaml
app:
  name: processlayer-mail-relay
  repoURL: https://github.com/TheDivine/k8s-platform.git
  revision: main
  path: apps/processlayer-mail-relay
  namespace: processlayer-mail-relay
```

Adding those registrations and merging activates automated deployment. This
preparation deliberately has neither registration. Do not manually apply the
Deployment or change unrelated cluster resources.

## Acceptance before Hestia cutover

Verify SealedSecret Synced, PVC Bound, Certificate Ready, image pull, pod Ready,
actual egress IP69.30.233.178 and Gmail MX25 reachability from the pod. From Oracle,
verify TCP587/TLS hostname and authentication rejection with no credentials;
use the generated credentials only through TLS. Confirm unauthorized sender
rejection and inspect source-IP preservation before adding a narrow allowlist.

Request provider PTR69.30.233.178 -> smtp.processlayerai.com where supported;
do not rename either node. Until then the existing PTR differs from relay EHLO.
Publish new DKIM selector relay without replacing Hestia selector mail.
At controlled cutover update the single SPF record to authorize actual relay
egress (relay-only: v=spf1 ip4:69.30.233.178 -all). Preserve other intentionally
used senders if any are discovered. Keep MX pointing to Oracle.

Use Hestia Edit Mail Domain -> processlayerai.com -> SMTP Relay, with generated
host, port587, username/password. Do not set Global SMTP. Before client use,
send one owner-authorized controlled test, inspect Gmail SPF/DKIM/DMARC results,
reply back to Hestia, and verify queue persistence, bounce behavior and TLS reload.
No campaign-sender switch is authorized; the reviewed Gmail campaign continues separately.

Monitor /var/spool/exim4/log/mainlog and paniclog plus queue age/disk use;
configure bounded retention before prolonged operation. Preserve queues on
rollback. Disabling Hestia relay returns to its known blocked direct route,
so it is not a working fallback. Never retry an uncertain test without checking
queue and Gmail state. Longhorn availability alone is not a backup guarantee.
