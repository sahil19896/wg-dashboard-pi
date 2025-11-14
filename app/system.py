
import os, time, psutil, subprocess
from flask import Blueprint, jsonify, request, abort, current_app
from functools import wraps

system_bp = Blueprint("system", __name__)

def require_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "")
        want = f"Bearer {current_app.config['API_TOKEN']}"
        if not current_app.config["API_TOKEN"] or token != want:
            abort(403)
        return f(*args, **kwargs)
    return wrapper

def get_temp_c():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp","r") as f:
            t = int(f.read().strip())
            return t / 1000.0
    except Exception:
        return None

@system_bp.get("/")
@require_token
def sys_info():
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    boot = psutil.boot_time()
    temp = get_temp_c()
    load1, load5, load15 = os.getloadavg()
    procs = sorted([(p.pid, p.info.get("name"), p.info.get("cpu_percent")) for p in psutil.process_iter(["name","cpu_percent"])], key=lambda x: x[2] or 0, reverse=True)[:5]
    return jsonify({
        "cpu": round(cpu,1),
        "mem": round(mem.percent,1),
        "disk": round(disk.percent,1),
        "uptime_sec": int(time.time() - boot),
        "temp_c": temp,
        "load": [load1, load5, load15],
        "top": procs
    })

@system_bp.get("/logs")
@require_token
def sys_logs():
    kind = request.args.get("kind","wg")
    n = request.args.get("n","100")
    try:
        n = str(int(n))
    except:
        n = "100"
    if kind == "wg":
        cmd = ["sudo","journalctl","-u",f"wg-quick@{current_app.config['WG_INTERFACE']}", "-n", n, "--no-pager"]
    elif kind == "syslog":
        cmd = ["sudo","journalctl","-n", n, "--no-pager"]
    elif kind == "auth":
        cmd = ["sudo","journalctl","-u","ssh", "-n", n, "--no-pager"]
    else:
        return jsonify({"error":"unknown kind"}), 400
    out = subprocess.run(cmd, capture_output=True, text=True)
    return jsonify({"output": out.stdout})

@system_bp.post("/power")
@require_token
def power():
    action = request.json.get("action")
    if action == "reboot":
        subprocess.Popen(["sudo","reboot"])
        return jsonify({"ok":True})
    if action == "shutdown":
        subprocess.Popen(["sudo","poweroff"])
        return jsonify({"ok":True})
    return jsonify({"error":"unknown action"}), 400
