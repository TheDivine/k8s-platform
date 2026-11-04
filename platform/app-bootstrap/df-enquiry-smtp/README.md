# DF enquiry SMTP prerequisite

The operator verified the existing processlayer-hestia login against smtp.processlayerai.com:587 using certificate-verified STARTTLS on 4 November 2026. No test email was sent during credential preparation. The password was entered privately and sealed offline for df-enquiry-smtp in processlayer and processlayer-prod; no plaintext is committed.

Flux owns this credential package with prune:false and waits for SealedSecret Synced=True. Application bootstrap depends on it and exposes processlayer.ai/smtp-prerequisite=df-enquiry-smtp-2026-11-04 on the two existing Argo Applications. This marker confirms prerequisite reconciliation, not delivery. Workload activation remains in the app repository after image CI and staging acceptance.

Only SMTP_PASSWORD is supplied. Existing relay-auth, DKIM, registry credentials, Hestia settings, queues, MX and DNS are unchanged. Do not regenerate or rotate the relay credential as part of normal deployment. For future rotation, encrypt the matching current relay password with the trusted controller public certificate using strict scope for each exact name/namespace, and update through a reviewed Git change. Never paste passwords into Git or chat.

The intended alert destination is mr.daliborf@gmail.com; sender dalibor@processlayerai.com matches the existing relay restriction. The application sends only owner alerts after persistence, not prospect messages. A controlled test and actual inbox receipt are required before claiming delivery.
