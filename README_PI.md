
# WireGuard Dashboard • Raspberry Pi (v3.6, Private Edition)

**Private-first:** no outbound integrations (no Telegram/email/third-party). Everything runs on your Pi and your LAN.

## Highlights
- 🔐 Local auth only, token auto-injected to UI
- 🧪 Peer Generator: creates keys, assigns next IP, updates `/etc/wireguard/wg0.conf`, shows QR + download
- 🧰 Controls: restart/start/stop wg0, reboot/shutdown Pi (with confirmation), view logs
- 📊 System health: CPU, RAM, disk, temp, load, process list
- 🧾 Log viewer (syslog/auth/wg-quick@wg0) with filters
- ⌨️ Local Console: run whitelisted commands only
- 📈 Peer history: handshake + rx/tx over time, per-peer chart
- 🧳 Backup/Export: zip WireGuard config + dashboard db
- 🌓 Themes: Dark/Light/OLED/Nord; PWA installable (manifest + service worker)
- 🔒 Security: IP allowlist (LAN ACL), PUBLIC_QR_ACCESS toggle
- 🧩 Plugin system: drop-in Blueprints via `plugins/`

## Quick Start
```bash
unzip wg-dashboard-pi-v3.6.zip -d wg-dashboard-pi-v3.6
cd wg-dashboard-pi-v3.6

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

cp .env.example .env
nano .env   # set SECRET_KEY, ADMIN_PASSWORD, API_TOKEN, ALLOWED_SUBNETS

# Initialize DB
python3 -m scripts.init_db

# Install sudoers + systemd
sudo install -m 440 -o root -g root deploy/sudoers-wg-dashboard /etc/sudoers.d/wg-dashboard
sudo install -m 644 -o root -g root deploy/wg-dashboard.service /etc/systemd/system/wg-dashboard.service
sudo systemctl daemon-reload
sudo systemctl enable wg-dashboard
sudo systemctl restart wg-dashboard
sudo journalctl -u wg-dashboard -f
```

Open: `http://<pi-ip>:5000`
