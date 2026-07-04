
import json, time
from pathlib import Path
from blue_next.config.settings import ROOT_DIR

STATUS_FILES = [ROOT_DIR / "blue_status.json", ROOT_DIR / "HUD_STATUS_FILE"]

def set_status(status: str, detail: str = ""):
    data = {"status": status, "detail": detail, "time": time.strftime("%Y-%m-%d %H:%M:%S")}
    for f in STATUS_FILES:
        try:
            f.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass
    return data
