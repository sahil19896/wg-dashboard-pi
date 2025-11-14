
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from .models import User
from . import login_manager

auth_bp = Blueprint("auth", __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.get("/login")
def login():
    return render_template("login.html")

@auth_bp.post("/login")
def login_post():
    username = request.form.get("username","").strip()
    password = request.form.get("password","")
    remember = bool(request.form.get("remember"))
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.pw_hash, password):
        return redirect(url_for("auth.login"))
    login_user(user, remember=remember)
    return redirect(url_for("ui.index"))

@auth_bp.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
