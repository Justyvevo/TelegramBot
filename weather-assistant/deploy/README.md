# Linux deployment template

This is an example for a systemd-based Linux host. It has not been deployed or verified on the local Windows development machine. Do not run the commands on a shared server without reviewing ownership and paths.

1. Create a dedicated unprivileged `weatherbot` system user/group (no login shell).
2. Put this package in `/opt/weather-assistant`, create `/opt/weather-assistant/.venv` using Python 3.11+ and install the package into that environment. Make the code readable by the service user; keep it non-writable where practical.
3. Store the required environment values in `/etc/weather-assistant.env`. This file should be owned by root with mode `0600`. Do not put real keys in the unit file or command history. systemd reads `EnvironmentFile` before dropping privileges.
4. Review and copy `weather-assistant.service` into `/etc/systemd/system/`.
5. Reload unit definitions and enable/start the service only when ready:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now weather-assistant
sudo systemctl status weather-assistant
sudo journalctl -u weather-assistant --since today
```

Only one process may poll a bot token. Stop a local instance before starting the service. This template requires outbound HTTPS to Telegram and WeatherAPI but no inbound listening port. Never disable TLS verification to resolve network issues.

To stop the service:

```bash
sudo systemctl stop weather-assistant
```

Restarting loses in-memory city selections and subscriptions. Users must opt in again. API/network availability and a real private-chat exchange should be checked before sharing a bot link publicly.
