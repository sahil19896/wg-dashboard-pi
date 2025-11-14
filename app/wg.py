
import subprocess, time, os, re, ipaddress, json, tempfile, shlex
from flask import current_app
from .models import Metric, AlertState, db

def sh(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or f"Command failed: {cmd}")
    return res.stdout

def wg_dump():
    wg = current_app.config["WG_BIN"]
    out = sh(["sudo", wg, "show", "all", "dump"])
    lines = out.strip().splitlines()
    peers = []
    now = int(time.time())
    for line in lines[1:]:
        f = line.split("\t")
        if len(f) < 9:
            continue
        iface, pub, psk, endpoint, ips, hs, rx, tx, keepalive = f[:9]
        hs_i = int(hs) if hs.isdigit() else 0
        peers.append({
            "interface": iface,
            "public_key": pub,
            "endpoint": endpoint or "—",
            "allowed_ips": ips or "—",
            "latest_handshake": hs_i,
            "latest_handshake_human": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(hs_i)) if hs_i else "Never",
            "rx": int(rx),
            "tx": int(tx),
            "rx_h": _fmt_bytes(int(rx)),
            "tx_h": _fmt_bytes(int(tx)),
            "status": "active" if hs_i and (now - hs_i) < 180 else "idle"
        })
    return peers

def interface_status():
    try:
        out = sh(["sudo", current_app.config["WG_BIN"], "show"])
        return out.strip()
    except Exception as e:
        return f"Error: {e}"

def restart_interface():
    iface = current_app.config["WG_INTERFACE"]
    sh(["sudo", "systemctl", "restart", f"wg-quick@{iface}"])
    return "restarted"

def start_interface():
    iface = current_app.config["WG_INTERFACE"]
    sh(["sudo", "systemctl", "start", f"wg-quick@{iface}"])
    return "started"

def stop_interface():
    iface = current_app.config["WG_INTERFACE"]
    sh(["sudo", "systemctl", "stop", f"wg-quick@{iface}"])
    return "stopped"

def add_peer(public_key, allowed_ips):
    iface = current_app.config["WG_INTERFACE"]
    conf_path = f"/etc/wireguard/{iface}.conf"
    line = f"\n[Peer]\nPublicKey = {public_key}\nAllowedIPs = {allowed_ips}\n"
    sh(["bash", "-c", f"echo {shlex.quote(line)} | sudo tee -a {conf_path} > /dev/null"])
    sh(["sudo", "wg-quick", "save", iface])
    sh(["sudo", "systemctl", "reload", f"wg-quick@{iface}"])
    return "peer added"

def remove_peer(public_key):
    iface = current_app.config["WG_INTERFACE"]
    sh(["sudo", "wg", "set", iface, "peer", public_key, "remove"])
    sh(["sudo", "wg-quick", "save", iface])
    return "peer removed"

def generate_keys():
    priv = sh(["bash","-c","wg genkey"] ).strip()
    pub = sh(["bash","-c",f"echo {priv} | wg pubkey"]).strip()
    return priv, pub

def next_client_ip():
    prefix = current_app.config["WG_CLIENT_PREFIX"]
    used = set()
    conf_path = os.path.join(current_app.config["WG_CONF_DIR"], f"{current_app.config['WG_INTERFACE']}.conf")
    if os.path.exists(conf_path):
        with open(conf_path,"r",encoding="utf-8") as f:
            for line in f:
                m = re.search(r"(\d+\.\d+\.\d+\.\d+)/(\d+)", line)
                if m:
                    used.add(m.group(1))
    for i in range(2,255):
        cand = f"{prefix}{i}"
        if cand not in used:
            return cand + "/32"
    raise RuntimeError("No free IP in subnet")

def generate_client_config(name):
    priv, pub = generate_keys()
    address = next_client_ip()
    server_port = current_app.config.get("WG_PORT", 51820)
    dns = current_app.config.get("WG_ALLOWED_DNS","1.1.1.1")
    conf = f"""[Interface]
PrivateKey = {priv}
Address = {address}
DNS = {dns}

[Peer]
PublicKey = SERVER_PUBLIC_KEY
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = YOUR_SERVER_IP:{server_port}
PersistentKeepalive = 25
"""
    return conf, pub, address

def _fmt_bytes(n):
    for unit in ["B","KB","MB","GB","TB"]:
        if n < 1024: return f"{n:.0f} {unit}" if unit=="B" else f"{n:.2f} {unit}"
        n/=1024
    return f"{n:.2f} PB"

def sample_wg_metrics():
    for p in wg_dump():
        m = Metric(
            interface=p["interface"],
            public_key=p["public_key"],
            rx_bytes=p["rx"],
            tx_bytes=p["tx"],
            latest_handshake=p["latest_handshake"]
        )
        db.session.add(m)
    db.session.commit()

def check_and_alert():
    peers = wg_dump()
    for p in peers:
        state = AlertState.query.filter_by(public_key=p["public_key"]).first()
        if not state:
            state = AlertState(public_key=p["public_key"], last_status=p["status"])
            db.session.add(state)
    db.session.commit()
