
import os

def _split_cidrs(raw):
    vals = [s.strip() for s in raw.split(',') if s.strip()]
    return vals

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///wg_dashboard.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_TOKEN = os.getenv("API_TOKEN", "")
    WG_INTERFACE = os.getenv("WG_INTERFACE", "wg0")
    WG_INTERFACES = [s.strip() for s in os.getenv("WG_INTERFACES","wg0").split(",") if s.strip()]
    WG_BIN = os.getenv("WG_BIN", "/usr/bin/wg")
    WG_QUICK_BIN = os.getenv("WG_QUICK_BIN", "/usr/bin/wg-quick")
    WG_CONF_DIR = os.getenv("WG_CONF_DIR", "/etc/wireguard")
    WG_PORT = int(os.getenv("WG_PORT", "51820"))
    WG_SUBNET = os.getenv("WG_SUBNET", "10.6.0.0/24")
    WG_CLIENT_PREFIX = os.getenv("WG_CLIENT_PREFIX", "10.6.0.")
    WG_ALLOWED_DNS = os.getenv("WG_ALLOWED_DNS", "1.1.1.1")
    PIVPN_BIN = os.getenv("PIVPN_BIN", "/usr/local/bin/pivpn")
    PIVPN_CONFIG_DIR = os.getenv("PIVPN_CONFIG_DIR", "/home/pi/configs")
    PUBLIC_QR_ACCESS = os.getenv("PUBLIC_QR_ACCESS", "True").lower() in ("1","true","yes","on")

    ALLOWED_SUBNETS = _split_cidrs(os.getenv("ALLOWED_SUBNETS",""))

    ALERT_IDLE_SECONDS = int(os.getenv("ALERT_IDLE_SECONDS", "300"))
    SMTP_HOST = ""  # disabled in private edition
    SSL_CERT = os.getenv("SSL_CERT","")
    SSL_KEY = os.getenv("SSL_KEY","")
