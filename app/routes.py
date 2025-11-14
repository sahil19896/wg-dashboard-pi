
from flask import Blueprint, render_template, current_app, send_from_directory
from flask_login import login_required

ui_bp = Blueprint("ui", __name__)

@ui_bp.get("/")
@login_required
def index():
    token = current_app.config.get("API_TOKEN","")
    public_qr = current_app.config.get("PUBLIC_QR_ACCESS", True)
    return render_template("index.html", api_token=token, public_qr=public_qr)

@ui_bp.get("/manifest.json")
def manifest():
    return send_from_directory('templates', 'manifest.json', mimetype='application/json')

@ui_bp.get("/sw.js")
def sw():
    return send_from_directory('templates', 'sw.js', mimetype='application/javascript')
