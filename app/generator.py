
import os, io, re, shlex
from flask import Blueprint, jsonify, request, abort, current_app, send_file
from functools import wraps
from .wg import generate_client_config
import qrcode

gen_bp = Blueprint("gen", __name__)

def require_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "")
        want = f"Bearer {current_app.config['API_TOKEN']}"
        if not current_app.config["API_TOKEN"] or token != want:
            abort(403)
        return f(*args, **kwargs)
    return wrapper

@gen_bp.post("/client")
@require_token
def gen_client():
    name = request.json.get("name","").strip()
    if not name: return jsonify({"error":"name required"}), 400
    conf, pub, address = generate_client_config(name)
    return jsonify({"conf": conf, "public_key": pub, "address": address})

@gen_bp.post("/client/qr")
@require_token
def gen_client_qr():
    text = request.json.get("conf","")
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(text); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
    return send_file(buf, mimetype="image/png", as_attachment=False, download_name="client.png")
