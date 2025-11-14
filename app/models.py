
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pw_hash = db.Column(db.String(255), nullable=False)

class Metric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ts = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    interface = db.Column(db.String(32), index=True)
    public_key = db.Column(db.String(64), index=True)
    rx_bytes = db.Column(db.BigInteger)
    tx_bytes = db.Column(db.BigInteger)
    latest_handshake = db.Column(db.Integer)  # epoch sec

class AlertState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_key = db.Column(db.String(64), unique=True, nullable=False)
    last_status = db.Column(db.String(16), default="unknown")  # active/idle
    last_notified = db.Column(db.DateTime, nullable=True)
