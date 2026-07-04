
# BLUE ULTIMATE FREE JARVIS LAUNCHER
import subprocess, sys, time, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable

def start(name, cmd):
    print(f"[BLUE] Starting {name}...")
    try:
        flags = subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
        return subprocess.Popen(cmd, cwd=str(ROOT), creationflags=flags)
    except Exception as e:
        print(f"[BLUE] {name} failed:", e)

if __name__ == "__main__":
    print("Blue Ultimate Free JARVIS")
    print("No paid services required. Start Ollama separately: ollama run llama3.1:8b")
    procs=[]
    if (ROOT/"orb_ui.py").exists():
        procs.append(start("JARVIS HUD", [PY, "orb_ui.py"]))
        time.sleep(1)
    procs.append(start("Blue Ultimate Core", [PY, "-m", "blue_next.main"]))
    try:
        while any(p and p.poll() is None for p in procs):
            time.sleep(1)
    except KeyboardInterrupt:
        for p in procs:
            if p and p.poll() is None:
                p.terminate()
