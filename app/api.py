
from flask import Blueprint, jsonify, request, abort, current_app, send_file
from functools import wraps
from .wg import wg_dump, interface_status, restart_interface, start_interface, stop_interface, add_peer, remove_peer
from .models import Metric, db
from io import BytesIO
import qrcode

api_bp = Blueprint("api", __name__)

def require_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "")
        want = f"Bearer {current_app.config['API_TOKEN']}"
        if not current_app.config["API_TOKEN"] or token != want:
            abort(403)
        return f(*args, **kwargs)
    return wrapper

@api_bp.get("/peers")
@require_token
def api_peers():
    return jsonify(wg_dump())

@api_bp.get("/status")
@require_token
def api_status():
    return jsonify({"raw": interface_status()})

@api_bp.post("/restart")
@require_token
def api_restart():
    return jsonify({"result": restart_interface()})

@api_bp.post("/start")
@require_token
def api_start():
    return jsonify({"result": start_interface()})

@api_bp.post("/stop")
@require_token
def api_stop():
    return jsonify({"result": stop_interface()})

@api_bp.post("/add-peer")
@require_token
def api_add_peer():
    data = request.get_json(force=True)
    return jsonify({"result": add_peer(data["public_key"], data["allowed_ips"])})

@api_bp.post("/remove-peer")
@require_token
def api_remove_peer():
    data = request.get_json(force=True)
    return jsonify({"result": remove_peer(data["public_key"])})

@api_bp.get("/stats")
@require_token
def api_stats():
    q = db.session.query(Metric).order_by(Metric.ts.desc()).limit(2000).all()
    rows = [
        dict(ts=m.ts.isoformat(), interface=m.interface, public_key=m.public_key, rx=m.rx_bytes, tx=m.tx_bytes, hs=m.latest_handshake)
        for m in q
    ]
    return jsonify(rows)

@api_bp.post("/qr")
@require_token
def api_qr():
    data = request.get_json(force=True)
    txt = data.get("text","")
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(txt); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
    return send_file(buf, mimetype="image/png", as_attachment=False, download_name="qr.png")
