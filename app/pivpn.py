
import subprocess, os, re, io
from flask import Blueprint, jsonify, request, abort, current_app, send_file, send_from_directory
from functools import wraps

pivpn_bp = Blueprint("pivpn", __name__)

def require_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "")
        want = f"Bearer {current_app.config['API_TOKEN']}"
        if not current_app.config["API_TOKEN"] or token != want:
            abort(403)
        return f(*args, **kwargs)
    return wrapper

def sh(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or f"Command failed: {cmd}")
    return res.stdout

def pivpn_list():
    bin = current_app.config["PIVPN_BIN"]
    out = sh(["/usr/bin/sudo", bin, "-l"])
    peers = []
    lines = [l for l in out.splitlines() if l.strip()]
    try:
        data_lines = [l for l in lines if re.search(r"\S+\s+\S+", l) and not l.startswith(":::")]
        for l in data_lines:
            cols = re.split(r"\s{2,}", l.strip())
            if len(cols) < 1:
                continue
            peers.append({"raw": l, "cols": cols})
    except Exception:
        pass
    return {"raw": out, "rows": peers}

def pivpn_add(name, days=365):
    bin = current_app.config["PIVPN_BIN"]
    try:
        out = sh(["/usr/bin/sudo", bin, "-a", "-n", name, "-d", str(days)])
    except RuntimeError as e:
        if "unexpected argument" in str(e).lower() or "invalid option" in str(e).lower():
            out = sh(["/usr/bin/sudo", bin, "-a", "-n", name])
        else:
            raise
    return out

def pivpn_revoke(name):
    bin = current_app.config["PIVPN_BIN"]
    try:
        out = sh(["/usr/bin/sudo", bin, "-r", name, "-y"])
    except RuntimeError:
        out = sh(["bash","-c", f"yes | /usr/bin/sudo {bin} -r {name}"])
    return out

@pivpn_bp.get("/list")
@require_token
def api_list():
    return jsonify(pivpn_list())

@pivpn_bp.post("/add")
@require_token
def api_add():
    data = request.get_json(force=True)
    name = data.get("name","").strip()
    days = int(data.get("days", 365))
    if not name:
        abort(400, "name required")
    out = pivpn_add(name, days)
    return jsonify({"ok": True, "output": out})

@pivpn_bp.post("/revoke")
@require_token
def api_revoke():
    data = request.get_json(force=True)
    name = data.get("name","").strip()
    if not name:
        abort(400, "name required")
    out = pivpn_revoke(name)
    return jsonify({"ok": True, "output": out})

@pivpn_bp.get("/download/<name>")
@require_token
def api_download(name):
    cfg_dir = current_app.config["PIVPN_CONFIG_DIR"]
    path = os.path.join(cfg_dir, f"{name}.conf")
    if not os.path.exists(path):
        abort(404, "config not found")
    return send_from_directory(cfg_dir, f"{name}.conf", as_attachment=True)

@pivpn_bp.get("/qr/<name>")
def api_qr(name):
    if not current_app.config.get("PUBLIC_QR_ACCESS", True):
        token = request.headers.get("Authorization", "")
        want = f"Bearer {current_app.config['API_TOKEN']}"
        if not current_app.config["API_TOKEN"] or token != want:
            abort(403)

    cfg_dir = current_app.config["PIVPN_CONFIG_DIR"]
    path = os.path.join(cfg_dir, f"{name}.conf")
    if not os.path.exists(path):
        abort(404, "config not found")
    import qrcode, io
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(text); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
    return send_file(buf, mimetype="image/png", as_attachment=False, download_name=f"{name}.png")
