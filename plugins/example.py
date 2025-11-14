
# Example plugin: adds /api/hello endpoint
from flask import Blueprint, jsonify

def register(app):
    bp = Blueprint("hello_plugin", __name__)
    @bp.get("/api/hello")
    def hello():
        return jsonify({"hello": "plugins"})
    app.register_blueprint(bp)
