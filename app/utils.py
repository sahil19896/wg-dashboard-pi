
import os, zipfile, datetime
from werkzeug.security import generate_password_hash
from .models import User, db

def ensure_admin_user():
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin")
    if not User.query.filter_by(username=username).first():
        u = User(username=username, pw_hash=generate_password_hash(password))
        db.session.add(u)
        db.session.commit()

def make_backup_zip(output_path, items):
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as z:
        for item in items:
            if os.path.isfile(item):
                z.write(item, os.path.basename(item))
            elif os.path.isdir(item):
                for root, _, files in os.walk(item):
                    for f in files:
                        p = os.path.join(root, f)
                        rel = os.path.relpath(p, os.path.dirname(item))
                        z.write(p, rel)
    return output_path
