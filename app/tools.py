
import subprocess, os, zipfile, datetime
from flask import Blueprint, jsonify, request, abort, current_app, send_file
from functools import wraps
from .utils import make_backup_zip

tools_bp = Blueprint("tools", __name__)

def require_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "")
        want = f"Bearer {current_app.config['API_TOKEN']}"
        if not current_app.config["API_TOKEN"] or token != want:
            abort(403)
        return f(*args, **kwargs)
    return wrapper

WHITELIST = {
    "wg_show": ["sudo","wg","show"],
    "wg_quick_status": ["sudo","systemctl","status","wg-quick@wg0"],
    "ip_addr": ["ip","addr"],
    "df_h": ["df","-h"],
    "uptime": ["uptime"],
    "tailsys": ["sudo","journalctl","-u","wg-quick@wg0","-n","50","--no-pager"]
}

@tools_bp.post("/console")
@require_token
def console():
    cmd_key = request.json.get("cmd")
    if cmd_key not in WHITELIST:
        return jsonify({"error":"command not allowed"}), 400
    out = subprocess.run(WHITELIST[cmd_key], capture_output=True, text=True, cwd="/")
    return jsonify({"output": out.stdout, "stderr": out.stderr, "returncode": out.returncode})

@tools_bp.get("/backup")
@require_token
def backup():
    wg_dir = current_app.config["WG_CONF_DIR"]
    db_path = os.path.join(current_app.root_path, "..", "wg_dashboard.db")
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = os.path.join(current_app.root_path, "..", "backups", f"backup-{ts}.zip")
    items = [wg_dir]
    if os.path.exists(db_path): items.append(db_path)
    make_backup_zip(out_path, items)
    return send_file(out_path, as_attachment=True, download_name=os.path.basename(out_path))
