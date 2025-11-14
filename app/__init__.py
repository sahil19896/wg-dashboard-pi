
import time, threading, os, ipaddress
from flask import Flask, request, abort
from flask_login import LoginManager
from dotenv import load_dotenv
from .config import Config
from .utils import ensure_admin_user
from .wg import sample_wg_metrics, check_and_alert
from .models import db

login_manager = LoginManager()
login_manager.login_view = "auth.login"

def _start_sampler(app):
    def loop():
        with app.app_context():
            while True:
                try:
                    sample_wg_metrics()
                    check_and_alert()
                except Exception as e:
                    app.logger.error(f"Sampler error: {e}")
                time.sleep(60)
    t = threading.Thread(target=loop, daemon=True)
    t.start()

def _ip_allowed(app):
    subnets = app.config.get("ALLOWED_SUBNETS", [])
    if not subnets:
        return True
    ip = request.remote_addr or "127.0.0.1"
    try:
        ip_obj = ipaddress.ip_address(ip)
    except Exception:
        return False
    for cidr in subnets:
        try:
            if ip_obj in ipaddress.ip_network(cidr.strip(), strict=False):
                return True
        except Exception:
            continue
    return False

def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    @app.before_request
    def check_acl():
        if not _ip_allowed(app):
            abort(403)

    from .auth import auth_bp
    from .routes import ui_bp
    from .api import api_bp
    from .pivpn import pivpn_bp
    from .system import system_bp
    from .tools import tools_bp
    from .generator import gen_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(ui_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(pivpn_bp, url_prefix="/api/pivpn")
    app.register_blueprint(system_bp, url_prefix="/api/system")
    app.register_blueprint(tools_bp, url_prefix="/api/tools")
    app.register_blueprint(gen_bp, url_prefix="/api/gen")

    # Load plugins (optional)
    from .plugins_loader import load_plugins
    load_plugins(app)

    with app.app_context():
        from . import models  # ensure models register
        db.create_all()
        ensure_admin_user()

    _start_sampler(app)
    return app
