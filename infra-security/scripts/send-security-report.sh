#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cat <<'EOF'
Security report placeholder.

This script intentionally does not send data anywhere.

Future integrations could add one of:
- Slack webhook
- Telegram bot
- email relay
- Wazuh API
- ticketing webhook

Do not commit real webhook URLs or credentials.
EOF

"$SCRIPT_DIR/collect-security-status.sh" || true

