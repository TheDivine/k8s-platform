# Migration From Docker Compose

The old Kasm installation under `/opt/kasm` was host-managed through Docker Compose. Keep it disabled while the Kubernetes-native deployment is built and validated.

## Stop Old Kasm

```bash
cd /opt/kasm/current/bin
bash stop
ss -tulpn | grep -E '4443|3389|kasm'
docker ps -a | grep kasm
```

## Back Up Existing Configuration

Create a dated archive location outside `/opt/kasm`:

```bash
sudo mkdir -p /root/kasm-backups/$(date +%Y%m%d)
sudo tar -czf /root/kasm-backups/$(date +%Y%m%d)/kasm-conf.tgz /opt/kasm/current/conf
sudo tar -czf /root/kasm-backups/$(date +%Y%m%d)/kasm-certs.tgz /opt/kasm/current/certs
sudo tar -czf /root/kasm-backups/$(date +%Y%m%d)/kasm-docker.tgz /opt/kasm/current/docker
```

If additional local customization exists under `/opt/kasm`, capture it before changing or removing anything:

```bash
sudo find /opt/kasm -maxdepth 3 -type f | sort
```

## Stop Compose Services

Use the official Kasm stop command first. If Compose services remain after validation, run the Compose down command from the correct Kasm compose directory:

```bash
cd /opt/kasm/current/docker
sudo docker compose down
```

## Archive Instead of Delete

Do not delete `/opt/kasm` immediately. Move or archive it only after the Kubernetes deployment is validated:

```bash
sudo tar -czf /root/kasm-backups/$(date +%Y%m%d)/kasm-opt-full.tgz /opt/kasm
```

## Validation Checklist

- Old Kasm ports are no longer listening on the host.
- No old Kasm containers are running.
- Kubernetes namespace, PVCs, services, and ingress are healthy.
- The final Kasm hostname resolves to Traefik.
- TLS is valid for the chosen hostname.
- Admin login succeeds with Kubernetes-managed secrets.
- A workspace launches successfully.
- Browser websocket or remote desktop sessions remain stable.
- Database and persistent data backups are tested.
- Rollback requirements are documented before deleting old data.

