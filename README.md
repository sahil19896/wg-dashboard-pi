# 🧭 PiVPN Dashboard (v3.6‑Polished‑UI)

A lightweight, private, and fully local **WireGuard + PiVPN dashboard** built for Raspberry Pi.
Designed for simplicity, security, and complete offline control — **no cloud, no telemetry, no external APIs**.

---

## ✨ Key Features

### 🔐 VPN Management
- Add / Revoke PiVPN clients
- Download `.conf` files
- Generate live QR codes
- View PiVPN client list (same output as CLI)

### 🌐 WireGuard Monitoring
- Live peer list (handshake, endpoint, RX/TX)
- Automatic refresh every 10 seconds
- Interface-level and peer-level insights

### 📊 System Monitoring
- CPU%, RAM%, Disk%
- Temperature (if supported)
- System uptime
- Live status cards with color indicators

### 🧙 UI Enhancements (v3.6‑Polished)
- Full‑width responsive layout
- Improved font sizes for large screens
- Clean dark/light toggle theme
- More intuitive navigation
- Better spacing, alignment, and typography
- Faster loading without page refresh
- Modernized modal windows
- Standalone About PiVPN modal

### 🔒 Security
- Token-based API authentication
- Token stored in browser’s localStorage
- Fully local — **no internet required**
- sudo rules included for minimal‑rights execution

---

## 📂 Project Structure
```
wg-dashboard-pi-v3.6-polished-ui/
│
├── app/
│   ├── __init__.py
│   ├── api.py
│   ├── wg.py
│   ├── pivpn.py
│   ├── models.py
│   ├── templates/
│   └── static/
│
├── scripts/
│   └── init_db.py
│
├── deploy/
│   ├── wg-dashboard.service
│   └── sudoers-wg-dashboard
│
├── .env
├── requirements.txt
└── README.md  ← (this file)
```

---

## ⚙️ Installation

### 1️⃣ Extract the project
```bash
unzip wg-dashboard-pi-v3.6-polished-ui.zip -d wg-dashboard
cd wg-dashboard
```

### 2️⃣ Create the virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3️⃣ Initialize Database
```bash
export PYTHONPATH=.
python3 scripts/init_db.py
```

### 4️⃣ Run Dashboard Manually
```bash
flask run --host=0.0.0.0 --port=5000
```

Access:  
**http://<your‑pi‑ip>:5000**

---

## 🔧 Running as a System Service (Gunicorn)

Install sudo + service files:

```bash
sudo install -m 440 -o root -g root deploy/sudoers-wg-dashboard /etc/sudoers.d/wg-dashboard
sudo install -m 644 -o root -g root deploy/wg-dashboard.service /etc/systemd/system/wg-dashboard.service
sudo systemctl daemon-reload
sudo systemctl enable wg-dashboard
sudo systemctl restart wg-dashboard
```

Check logs:
```bash
sudo journalctl -u wg-dashboard -n 40 --no-pager
```

---

## 🔑 Authentication Setup

### 1. Put a token in `.env`:
```
API_TOKEN=use-a-long-secure-random-token
```

### 2. In browser console:
```js
localStorage.setItem('apiToken', 'Bearer use-a-long-secure-random-token');
```

### 3. Refresh the page  
You will stay logged in permanently.

---

## 🧪 About PiVPN Modal

Shows:
- Dashboard version
- Pi model + OS release
- WireGuard version (`wg --version`)
- PiVPN version (`pivpn --version`)
- System info (CPU, RAM, Disk, Temp)
- Real uptime counter

---

## 💬 Troubleshooting

| Issue | Solution |
|------|----------|
| `ModuleNotFoundError: app` | Run `export PYTHONPATH=.` |
| Service can’t find gunicorn | Ensure `.venv` exists, reinstall gunicorn |
| 403 Forbidden | Set correct `apiToken` in localStorage |
| QR not showing | PiVPN installation incomplete |
| Stats not updating | Check sudoers file and permissions |

---

## 🏁 License
MIT — Free, open-source, private forever.

---

Enjoy your polished, fast, modern **self‑hosted PiVPN Dashboard** 🚀
