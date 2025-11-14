
import importlib.util, os, sys
from flask import current_app

def load_plugins(app):
    plug_dir = os.path.join(app.root_path, "..", "plugins")
    if not os.path.isdir(plug_dir):
        return
    for fname in os.listdir(plug_dir):
        if not fname.endswith(".py"):
            continue
        path = os.path.join(plug_dir, fname)
        try:
            spec = importlib.util.spec_from_file_location(f"plugins.{fname[:-3]}", path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = mod
            spec.loader.exec_module(mod)  # type: ignore
            if hasattr(mod, "register"):
                mod.register(app)
                app.logger.info(f"Loaded plugin: {fname}")
        except Exception as e:
            app.logger.error(f"Plugin load failed for {fname}: {e}")
