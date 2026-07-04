# BLUE RUN ALL LAUNCHER
# Run this file: python run_all.py
# It starts Blue main assistant + floating orb + Streamlit dashboard together.

import os
import sys
import time
import signal
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable

processes = []

def start_process(name, command, new_console=True):
    print(f"[BLUE LAUNCHER] Starting {name}...")
    creationflags = 0
    if os.name == "nt" and new_console:
        creationflags = subprocess.CREATE_NEW_CONSOLE
    try:
        p = subprocess.Popen(
            command,
            cwd=str(ROOT),
            creationflags=creationflags
        )
        processes.append((name, p))
        print(f"[BLUE LAUNCHER] {name} started. PID={p.pid}")
        return p
    except Exception as e:
        print(f"[BLUE LAUNCHER] Could not start {name}: {e}")
        return None

def stop_all():
    print("\n[BLUE LAUNCHER] Closing Blue modules...")
    for name, p in processes:
        try:
            if p.poll() is None:
                print(f"[BLUE LAUNCHER] Stopping {name}...")
                p.terminate()
        except Exception as e:
            print(f"[BLUE LAUNCHER] Stop error for {name}: {e}")
    time.sleep(1)
    for name, p in processes:
        try:
            if p.poll() is None:
                p.kill()
        except Exception:
            pass
    print("[BLUE LAUNCHER] Done.")

def main():
    print("=" * 55)
    print("BLUE 4.0 RUN-ALL STARTER")
    print("This launches: main assistant + orb UI + dashboard")
    print("Press CTRL + C in this launcher to close all modules.")
    print("=" * 55)

    # 1) Floating Orb UI
    if (ROOT / "orb_ui.py").exists():
        start_process("Floating Orb UI", [PYTHON, "orb_ui.py"])
        time.sleep(1)
    else:
        print("[BLUE LAUNCHER] orb_ui.py not found, skipping Orb UI.")

    # 2) Streamlit Dashboard
    if (ROOT / "dashboard_jarvis.py").exists():
        start_process("Dashboard", [PYTHON, "-m", "streamlit", "run", "dashboard_jarvis.py"], new_console=True)
        time.sleep(2)
    else:
        print("[BLUE LAUNCHER] dashboard_jarvis.py not found, skipping Dashboard.")

    # 3) Blue Main Assistant
    if (ROOT / "main.py").exists():
        start_process("Blue Main Assistant", [PYTHON, "main.py"], new_console=True)
    else:
        print("[BLUE LAUNCHER] main.py not found. Cannot start Blue.")

    try:
        while True:
            alive = [(n, p) for n, p in processes if p.poll() is None]
            if not alive:
                print("[BLUE LAUNCHER] All modules closed.")
                break
            time.sleep(2)
    except KeyboardInterrupt:
        stop_all()

if __name__ == "__main__":
    main()
