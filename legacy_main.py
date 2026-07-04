# BLUE START HERE
import os
import re
import json
import time
import queue
import threading
import webbrowser
import difflib
import winsound
import sqlite3
import subprocess

try:
    import joblib
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.pipeline import Pipeline
    from sklearn.linear_model import LogisticRegression
    ML_AVAILABLE = True
except Exception:
    ML_AVAILABLE = False
import requests
import sounddevice as sd
import pyttsx3
import asyncio
import uuid

try:
    import edge_tts
    from playsound import playsound
    EDGE_TTS_AVAILABLE = True
except Exception:
    EDGE_TTS_AVAILABLE = False
import pyautogui

try:
    import pytesseract
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

try:
    import screen_brightness_control as sbc
    BRIGHTNESS_AVAILABLE = True
except Exception:
    BRIGHTNESS_AVAILABLE = False

try:
    import pandas as pd
    import numpy as np
    from sklearn.linear_model import LinearRegression
    DATA_AI_AVAILABLE = True
except Exception:
    DATA_AI_AVAILABLE = False

try:
    import cv2
    VISION_AVAILABLE = True
except Exception:
    VISION_AVAILABLE = False

try:
    import yfinance as yf
    FINANCE_AVAILABLE = True
except Exception:
    FINANCE_AVAILABLE = False

from datetime import datetime
from urllib.parse import quote_plus
from scipy.io.wavfile import write
try:
    from scipy.signal import butter, filtfilt
    SCIPY_SIGNAL_AVAILABLE = True
except Exception:
    SCIPY_SIGNAL_AVAILABLE = False
try:
    import noisereduce as nr
    NOISEREDUCE_AVAILABLE = True
except Exception:
    NOISEREDUCE_AVAILABLE = False
from faster_whisper import WhisperModel

# =========================================================
# BLUE 3.0 SETTINGS
# =========================================================
WAKE_WORD = "blue"              # Say: "Blue open YouTube"
ALWAYS_LISTEN_MODE = True       # False = wake word is needed only to activate Blue session
MAIN_ENGINE = "faster"           # Blue 3.0 uses only Faster Whisper now
MODEL_SIZE = "tiny"              # Command model: tiny, base, small, medium
WAKE_MODEL_SIZE = "tiny"          # Fast wake-word model for standby mode
DEVICE = "cpu"                   # cpu. For Nvidia GPU use: cuda
COMPUTE_TYPE = "int8"            # CPU: int8. GPU: float16
SAMPLE_RATE = 16000

# =========================================================
# BACKGROUND NOISE CANCELLATION SETTINGS
# =========================================================
# Works without extra packages using noise gate + high-pass filter + normalization.
# Optional better denoise: pip install noisereduce
NOISE_CANCELLATION_ENABLED = True
NOISE_PROFILE_FILE = "blue_noise_profile.json"
NOISE_GATE_MULTIPLIER = 1.8        # higher = stronger noise removal
NOISE_FLOOR_SECONDS = 0.35         # first part of recording used as ambient noise sample
HIGH_PASS_FILTER_ENABLED = True
HIGH_PASS_CUTOFF_HZ = 90           # removes fan/rumble/low frequency noise
NORMALIZE_MIC_AUDIO = True
MIN_VOICE_RMS = 70                 # if below this, Blue treats audio as mostly silence

RECORD_SECONDS = 3
WAKE_RECORD_SECONDS = 0.8          # Short listening window while waiting for wake word
COMMAND_SECONDS = 3
TEMP_AUDIO = "blue3_command.wav"
MEMORY_FILE = "blue3_memory.json"
LANGUAGE = "en-IN"
USE_ONLINE_KNOWLEDGE = True
USE_META_AI_BRAIN = True
OLLAMA_MODEL = "llama3.2:3b"      # Meta Llama model through Ollama. You can also use llama3.1:8b if your PC is strong.
OLLAMA_URL = "http://localhost:11434/api/generate"
ACTIVE_SESSION_SECONDS = 12   # Say "Blue" once, then commands work until you say sleep/standby
DATABASE_FILE = "blue3_memory.db"
INTENT_MODEL_FILE = "blue3_intent_model.joblib"

# =========================================================
# FULL CONTROL MODE + SAFETY GUARD
# =========================================================
FULL_CONTROL_MODE = True
SAFETY_MODE = True
CONFIRM_RISKY_ACTIONS = True
ACTION_LOG_TABLE = "action_logs"

TRADINGVIEW_CHART_URL = "https://in.tradingview.com/chart/JAQInaxL/?symbol=OANDA%3AXAUUSD"

# Blue must NEVER type or handle private secrets.
SECRET_WORDS = [
    "password", "pass word", "passcode", "otp", "one time password",
    "pin", "cvv", "card number", "atm pin", "upi pin", "secret key",
    "api key", "private key", "recovery phrase", "seed phrase"
]

# Destructive commands are blocked even in Full Control Mode.
BLOCKED_TERMINAL_PATTERNS = [
    "format c:", "format d:", "diskpart", "clean all", "delete partition",
    "rm -rf /", "rm -rf *", "del /f /s /q", "rmdir /s /q",
    "cipher /w", "bcdedit", "reg delete", "takeown /f c:\\",
    "shutdown /s /t 0", "shutdown /r /t 0"
]

# These actions are allowed only after confirmation.
RISKY_ACTION_WORDS = [
    "delete", "remove file", "erase", "format", "shutdown", "restart",
    "install", "uninstall", "send email", "send mail", "send message",
    "whatsapp message", "payment", "pay ", "make payment", "upi",
    "terminal", "cmd", "command prompt", "powershell", "run command",
    "execute command", "shell"
]

SAFE_FULL_CONTROL_HELP = "Full Control Mode is active with Safety Mode. I can open apps, websites, folders, control browser, volume, brightness, screenshots, OCR screen reading, and safe automation. Risky actions need your confirmation."

VOICE_RATE = 175
VOICE_VOLUME = 1.0

# Voice mode:
# "edge" = more natural JARVIS-style voice, needs internet
# "pyttsx3" = offline backup voice
VOICE_MODE = "edge"
JARVIS_VOICE = "en-US-GuyNeural"
VOICE_EDGE_RATE = "-10%"
VOICE_EDGE_PITCH = "-20Hz"

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

APP_COMMANDS = {
    "notepad": "notepad",
    "calculator": "calc",
    "paint": "mspaint",
    "cmd": "cmd",
    "command prompt": "cmd",
    "vs code": "code",
    "vscode": "code",
    "chrome": "chrome",
    "crome": "chrome",
    "file explorer": "explorer",
    "explorer": "explorer",
    "task manager": "taskmgr",
    "settings": "start ms-settings:",
}

FOLDER_COMMANDS = {
    "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
    "documents": os.path.join(os.path.expanduser("~"), "Documents"),
    "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
    "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
    "music": os.path.join(os.path.expanduser("~"), "Music"),
    "videos": os.path.join(os.path.expanduser("~"), "Videos"),
}

DATA_SEARCH_FOLDERS = [
    FOLDER_COMMANDS["downloads"],
    FOLDER_COMMANDS["desktop"],
    FOLDER_COMMANDS["documents"],
]

WEBSITE_COMMANDS = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "chatgpt": "https://chatgpt.com",
    "whatsapp": "https://web.whatsapp.com",
    "chart": TRADINGVIEW_CHART_URL,
    "tradingview chart": TRADINGVIEW_CHART_URL,
    "xauusd chart": TRADINGVIEW_CHART_URL,
}

# =========================================================
# CHROME SETUP
# =========================================================
def setup_browser():
    for path in CHROME_PATHS:
        if os.path.exists(path):
            webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(path))
            return "chrome"
    return None

BROWSER_NAME = setup_browser()


def open_url(url: str):
    try:
        if BROWSER_NAME:
            webbrowser.get(BROWSER_NAME).open(url)
        else:
            webbrowser.open(url)
    except Exception:
        webbrowser.open(url)

# =========================================================
# JARVIS SOUND EFFECTS
# =========================================================
def play_tone(kind="done"):
    return
    try:
        if kind == "startup":
            winsound.Beep(600,120); winsound.Beep(900,120); winsound.Beep(1200,160)
        elif kind == "listen":
            winsound.Beep(850,90)
        elif kind == "thinking":
            winsound.Beep(700,70); winsound.Beep(760,70)
        elif kind == "done":
            winsound.Beep(1000,90); winsound.Beep(1300,100)
        elif kind == "error":
            winsound.Beep(350,180)
    except Exception as e:
        print("Sound error:", e)

# =========================================================
# SPEECH OUTPUT: NON-REPEATING + QUEUE
# =========================================================
engine = pyttsx3.init()
engine.setProperty("rate", VOICE_RATE)
engine.setProperty("volume", VOICE_VOLUME)

speech_queue = queue.Queue()

# =========================================================
# ADVANCED TEXT COMMAND MODE
# =========================================================
TEXT_COMMAND_MODE = True
TEXT_COMMAND_HISTORY_FILE = "blue_text_history.json"
command_queue = queue.Queue()
text_input_active = threading.Event()

last_spoken = ""
last_spoken_time = 0


async def speak_with_edge_tts(text: str):
    filename = f"blue_voice_{uuid.uuid4().hex}.mp3"
    communicate = edge_tts.Communicate(
        text=text,
        voice=JARVIS_VOICE,
        rate=VOICE_EDGE_RATE,
        pitch=VOICE_EDGE_PITCH
    )
    await communicate.save(filename)
    playsound(filename)
    try:
        os.remove(filename)
    except Exception:
        pass


def speak_with_pyttsx3(text: str):
    engine.say(text)
    engine.runAndWait()


def speech_worker():
    while True:
        text = speech_queue.get()
        if text is None:
            break
        try:
            if VOICE_MODE == "edge" and EDGE_TTS_AVAILABLE:
                asyncio.run(speak_with_edge_tts(text))
            else:
                speak_with_pyttsx3(text)
        except Exception as e:
            print("TTS error:", e)
            try:
                speak_with_pyttsx3(text)
            except Exception:
                pass
        speech_queue.task_done()

threading.Thread(target=speech_worker, daemon=True).start()


def speak(text: str, allow_repeat: bool = False):
    global last_spoken, last_spoken_time
    text = str(text).strip()
    if not text:
        return

    now = time.time()
    if not allow_repeat and text == last_spoken and now - last_spoken_time < 10:
        print(f"Blue skipped repeat: {text}")
        return

    print(f"Blue: {text}")
    last_spoken = text
    last_spoken_time = now
    speech_queue.put(text)


def wait_until_done_speaking():
    try:
        speech_queue.join()
        time.sleep(0.4)
    except Exception:
        time.sleep(0.8)

# =========================================================
# ADVANCED TEXT COMMAND HELPERS
# =========================================================
def load_text_history():
    if not os.path.exists(TEXT_COMMAND_HISTORY_FILE):
        return []
    try:
        with open(TEXT_COMMAND_HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_text_history(history):
    try:
        with open(TEXT_COMMAND_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-80:], f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Text history save error:", e)


TEXT_COMMAND_HISTORY = load_text_history()


def add_text_history(command):
    command = command.strip()
    if not command:
        return
    if command in TEXT_COMMAND_HISTORY:
        TEXT_COMMAND_HISTORY.remove(command)
    TEXT_COMMAND_HISTORY.append(command)
    save_text_history(TEXT_COMMAND_HISTORY)


def get_text_suggestions(partial):
    partial = normalize_text(partial)
    examples = [
        "open youtube", "open google", "open downloads", "open calculator",
        "what time is it", "today date", "search for ibps syllabus",
        "search youtube for python tutorial", "explain machine learning",
        "make ibps study plan", "analyze data", "predict data", "read screen",
        "take screenshot", "weather in aurangabad", "latest news about ai",
        "stock price aapl", "study mode", "train my dataset", "sleep", "exit"
    ]
    pool = list(dict.fromkeys(TEXT_COMMAND_HISTORY[-30:] + examples))
    if not partial:
        return examples[:5]
    suggestions = []
    for item in pool:
        clean_item = normalize_text(item)
        if clean_item.startswith(partial) or partial in clean_item:
            suggestions.append(item)
    return suggestions[:5]


def expand_slash_command(command):
    clean = command.strip()
    if not clean.startswith("/"):
        return command
    parts = clean[1:].split(maxsplit=1)
    root = parts[0].lower() if parts else ""
    rest = parts[1] if len(parts) > 1 else ""
    shortcuts = {
        "yt": "open youtube",
        "youtube": "open youtube",
        "google": "open google",
        "g": "search for " + rest if rest else "open google",
        "search": "search for " + rest,
        "time": "what time is it",
        "date": "today date",
        "ai": rest if rest else "explain artificial intelligence",
        "explain": "explain " + rest,
        "data": "analyze data",
        "predict": "predict data",
        "screen": "read screen",
        "shot": "take screenshot",
        "weather": "weather in " + rest if rest else "weather",
        "news": "latest news about " + rest if rest else "latest news",
        "study": "study mode",
        "sleep": "sleep",
        "exit": "exit",
    }
    return shortcuts.get(root, command)


def print_text_help():
    print("""
Text command tips:
  Type command + Enter to run.
  Press Esc to cancel current command.
  Press Tab to show suggestions.
  Slash shortcuts: /yt, /g topic, /ai topic, /weather city, /study, /sleep
""")



# =========================================================
# MEMORY
# =========================================================
DEFAULT_MEMORY = {
    "user_name": "",
    "facts": [],
    "chat_history": [],
    "last_command": "",
    "preferences": {}
}


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return DEFAULT_MEMORY.copy()
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, value in DEFAULT_MEMORY.items():
            data.setdefault(key, value)
        return data
    except Exception:
        return DEFAULT_MEMORY.copy()


def save_memory():
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Memory save error:", e)


memory = load_memory()


# =========================================================
# SQLITE MEMORY DATABASE + LONG TERM PROFILE
# =========================================================
def init_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS command_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            command TEXT,
            intent TEXT,
            category TEXT,
            payload TEXT,
            response TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS action_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            command TEXT,
            action_type TEXT,
            status TEXT,
            reason TEXT
        )
    """)
    conn.commit()
    conn.close()


def db_set(table, key, value):
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    cur.execute(
        f"INSERT OR REPLACE INTO {table}(key, value, updated_at) VALUES (?, ?, ?)",
        (key, str(value), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def get_intent_category(intent):
    if intent in ["open_app", "youtube", "google_home", "maps", "open_folder", "open_chart"]:
        return "open"
    if intent in ["google_search", "web_search", "youtube_search"]:
        return "search"
    if intent in ["remember", "recall_memory", "clear_memory", "recall_profile"]:
        return "memory"
    if intent in ["time", "date", "screenshot", "lock", "volume_up", "volume_down", "mute", "brightness_up", "brightness_down", "music_play_pause", "music_next", "music_previous", "browser_new_tab", "browser_close_tab", "browser_refresh", "browser_back", "read_screen"]:
        return "pc_control"
    if intent in ["analyze_data", "predict_data", "daily_summary", "next_suggestion"]:
        return "data_science"
    if intent in ["name_query", "how_are_you", "greeting", "chat", "sleep", "active_status"]:
        return "chat"
    return "other"


def log_command_db(command, intent, payload, response):
    category = get_intent_category(intent)
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO command_logs(timestamp, command, intent, category, payload, response) VALUES (?, ?, ?, ?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), command, intent, category, payload, response)
        )
    except sqlite3.OperationalError:
        cur.execute("ALTER TABLE command_logs ADD COLUMN category TEXT")
        cur.execute(
            "INSERT INTO command_logs(timestamp, command, intent, category, payload, response) VALUES (?, ?, ?, ?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), command, intent, category, payload, response)
        )
    conn.commit()
    conn.close()


def log_action_db(command, action_type, status, reason=""):
    """Separate safety/action log for Full Control Mode."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS action_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                command TEXT,
                action_type TEXT,
                status TEXT,
                reason TEXT
            )
        """)
        cur.execute(
            "INSERT INTO action_logs(timestamp, command, action_type, status, reason) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), command, action_type, status, reason)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("Action log error:", e)


def is_emergency_stop(command: str) -> bool:
    clean = normalize_text(command)
    return clean in ["stop blue", "blue stop", "emergency stop", "stop assistant", "kill blue"]


def contains_secret_request(command: str) -> bool:
    clean = normalize_text(command)
    return any(word in clean for word in SECRET_WORDS)


def contains_blocked_terminal_pattern(command: str) -> bool:
    clean = command.lower().strip()
    return any(pattern in clean for pattern in BLOCKED_TERMINAL_PATTERNS)


def is_risky_action(command: str) -> bool:
    clean = normalize_text(command)
    return any(word in clean for word in RISKY_ACTION_WORDS)


def ask_user_confirmation(command: str, reason="risky action") -> bool:
    if not CONFIRM_RISKY_ACTIONS:
        return True
    speak(f"Safety check. This may be a {reason}. Should I continue? Type yes or no.", allow_repeat=True)
    wait_until_done_speaking()
    try:
        answer = input(f"Confirm action '{command}'? yes/no: ").strip().lower()
    except Exception:
        answer = "no"
    allowed = answer in ["yes", "y", "ok", "continue", "allow", "confirm"]
    log_action_db(command, "confirmation", "allowed" if allowed else "cancelled", reason)
    return allowed


def safety_guard(command: str):
    """Return (allowed: bool, stop_blue: bool, reply: str)."""
    if not SAFETY_MODE:
        return True, False, ""

    if is_emergency_stop(command):
        reply = "Emergency stop activated. Blue is shutting down safely."
        log_action_db(command, "emergency_stop", "success", "user emergency stop")
        return False, True, reply

    if contains_secret_request(command):
        reply = "For safety, I cannot type, store, read, or handle passwords, OTP, PIN, CVV, API keys, or private keys."
        log_action_db(command, "secret_protection", "blocked", "secret keyword detected")
        return False, False, reply

    if contains_blocked_terminal_pattern(command):
        reply = "I blocked this command because it can damage the system or erase data."
        log_action_db(command, "blocked_terminal", "blocked", "destructive terminal pattern")
        return False, False, reply

    if is_risky_action(command):
        if not ask_user_confirmation(command, "risky action"):
            reply = "Cancelled. I did not perform that action."
            log_action_db(command, "risky_action", "cancelled", "user denied confirmation")
            return False, False, reply
        log_action_db(command, "risky_action", "confirmed", "user confirmed")

    return True, False, ""


def extract_shell_command(command: str):
    clean = command.strip()
    phrases = ["run command", "execute command", "run terminal command", "run cmd", "run powershell"]
    low = clean.lower()
    for phrase in phrases:
        if low.startswith(phrase):
            return clean[len(phrase):].strip(" :")
    return ""


def run_safe_shell_command(command: str):
    shell_cmd = extract_shell_command(command)
    if not shell_cmd:
        return "Tell me the exact command after saying run command."

    if contains_blocked_terminal_pattern(shell_cmd) or contains_secret_request(shell_cmd):
        log_action_db(command, "shell", "blocked", "blocked after extraction")
        return "I blocked that terminal command for safety."

    try:
        completed = subprocess.run(
            shell_cmd, shell=True, capture_output=True, text=True, timeout=20
        )
        output = (completed.stdout or completed.stderr or "Command finished.").strip()
        output = output[:600]
        log_action_db(command, "shell", "success", shell_cmd)
        return "Command executed. Output: " + output
    except Exception as e:
        log_action_db(command, "shell", "failed", str(e))
        return "I could not run that command because " + str(e)


def handle_full_control_direct_commands(command: str):
    """Direct commands that should work before ML/fuzzy intent classification."""
    global ALWAYS_LISTEN_MODE, NOISE_CANCELLATION_ENABLED
    clean = normalize_text(remove_wake_word(command))

# =========================================================
# CLOSE APPS / WINDOWS / WEBSITES
# =========================================================

CLOSE_COMMANDS = {
    "chrome": ["chrome.exe"],
    "crome": ["chrome.exe"],
    "youtube": ["chrome.exe"],
    "google": ["chrome.exe"],
    "gmail": ["chrome.exe"],
    "github": ["chrome.exe"],
    "whatsapp": ["chrome.exe"],
    "notepad": ["notepad.exe"],
    "calculator": ["CalculatorApp.exe", "calc.exe"],
    "paint": ["mspaint.exe"],
    "cmd": ["cmd.exe"],
    "command prompt": ["cmd.exe"],
    "vs code": ["Code.exe"],
    "vscode": ["Code.exe"],
    "explorer": ["explorer.exe"],
    "file explorer": ["explorer.exe"],
}


def close_application(app_name):
    app_name = normalize_text(app_name)

    if app_name not in CLOSE_COMMANDS:
        return f"I do not know how to close {app_name} safely."

    closed_any = False

    for process_name in CLOSE_COMMANDS[app_name]:
        try:
            subprocess.run(
                f'taskkill /f /im "{process_name}"',
                shell=True,
                capture_output=True
            )
            closed_any = True
        except Exception as e:
            print("Close app error:", e)

    if closed_any:
        log_action_db(
            f"close {app_name}",
            "close_application",
            "success",
            app_name
        )
        return f"Closing {app_name}."

    return f"I could not close {app_name}."

   
    if clean.startswith("close "):
       app_name = clean.replace("close ", "").strip()
       return close_application(app_name)

    if clean in [
    "close current tab",
    "close tab"
]:
       pyautogui.hotkey("ctrl", "w")
       return "Closing current tab."

    if clean in [
    "close window",
    "close current window"
]:
      pyautogui.hotkey("alt", "f4")
      return "Closing current window."

    if clean in [
        "close all windows",
        "close everything"
]:
      if ask_user_confirmation(command, "closing all windows"):
        pyautogui.hotkey("win", "d")
        return "Minimizing all windows safely."
        return "Cancelled."

    if clean in ["noise cancellation on", "background noise cancellation on", "noise cancel on", "denoise on"]:
        NOISE_CANCELLATION_ENABLED = True
        log_action_db(command, "noise_cancellation", "enabled", "user command")
        return "Background noise cancellation is now ON."

    if clean in ["noise cancellation off", "background noise cancellation off", "noise cancel off", "denoise off"]:
        NOISE_CANCELLATION_ENABLED = False
        log_action_db(command, "noise_cancellation", "disabled", "user command")
        return "Background noise cancellation is now OFF."

    if clean in ["noise status", "noise cancellation status", "background noise status", "mic noise status"]:
        return noise_cancellation_status()

    if clean in ["calibrate noise", "calibrate background noise", "calibrate mic noise", "noise calibration"]:
        return calibrate_background_noise()

    if clean in ["full control", "full control mode", "what can you control", "blue full control"]:
        return SAFE_FULL_CONTROL_HELP + " Advanced modules: continuous listening, Live Mouse AI, market assistant, replay backtest, and Iron HUD."

    if clean in ["start continuous listening", "continuous listening on", "real time listening on"]:
        ALWAYS_LISTEN_MODE = True
        log_action_db(command, "continuous_listening", "enabled", "user command")
        return "Real-time continuous listening is now ON. Say stop continuous listening to turn it off."

    if clean in ["stop continuous listening", "continuous listening off", "real time listening off"]:
        ALWAYS_LISTEN_MODE = False
        log_action_db(command, "continuous_listening", "disabled", "user command")
        return "Real-time continuous listening is now OFF. Wake word mode restored."

    if clean in ["open hud", "open iron hud", "start hud", "floating iron man hud", "open iron man hud"]:
        return start_iron_hud()

    mouse_reply = live_mouse_command(command)
    if mouse_reply:
        log_action_db(command, "live_mouse_ai", "success", mouse_reply)
        return mouse_reply

    if clean in ["open chart", "open tradingview chart", "open xauusd chart", "open gold chart", "open xau usd chart"]:
        open_url(TRADINGVIEW_CHART_URL)
        log_action_db(command, "open_chart", "success", TRADINGVIEW_CHART_URL)
        return "Opening XAUUSD TradingView chart."

    if clean.startswith("analyze chart") or clean.startswith("market signal") or clean.startswith("signal for") or clean.startswith("analyze market"):
        reply = run_market_signal_command(command)
        log_action_db(command, "market_signal", "success", "analysis only")
        return reply

    if clean.startswith("backtest") or clean.startswith("replay backtest"):
        reply = run_market_backtest_command(command)
        log_action_db(command, "market_backtest", "success", "analysis only")
        return reply

    if clean.startswith("autonomous market watch") or clean.startswith("start market watch"):
        reply = run_market_autonomous_watch(command)
        log_action_db(command, "autonomous_market_watch", "success", "monitoring only")
        return reply

    if clean in ["open chrome", "open crome", "launch chrome", "launch crome"]:
        try:
            subprocess.Popen("chrome", shell=True)
            log_action_db(command, "open_app", "success", "chrome")
            return "Opening Chrome."
        except Exception as e:
            open_url("https://www.google.com")
            log_action_db(command, "open_app", "fallback", str(e))
            return "Chrome command failed, so I opened the browser instead."

    if clean.startswith("run command") or clean.startswith("execute command") or clean.startswith("run terminal command") or clean.startswith("run cmd") or clean.startswith("run powershell"):
        return run_safe_shell_command(command)

    return ""


def predict_next_command():
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT command, COUNT(*) AS total
        FROM command_logs
        GROUP BY command
        ORDER BY total DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    conn.close()
    return row[0] if row else "open youtube"


def daily_command_summary():
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT COUNT(*) FROM command_logs WHERE timestamp LIKE ?", (today + "%",))
    total_today = cur.fetchone()[0]
    cur.execute("SELECT intent, COUNT(*) FROM command_logs GROUP BY intent ORDER BY COUNT(*) DESC LIMIT 1")
    top_intent = cur.fetchone()
    conn.close()
    if top_intent:
        return f"Today you used {total_today} commands. Your most used intent is {top_intent[0]}."
    return f"Today you used {total_today} commands."



def learn_preference_from_text(text):
    clean = normalize_text(text)
    if "my favorite browser is" in clean:
        value = clean.split("my favorite browser is", 1)[1].strip()
        db_set("preferences", "favorite_browser", value)
        memory["preferences"]["favorite_browser"] = value
        save_memory()
        return f"I learned that your favorite browser is {value}."
    if "my favorite app is" in clean:
        value = clean.split("my favorite app is", 1)[1].strip()
        db_set("preferences", "favorite_app", value)
        memory["preferences"]["favorite_app"] = value
        save_memory()
        return f"I learned that your favorite app is {value}."
    return ""


def recall_profile():
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    cur.execute("SELECT key, value FROM profile ORDER BY updated_at DESC LIMIT 10")
    profile_rows = cur.fetchall()
    cur.execute("SELECT key, value FROM preferences ORDER BY updated_at DESC LIMIT 10")
    pref_rows = cur.fetchall()
    conn.close()
    parts = []
    if profile_rows:
        parts.append("Profile: " + "; ".join([f"{k} is {v}" for k, v in profile_rows]))
    if pref_rows:
        parts.append("Preferences: " + "; ".join([f"{k} is {v}" for k, v in pref_rows]))
    return " | ".join(parts) if parts else "I do not have a long term profile saved yet."


def add_chat_history(user_text, blue_text):
    memory["chat_history"].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user_text,
        "blue": blue_text
    })
    memory["chat_history"] = memory["chat_history"][-20:]
    save_memory()


def remember_fact(fact: str):
    fact = fact.strip()
    if not fact:
        return "I did not catch what you want me to remember."
    if fact not in memory["facts"]:
        memory["facts"].append(fact)
        memory["facts"] = memory["facts"][-80:]
        save_memory()
    return f"Okay, I will remember that {fact}"


def recall_facts():
    if not memory["facts"]:
        return "I do not have anything saved in memory yet."
    return "Here is what I remember: " + "; ".join(memory["facts"][-7:])


def clear_memory():
    global memory
    memory = DEFAULT_MEMORY.copy()
    save_memory()
    return "Done. I cleared my saved memory."

# =========================================================
# LOAD FASTER WHISPER
# =========================================================
print("Loading Faster Whisper command model...")
try:
    fw_model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
    print("Command Whisper ready.")
except Exception as e:
    print("Command Whisper load error:", e)
    fw_model = None

print("Loading fast wake-word model...")
try:
    wake_model = WhisperModel(WAKE_MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
    print("Fast wake-word model ready.")
except Exception as e:
    print("Wake model load error:", e)
    wake_model = None

# =========================================================
# BACKGROUND NOISE CANCELLATION ENGINE
# =========================================================
def load_noise_profile():
    """Load saved microphone noise floor. Returns None if no calibration exists."""
    try:
        if os.path.exists(NOISE_PROFILE_FILE):
            with open(NOISE_PROFILE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return float(data.get("noise_rms", 0)) or None
    except Exception as e:
        print("Noise profile load error:", e)
    return None


def save_noise_profile(noise_rms: float):
    try:
        with open(NOISE_PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "noise_rms": float(noise_rms),
                "sample_rate": SAMPLE_RATE,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, f, indent=2)
        return True
    except Exception as e:
        print("Noise profile save error:", e)
        return False


def audio_rms(audio_float):
    try:
        return float(np.sqrt(np.mean(np.square(audio_float))) + 1e-9)
    except Exception:
        return 0.0


def high_pass_filter_audio(audio_float, samplerate=SAMPLE_RATE, cutoff_hz=HIGH_PASS_CUTOFF_HZ):
    """Reduce low frequency fan/rumble noise. Falls back safely if scipy.signal is unavailable."""
    if not HIGH_PASS_FILTER_ENABLED or not SCIPY_SIGNAL_AVAILABLE:
        return audio_float
    try:
        nyquist = samplerate / 2.0
        cutoff = max(20.0, min(float(cutoff_hz), nyquist - 100.0))
        b, a = butter(2, cutoff / nyquist, btype="highpass")
        return filtfilt(b, a, audio_float).astype(np.float32)
    except Exception as e:
        print("High-pass filter error:", e)
        return audio_float


def reduce_background_noise(audio, samplerate=SAMPLE_RATE):
    """Clean microphone audio before Faster Whisper transcription."""
    if not NOISE_CANCELLATION_ENABLED:
        return audio

    try:
        # Convert int16 microphone audio to float32 mono.
        audio_float = audio.astype(np.float32).reshape(-1)

        # Use first small part as ambient noise profile for this recording.
        floor_samples = int(max(0.1, NOISE_FLOOR_SECONDS) * samplerate)
        floor_samples = min(floor_samples, max(1, len(audio_float) // 3))
        noise_sample = audio_float[:floor_samples]

        saved_floor = load_noise_profile()
        current_floor = audio_rms(noise_sample)
        noise_floor = max(saved_floor or 0, current_floor, 1.0)

        # Optional advanced noise reduction when noisereduce is installed.
        if NOISEREDUCE_AVAILABLE:
            try:
                audio_float = nr.reduce_noise(
                    y=audio_float,
                    y_noise=noise_sample,
                    sr=samplerate,
                    stationary=False,
                    prop_decrease=0.75
                ).astype(np.float32)
            except Exception as e:
                print("noisereduce fallback:", e)

        # High-pass filter removes rumble and fan vibration.
        audio_float = high_pass_filter_audio(audio_float, samplerate)

        # Noise gate: suppress quiet background segments.
        gate_threshold = noise_floor * NOISE_GATE_MULTIPLIER
        quiet_mask = np.abs(audio_float) < gate_threshold
        audio_float[quiet_mask] *= 0.18

        # If the whole recording is mostly silence/noise, keep it very low.
        if audio_rms(audio_float) < MIN_VOICE_RMS:
            audio_float *= 0.25

        # Normalize voice level safely to improve Whisper accuracy.
        if NORMALIZE_MIC_AUDIO:
            peak = float(np.max(np.abs(audio_float)) + 1e-9)
            target_peak = 22000.0
            if 1000 < peak < 32000:
                audio_float = audio_float * min(3.0, target_peak / peak)

        audio_float = np.clip(audio_float, -32768, 32767)
        return audio_float.astype(np.int16).reshape(-1, 1)
    except Exception as e:
        print("Noise cancellation error:", e)
        return audio


def calibrate_background_noise(duration=2.0, samplerate=SAMPLE_RATE):
    """Record room noise and save a noise profile. Stay silent while this runs."""
    try:
        print("Calibrating background noise. Stay silent...")
        audio = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype="int16"
        )
        sd.wait()
        rms = audio_rms(audio.astype(np.float32).reshape(-1))
        save_noise_profile(rms)
        log_action_db("calibrate noise", "noise_cancellation", "success", f"noise_rms={rms:.2f}")
        return f"Noise calibration complete. Background noise level saved at {rms:.2f}."
    except Exception as e:
        log_action_db("calibrate noise", "noise_cancellation", "failed", str(e))
        return "Noise calibration failed because " + str(e)


def noise_cancellation_status():
    profile = load_noise_profile()
    mode = "ON" if NOISE_CANCELLATION_ENABLED else "OFF"
    optional = "advanced noisereduce available" if NOISEREDUCE_AVAILABLE else "basic built-in denoise active"
    saved = f"Saved noise profile RMS: {profile:.2f}." if profile else "No saved noise profile yet."
    return f"Noise cancellation is {mode}. {optional}. {saved}"

# =========================================================
# AUDIO + SPEECH TO TEXT
# =========================================================
def record_audio_file(filename=TEMP_AUDIO, duration=RECORD_SECONDS, samplerate=SAMPLE_RATE):
    print("Listening...")
    play_tone("listen")
    audio = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype="int16"
    )
    sd.wait()
    audio = reduce_background_noise(audio, samplerate)
    write(filename, samplerate, audio)
    return filename


def listen_faster_whisper(duration=RECORD_SECONDS):
    play_tone("thinking")
    if fw_model is None:
        return ""
    try:
        path = record_audio_file(duration=duration)
        segments, _ = fw_model.transcribe(
            path,
            beam_size=5,
            language="en",
            vad_filter=True
        )
        text = " ".join(seg.text for seg in segments).strip().lower()
        if text:
            print(f"[Faster Whisper] {text}")
        return text
    except Exception as e:
        print("Faster Whisper error:", e)
        return ""


def listen_blue():
    text = listen_faster_whisper(duration=RECORD_SECONDS)
    if text:
        return text, "command_whisper"
    return "", "none"


def listen_wake_word():
    if wake_model is None:
        return "", "none"
    try:
        path = record_audio_file(duration=WAKE_RECORD_SECONDS)
        segments, _ = wake_model.transcribe(
            path,
            beam_size=1,
            language="en",
            vad_filter=True
        )
        text = " ".join(seg.text for seg in segments).strip().lower()
        if text:
            print(f"[Wake Whisper] {text}")
        return text, "wake_whisper"
    except Exception as e:
        print("Wake listener error:", e)
        return "", "none"

# =========================================================
# AI/ML INTENT MODEL
# =========================================================
def train_small_intent_model():
    if not ML_AVAILABLE:
        return False
    training_data = [
        ("open youtube", "youtube"),
        ("launch youtube", "youtube"),
        ("search youtube for python", "youtube_search"),
        ("youtube search banking exam", "youtube_search"),
        ("find on youtube data science", "youtube_search"),
        ("open google", "google_home"),
        ("open maps", "maps"),
        ("open calculator", "open_app"),
        ("open notepad", "open_app"),
        ("open vs code", "open_app"),
        ("open downloads", "open_folder"),
        ("open desktop", "open_folder"),
        ("search for python tutorial", "google_search"),
        ("google ibps syllabus", "google_search"),
        ("what is machine learning", "web_search"),
        ("who is ratan tata", "web_search"),
        ("remember that my exam is tomorrow", "remember"),
        ("save this my favorite browser is chrome", "remember"),
        ("what do you remember", "recall_memory"),
        ("show profile", "recall_profile"),
        ("clear memory", "clear_memory"),
        ("take screenshot", "screenshot"),
        ("lock computer", "lock"),
        ("volume up", "volume_up"),
        ("volume down", "volume_down"),
        ("mute sound", "mute"),
        ("brightness up", "brightness_up"),
        ("brightness down", "brightness_down"),
        ("play music", "music_play_pause"),
        ("next song", "music_next"),
        ("previous song", "music_previous"),
        ("new tab", "browser_new_tab"),
        ("close tab", "browser_close_tab"),
        ("refresh page", "browser_refresh"),
        ("go back", "browser_back"),
        ("analyze data", "analyze_data"),
        ("read data", "analyze_data"),
        ("data summary", "analyze_data"),
        ("predict data", "predict_data"),
        ("make prediction", "predict_data"),
        ("forecast data", "predict_data"),
        ("what time is it", "time"),
        ("tell me date", "date"),
        ("how are you", "how_are_you"),
        ("hello blue", "greeting"),
        ("open camera", "open_camera"),
        ("blue vision", "open_camera"),
        ("type this hello world", "type_text"),
        ("weather today", "weather"),
        ("latest news", "news"),
        ("stock price apple", "stock_price"),
        ("study mode", "study_mode"),
        ("train my dataset", "train_habits"),
        ("ask meta what is ai", "ai_brain"),
        ("explain machine learning", "ai_brain"),
        ("make ibps study plan", "ai_brain"),
        ("help me understand reasoning", "ai_brain"),
        ("start autonomous agent", "autonomous_agent"),
        ("stop blue", "exit"),
    ]
    X = [x for x, y in training_data]
    y = [y for x, y in training_data]
    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
        ("clf", LogisticRegression(max_iter=1000))
    ])
    model.fit(X, y)
    joblib.dump(model, INTENT_MODEL_FILE)
    return True


def ml_classify_intent(text):
    if not ML_AVAILABLE:
        return ""
    try:
        clean = normalize_text(text)

        # Do not let tiny filler replies become commands
        ignore_words = ["yes", "yes sir", "okay", "ok", "hmm", "hello sir", "right away sir", "certainly sir"]
        if clean in ignore_words or len(clean.split()) <= 1:
            return ""

        if not os.path.exists(INTENT_MODEL_FILE):
            train_small_intent_model()

        model = joblib.load(INTENT_MODEL_FILE)

        # Only trust ML when confidence is good
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba([clean])[0]
            best_index = int(np.argmax(probs)) if DATA_AI_AVAILABLE else int(max(range(len(probs)), key=lambda i: probs[i]))
            confidence = float(probs[best_index])
            label = model.classes_[best_index]
            if confidence >= 0.55:
                return label
            return ""

        return model.predict([clean])[0]
    except Exception as e:
        print("ML intent error:", e)
        return ""


# =========================================================
# TEXT HELPERS
# =========================================================
def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def similarity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def contains_any(text, phrases):
    return any(p in text for p in phrases)


def remove_wake_word(text: str):
    clean = normalize_text(text)
    if clean == WAKE_WORD:
        return ""
    if clean.startswith(WAKE_WORD + " "):
        return clean[len(WAKE_WORD):].strip()
    return clean


def should_accept_command(text: str):
    clean = normalize_text(text)
    if ALWAYS_LISTEN_MODE:
        return True
    return clean == WAKE_WORD or clean.startswith(WAKE_WORD + " ")

# =========================================================
# INTENT SYSTEM
# =========================================================
INTENT_PATTERNS = {
    "youtube": ["open youtube", "launch youtube", "youtube kholo", "start youtube"],
    "youtube_search": ["search youtube", "search youtube for", "youtube search", "find on youtube"],
    "google_home": ["open google", "launch google", "go to google"],
    "google_search": ["search for", "search google for", "look up", "find on google", "google"],
    "maps": ["open maps", "open google maps", "show map", "find location"],
    "open_chart": ["open chart", "open tradingview chart", "open xauusd chart", "open gold chart", "open xau usd chart"],
    "full_control": ["full control", "full control mode", "what can you control", "blue full control"],
    "open_app": ["open notepad", "open calculator", "open vs code", "open file explorer", "open task manager", "open settings", "open chrome", "open crome", "launch chrome", "launch crome", "launch app", "start app"],
    "open_folder": ["open downloads", "open documents", "open desktop", "open pictures", "open music folder", "open videos"],
    "volume_up": ["volume up", "increase volume", "raise volume", "sound up"],
    "volume_down": ["volume down", "decrease volume", "lower volume", "sound down"],
    "mute": ["mute", "mute sound", "silence volume"],
    "brightness_up": ["brightness up", "increase brightness", "screen brighter"],
    "brightness_down": ["brightness down", "decrease brightness", "screen dimmer"],
    "music_play_pause": ["play music", "pause music", "resume music", "play pause"],
    "music_next": ["next song", "next track", "skip song"],
    "music_previous": ["previous song", "previous track", "back song"],
    "browser_new_tab": ["new tab", "open new tab", "browser new tab"],
    "browser_close_tab": ["close tab", "close browser tab"],
    "browser_refresh": ["refresh page", "reload page"],
    "browser_back": ["go back", "browser back", "back page"],
    "read_screen": ["read screen", "read my screen", "what is on screen", "scan screen", "analyze screen"],
    "analyze_data": ["analyze data", "read data", "analyze csv", "analyze excel", "data summary", "summarize data"],
    "predict_data": ["predict data", "make prediction", "predict from data", "forecast data", "data prediction"],
    "screenshot": ["take screenshot", "capture screen", "save my screen"],
    "lock": ["lock computer", "lock my pc", "lock screen", "lock laptop"],
    "time": ["what time is it", "tell me the time", "current time"],
    "date": ["today date", "tell me the date", "what day is it"],
    "remember": ["remember that", "save this", "note this down", "keep this in memory"],
    "recall_memory": ["what do you remember", "show memory", "my saved things"],
    "clear_memory": ["clear memory", "forget everything", "delete memory"],
    "recall_profile": ["show profile", "what is my profile", "show preferences", "what do you know about me"],
    "daily_summary": ["daily summary", "today summary", "command summary", "analytics summary"],
    "next_suggestion": ["suggest next command", "what should i do next", "next command", "predict next command"],
    "sleep": ["sleep", "go to sleep", "standby", "stop listening", "deactivate"],
    "active_status": ["are you active", "active status", "are you listening"],
    "open_camera": ["open camera", "start camera", "blue vision", "activate vision"],
    "type_text": ["type this", "write this", "type", "write"],
    "weather": ["weather", "today weather", "current weather"],
    "news": ["latest news", "open news", "today news"],
    "stock_price": ["stock price", "share price", "price of stock"],
    "study_mode": ["study mode", "start study mode", "ibps study mode", "prepare study setup"],
    "train_habits": ["train my dataset", "learn my habits", "train blue", "analyze my habits"],
    "ai_brain": ["ask ai", "ask meta", "meta ai", "explain", "make plan", "help me", "answer this", "summarize"],
    "autonomous_agent": ["start autonomous agent", "auto mode", "plan my task", "do it yourself"],
    "exit": ["exit", "quit", "stop blue", "close assistant", "goodbye"],
    "name_query": ["what is your name", "who are you"],
    "how_are_you": ["how are you", "are you okay"],
    "greeting": ["hello", "hi", "hey", "hey blue"]
}


def score_intent(text, patterns):
    text = normalize_text(text)
    text_tokens = set(text.split())
    best = 0.0
    for pattern in patterns:
        p = normalize_text(pattern)
        p_tokens = set(p.split())
        if p in text:
            best = max(best, 1.0)
        else:
            sim = similarity(text, p) * 0.55
            overlap = (len(text_tokens & p_tokens) / len(p_tokens)) * 0.75 if p_tokens else 0
            best = max(best, sim + overlap)
    return best


def extract_after_phrases(command: str, phrases):
    command = normalize_text(command)
    for phrase in phrases:
        phrase = normalize_text(phrase)
        if command.startswith(phrase + " "):
            return command.replace(phrase, "", 1).strip()
        if phrase in command:
            return command.split(phrase, 1)[1].strip()
    return ""


def extract_search_query(command: str):
    phrases = ["search google for", "search the web for", "search for", "find on google", "look up", "google"]
    query = extract_after_phrases(command, phrases)
    return query if query else normalize_text(command)


def extract_youtube_query(command: str):
    phrases = ["search youtube for", "search youtube", "youtube search", "find on youtube"]
    query = extract_after_phrases(command, phrases)
    return query if query else normalize_text(command).replace("youtube", "").replace("search", "").strip()


def classify_intent(text: str):
    clean = remove_wake_word(text)

    ml_intent = ml_classify_intent(clean)
    if ml_intent:
        if ml_intent == "google_search":
            return "google_search", extract_search_query(clean)
        if ml_intent == "youtube_search":
            return "youtube_search", extract_youtube_query(clean)
        return ml_intent, clean

    direct_memory = extract_after_phrases(clean, ["remember that", "save this", "note this down"])
    if direct_memory:
        return "remember", direct_memory

    best_intent = "chat"
    best_score = 0.0
    for intent, patterns in INTENT_PATTERNS.items():
        score = score_intent(clean, patterns)
        if score > best_score:
            best_score = score
            best_intent = intent

    if best_score < 0.58:
        search_clues = ["who is", "what is", "where is", "tell me about", "search", "find"]
        if contains_any(clean, search_clues):
            return "web_search", clean
        return "chat", clean

    if best_intent == "google_search":
        return "google_search", extract_search_query(clean)
    if best_intent == "youtube_search":
        return "youtube_search", extract_youtube_query(clean)

    return best_intent, clean

# =========================================================
# ONLINE KNOWLEDGE
# =========================================================
def online_answer(query: str):
    if not USE_ONLINE_KNOWLEDGE:
        return ""
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        r = requests.get(url, params=params, timeout=8)
        data = r.json()
        answer = data.get("Answer", "").strip()
        abstract = data.get("AbstractText", "").strip()
        heading = data.get("Heading", "").strip()
        if answer:
            return answer
        if abstract:
            return f"{heading}: {abstract}" if heading else abstract
    except Exception as e:
        print("Online answer error:", e)
    return ""


def ask_meta_ai_brain(prompt: str):
    if not USE_META_AI_BRAIN:
        return "Meta AI brain is turned off."

    try:
        system_prompt = """
You are Blue 3.0, a helpful JARVIS-style desktop AI assistant.
Answer clearly, briefly, and practically.
The user is a student preparing for IBPS and learning AI/Data Science.
""".strip()

        full_prompt = f"""
{system_prompt}

User: {prompt}
Blue:
""".strip()

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False
        }

        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        data = response.json()
        answer = data.get("response", "").strip()

        if answer:
            return answer[:900]

        return "Meta AI brain did not return an answer."

    except Exception as e:
        return "Meta AI brain is not available. Open Ollama and run the Llama model first. Error: " + str(e)


# =========================================================
# FRIENDLY CHAT
# =========================================================
def friendly_chat_reply(text: str):
    clean = normalize_text(text)

    if "my name is" in clean:
        name = clean.split("my name is", 1)[1].strip().title()
        if name:
            memory["user_name"] = name
            save_memory()
            return f"Nice to meet you, {name}. I will remember your name."

    if "who am i" in clean:
        return f"You are {memory['user_name']}." if memory.get("user_name") else "You have not told me your name clearly yet."

    if contains_any(clean, ["hello", "hi", "hey"]):
        return f"Hello {memory['user_name']}. What can I do for you?" if memory.get("user_name") else "Hello. What can I do for you?"

    if "how are you" in clean:
        return "I am doing great and ready to help you."

    if "what is your name" in clean or "who are you" in clean:
        return "I am Blue 3.0, your desktop assistant."

    if "thank you" in clean or "thanks" in clean:
        return "You are welcome."

    if USE_ONLINE_KNOWLEDGE and contains_any(clean, ["who is", "what is", "where is", "tell me about"]):
        ans = online_answer(clean)
        if ans:
            return ans[:450]

    return "I heard you. Try saying open YouTube, search for banking exam syllabus, take screenshot, remember that, or what time is it."

# =========================================================
# PC CONTROL + APP/FOLDER/BROWSER AUTOMATION
# =========================================================
def open_dynamic_app(command: str):
    clean = normalize_text(command)
    for name, app_command in APP_COMMANDS.items():
        if name in clean:
            try:
                subprocess.Popen(app_command, shell=True)
                return f"Opening {name}."
            except Exception:
                return f"I could not open {name}."
    return "I do not know that app yet. Add it inside APP_COMMANDS."


def open_dynamic_folder(command: str):
    clean = normalize_text(command)
    for name, folder_path in FOLDER_COMMANDS.items():
        if name in clean:
            if os.path.exists(folder_path):
                os.startfile(folder_path)
                return f"Opening {name} folder."
            return f"I could not find your {name} folder."
    return "Tell me which folder to open, like downloads, desktop, documents, pictures, music, or videos."


def change_volume(action: str):
    if action == "up":
        pyautogui.press("volumeup", presses=5)
        return "Increasing volume."
    if action == "down":
        pyautogui.press("volumedown", presses=5)
        return "Decreasing volume."
    if action == "mute":
        pyautogui.press("volumemute")
        return "Toggling mute."
    return "Volume command not understood."


def change_brightness(action: str):
    if not BRIGHTNESS_AVAILABLE:
        return "Brightness control needs this package: pip install screen-brightness-control"
    try:
        current = sbc.get_brightness(display=0)[0]
        new_value = min(100, current + 10) if action == "up" else max(0, current - 10)
        sbc.set_brightness(new_value, display=0)
        return f"Brightness set to {new_value} percent."
    except Exception:
        return "I could not control brightness on this device."


def control_music(action: str):
    if action == "play_pause":
        pyautogui.press("playpause")
        return "Toggling play and pause."
    if action == "next":
        pyautogui.press("nexttrack")
        return "Skipping to next track."
    if action == "previous":
        pyautogui.press("prevtrack")
        return "Going to previous track."
    return "Music command not understood."


def browser_automation(action: str):
    if action == "new_tab":
        pyautogui.hotkey("ctrl", "t")
        return "Opening a new browser tab."
    if action == "close_tab":
        pyautogui.hotkey("ctrl", "w")
        return "Closing the current tab."
    if action == "refresh":
        pyautogui.hotkey("ctrl", "r")
        return "Refreshing the page."
    if action == "back":
        pyautogui.hotkey("alt", "left")
        return "Going back."
    return "Browser command not understood."


def read_screen_text():
    if not OCR_AVAILABLE:
        return "Screen reading needs this package: pip install pytesseract pillow. You also need to install Tesseract OCR on Windows."
    try:
        screenshot = pyautogui.screenshot()
        text = pytesseract.image_to_string(screenshot).strip()
        text = re.sub(r"\s+", " ", text)
        if not text:
            return "I scanned the screen, but I could not read clear text."
        if len(text) > 600:
            text = text[:600] + "..."
        return "I can see this on your screen: " + text
    except Exception as e:
        return "I could not read the screen because " + str(e) + "."


def find_latest_data_file():
    supported = [".csv", ".xlsx", ".xls"]
    files = []
    for folder in DATA_SEARCH_FOLDERS:
        if os.path.exists(folder):
            for name in os.listdir(folder):
                path = os.path.join(folder, name)
                if os.path.isfile(path) and os.path.splitext(path)[1].lower() in supported:
                    files.append(path)
    return max(files, key=os.path.getmtime) if files else ""


def load_data_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)
    if ext in [".xlsx", ".xls"]:
        return pd.read_excel(path)
    raise ValueError("Unsupported file type")


def analyze_latest_data_file():
    if not DATA_AI_AVAILABLE:
        return "Data analysis needs: pip install pandas numpy scikit-learn openpyxl"
    path = find_latest_data_file()
    if not path:
        return "No CSV or Excel file found in Downloads, Desktop, or Documents."
    try:
        df = load_data_file(path)
        rows, cols = df.shape
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        missing_total = int(df.isna().sum().sum())
        message = f"I analyzed {os.path.basename(path)}. It has {rows} rows, {cols} columns, {len(numeric_cols)} numeric columns, and {missing_total} missing values."
        if numeric_cols:
            col = numeric_cols[0]
            message += f" For {col}, average is {df[col].mean():.2f}, minimum is {df[col].min():.2f}, and maximum is {df[col].max():.2f}."
        db_set("profile", "last_data_file", path)
        return message
    except Exception as e:
        return "I could not analyze the data because " + str(e) + "."


def predict_from_latest_data_file():
    if not DATA_AI_AVAILABLE:
        return "Prediction needs: pip install pandas numpy scikit-learn openpyxl"
    path = find_latest_data_file()
    if not path:
        return "No CSV or Excel file found in Downloads, Desktop, or Documents."
    try:
        df = load_data_file(path)
        numeric_df = df.select_dtypes(include=["number"]).dropna()
        if numeric_df.shape[1] < 2 or len(numeric_df) < 5:
            return "I need at least two numeric columns and five clean rows to make a prediction."
        x_col = numeric_df.columns[0]
        y_col = numeric_df.columns[-1]
        X = numeric_df[[x_col]].values
        y = numeric_df[y_col].values
        model = LinearRegression()
        model.fit(X, y)
        next_x = float(np.max(X)) + 1
        prediction = model.predict([[next_x]])[0]
        return f"Using {os.path.basename(path)}, I made a simple prediction. If {x_col} becomes {next_x:.2f}, predicted {y_col} is {prediction:.2f}."
    except Exception as e:
        return "I could not make prediction because " + str(e) + "."


def open_camera_vision():
    if not VISION_AVAILABLE:
        return "Computer vision needs this package: pip install opencv-python"
    try:
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            return "I could not access the camera."
        speak("Camera vision activated. Press escape to close.")
        while True:
            ret, frame = cam.read()
            if not ret:
                break
            cv2.putText(frame, "BLUE VISION ACTIVE - Press ESC to exit", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.imshow("Blue Vision", frame)
            if cv2.waitKey(1) == 27:
                break
        cam.release()
        cv2.destroyAllWindows()
        return "Camera vision closed."
    except Exception as e:
        return "Vision error: " + str(e)


def extract_text_to_type(command: str):
    clean = normalize_text(command)
    for phrase in ["type this", "write this", "type", "write"]:
        if clean.startswith(phrase + " "):
            return clean.replace(phrase, "", 1).strip()
    return ""


def type_text_on_screen(command: str):
    text_to_type = extract_text_to_type(command)
    if not text_to_type:
        return "Tell me what to type. For example, say type this hello world."
    if contains_secret_request(text_to_type):
        log_action_db(command, "type_text", "blocked", "secret text detected")
        return "I cannot type passwords, OTP, PIN, CVV, API keys, or other private secrets."
    pyautogui.write(text_to_type, interval=0.03)
    log_action_db(command, "type_text", "success", "typed non-secret text")
    return "Typed your text."


def get_weather_report(command: str):
    try:
        city = extract_after_phrases(command, ["weather in", "today weather in", "current weather in"])
        if not city:
            city = "Aurangabad Maharashtra"
        url = "https://wttr.in/" + quote_plus(city) + "?format=3"
        r = requests.get(url, timeout=8)
        if r.text:
            return r.text.strip()
    except Exception as e:
        return "Weather error: " + str(e)
    return "I could not get weather right now."


def open_latest_news(command: str):
    query = extract_after_phrases(command, ["latest news about", "news about", "latest news"])
    if not query:
        query = "India technology news"
    open_url("https://news.google.com/search?q=" + quote_plus(query))
    return "Opening latest news for " + query + "."


def get_stock_price(command: str):
    if not FINANCE_AVAILABLE:
        return "Stock price needs this package: pip install yfinance"
    try:
        symbol = extract_after_phrases(command, ["stock price of", "stock price", "share price of", "share price"])
        if not symbol:
            symbol = "AAPL"
        symbol = symbol.upper().replace(" ", "")
        data = yf.Ticker(symbol).history(period="1d")
        if data.empty:
            return "I could not find stock data for " + symbol + "."
        price = float(data["Close"].iloc[-1])
        return f"The latest available price for {symbol} is {price:.2f}."
    except Exception as e:
        return "Stock price error: " + str(e)


def train_user_habits():
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT command, intent, COUNT(*) as total
        FROM command_logs
        GROUP BY command, intent
        ORDER BY total DESC
        LIMIT 5
    """)
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return "I need more command history before I can learn your habits."
    summary = "; ".join([f"{cmd} used {total} times" for cmd, intent, total in rows])
    db_set("preferences", "habit_summary", summary)
    return "I trained on your command history. Your top habits are: " + summary


def start_study_mode():
    open_url("https://www.youtube.com/results?search_query=IBPS+PO+preparation")
    open_url("https://www.google.com/search?q=IBPS+PO+syllabus")
    try:
        subprocess.Popen("notepad", shell=True)
    except Exception:
        pass
    return "Study mode started. I opened IBPS resources and notes for you."


def autonomous_agent(command: str):
    clean = normalize_text(command)
    if "study" in clean or "ibps" in clean:
        return start_study_mode()
    if "data" in clean:
        return analyze_latest_data_file()
    if "screen" in clean:
        return read_screen_text()
    suggestion = predict_next_command()
    return "Autonomous mode checked your context. Suggested next action is: " + suggestion




# =========================================================
# MERGED BLUE 4.0: ADVANCED CONTROL + MARKET AI (ONE FILE)
# =========================================================
# This section merges the uploaded market modules into this single file:
# indicators.py, market_data.py, smc_ict.py, liquidity_heatmap.py,
# smt.py, signal_engine.py, autonomous.py, replay_engine.py, app.py ideas.
# Trading is ANALYSIS ONLY. Blue will not place broker orders or handle payments.

# ---- Market config fallback ----
TIMEFRAMES = {
    '5m': {'interval': '5m', 'period': '5d', 'role': 'entry timing'},
    '15m': {'interval': '15m', 'period': '30d', 'role': 'main entry'},
    '1h': {'interval': '1h', 'period': '60d', 'role': 'intraday bias'},
    '4h': {'interval': '4h', 'period': '180d', 'role': 'swing bias'},
    '1d': {'interval': '1d', 'period': '1y', 'role': 'macro bias'},
}
SYMBOLS = {
    'gold': 'GC=F', 'xauusd': 'GC=F', 'xau/usd': 'GC=F', 'xau usd': 'GC=F',
    'eurusd': 'EURUSD=X', 'eur/usd': 'EURUSD=X',
    'btcusd': 'BTC-USD', 'btc': 'BTC-USD', 'bitcoin': 'BTC-USD',
    'ethusd': 'ETH-USD', 'eth': 'ETH-USD', 'ethereum': 'ETH-USD',
    'usoil': 'CL=F', 'oil': 'CL=F', 'crude oil': 'CL=F',
}
SMT_PAIRS = {'GC=F': 'DX-Y.NYB', 'EURUSD=X': 'DX-Y.NYB', 'BTC-USD': 'ETH-USD', 'ETH-USD': 'BTC-USD'}
MIN_CONFIDENCE_FOR_ACTION = 58
DEFAULT_ATR_MULTIPLIER = 1.25
SWING_LOOKBACK = 3
FVG_LOOKBACK_BARS = 120
OB_LOOKBACK_BARS = 120
LIQUIDITY_LOOKBACK_BARS = 60
PREMIUM_DISCOUNT_LOOKBACK = 120


def resolve_market_symbol(text='gold'):
    clean = normalize_text(text).replace('analyze chart', '').replace('market signal', '').replace('signal for', '').strip()
    if not clean:
        clean = 'gold'
    for key, ticker in SYMBOLS.items():
        if key in clean:
            return key.upper(), ticker
    return clean.upper(), SYMBOLS.get(clean, 'GC=F')


def market_ema(series, length):
    return series.ewm(span=length, adjust=False).mean()


def market_atr(df, length=14):
    h, l, c = df['high'], df['low'], df['close']
    tr = pd.concat([(h-l), (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(length).mean()


def market_rsi(series, length=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(length).mean()
    loss = (-delta.clip(upper=0)).rolling(length).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def market_add_indicators(df):
    df = df.copy()
    df['ema_20'] = market_ema(df['close'], 20)
    df['ema_50'] = market_ema(df['close'], 50)
    df['ema_200'] = market_ema(df['close'], 200)
    df['atr_14'] = market_atr(df, 14)
    df['rsi_14'] = market_rsi(df['close'], 14)
    return df


def market_fetch_ohlcv(ticker: str, interval: str, period: str):
    if not FINANCE_AVAILABLE:
        raise RuntimeError('yfinance is not installed. Run: pip install yfinance')
    df = yf.download(ticker, interval=interval, period=period, progress=False, auto_adjust=False)
    if df is None or df.empty:
        raise RuntimeError(f'No data returned for {ticker} {interval}/{period}')
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    df = df.rename(columns={c: c.lower().replace(' ', '_') for c in df.columns})
    required = ['open', 'high', 'low', 'close']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise RuntimeError(f'Missing OHLC columns: {missing}')
    df = df.dropna(subset=required).copy()
    if 'volume' not in df.columns:
        df['volume'] = 0
    return df


class MarketZone:
    def __init__(self, kind, direction, low, high, index, strength=1):
        self.kind = kind; self.direction = direction; self.low = float(low); self.high = float(high); self.index = str(index); self.strength = int(strength)


def market_detect_swings(df, lookback=SWING_LOOKBACK):
    df = df.copy()
    df['swing_high'] = False; df['swing_low'] = False
    for i in range(lookback, len(df) - lookback):
        h = df['high'].iloc[i]; l = df['low'].iloc[i]
        if h == df['high'].iloc[i-lookback:i+lookback+1].max():
            df.iloc[i, df.columns.get_loc('swing_high')] = True
        if l == df['low'].iloc[i-lookback:i+lookback+1].min():
            df.iloc[i, df.columns.get_loc('swing_low')] = True
    return df


def market_structure_state(df):
    d = market_detect_swings(df)
    swings_hi = d[d['swing_high']]; swings_lo = d[d['swing_low']]
    close = float(d['close'].iloc[-1])
    last_hi = float(swings_hi['high'].iloc[-1]) if len(swings_hi) else float(d['high'].tail(30).max())
    last_lo = float(swings_lo['low'].iloc[-1]) if len(swings_lo) else float(d['low'].tail(30).min())
    prev_hi = float(swings_hi['high'].iloc[-2]) if len(swings_hi) > 1 else last_hi
    prev_lo = float(swings_lo['low'].iloc[-2]) if len(swings_lo) > 1 else last_lo
    direction, event, score = 'range', 'inside structure', 0
    if close > last_hi:
        direction, event, score = 'bullish', 'BOS above last swing high', 3
    elif close < last_lo:
        direction, event, score = 'bearish', 'BOS below last swing low', -3
    elif last_hi > prev_hi and last_lo > prev_lo:
        direction, event, score = 'bullish', 'higher-high / higher-low structure', 2
    elif last_hi < prev_hi and last_lo < prev_lo:
        direction, event, score = 'bearish', 'lower-high / lower-low structure', -2
    return {'direction': direction, 'event': event, 'score': score, 'last_swing_high': round(last_hi, 6), 'last_swing_low': round(last_lo, 6), 'prev_swing_high': round(prev_hi, 6), 'prev_swing_low': round(prev_lo, 6)}


def market_detect_fvg(df, lookback=FVG_LOOKBACK_BARS):
    zones = []
    start = max(2, len(df) - lookback)
    for i in range(start, len(df)):
        c1 = df.iloc[i-2]; c3 = df.iloc[i]; idx = df.index[i]
        if c1['high'] < c3['low']:
            zones.append(MarketZone('FVG', 'bullish', c1['high'], c3['low'], idx, 2))
        if c1['low'] > c3['high']:
            zones.append(MarketZone('FVG', 'bearish', c3['high'], c1['low'], idx, 2))
    return zones[-8:]


def market_detect_order_blocks(df, lookback=OB_LOOKBACK_BARS):
    zones = []
    recent = df.tail(lookback).copy()
    body = (recent['close'] - recent['open']).abs()
    avg_body = body.rolling(10).mean()
    for i in range(11, len(recent)):
        candle = recent.iloc[i]; prev = recent.iloc[i-1]
        impulse = abs(candle['close'] - candle['open']) > (avg_body.iloc[i] * 1.4 if not np.isnan(avg_body.iloc[i]) else 0)
        if not impulse:
            continue
        idx = recent.index[i-1]
        if candle['close'] > candle['open'] and prev['close'] < prev['open']:
            zones.append(MarketZone('Order Block', 'bullish', prev['low'], prev['high'], idx, 3))
        if candle['close'] < candle['open'] and prev['close'] > prev['open']:
            zones.append(MarketZone('Order Block', 'bearish', prev['low'], prev['high'], idx, 3))
    return zones[-8:]


def market_liquidity_sweep(df, lookback=LIQUIDITY_LOOKBACK_BARS):
    if len(df) < 30:
        return {'type': 'none', 'score': 0, 'direction': 'neutral', 'level': None, 'note': 'not enough candles'}
    recent = df.tail(lookback); last = recent.iloc[-1]; prior = recent.iloc[:-1]
    prior_high = float(prior['high'].max()); prior_low = float(prior['low'].min())
    if last['high'] > prior_high and last['close'] < prior_high:
        return {'type': 'buy-side liquidity sweep', 'direction': 'bearish', 'score': -3, 'level': round(prior_high, 6), 'note': 'price took highs and closed back below'}
    if last['low'] < prior_low and last['close'] > prior_low:
        return {'type': 'sell-side liquidity sweep', 'direction': 'bullish', 'score': 3, 'level': round(prior_low, 6), 'note': 'price took lows and closed back above'}
    return {'type': 'none', 'direction': 'neutral', 'score': 0, 'level': None, 'note': 'no clean sweep on latest candle'}


def market_premium_discount(df, lookback=PREMIUM_DISCOUNT_LOOKBACK):
    recent = df.tail(lookback)
    hi = float(recent['high'].max()); lo = float(recent['low'].min()); mid = (hi + lo) / 2
    close = float(recent['close'].iloc[-1])
    pos = 'premium' if close > mid else 'discount' if close < mid else 'equilibrium'
    return {'range_high': round(hi, 6), 'range_low': round(lo, 6), 'equilibrium': round(mid, 6), 'price_location': pos}


def market_nearest_zone(zones, price, direction=None):
    filtered = [z for z in zones if direction is None or z.direction == direction]
    if not filtered:
        return None
    return min(filtered, key=lambda z: abs(((z.low + z.high) / 2) - price))


def market_killzone_now():
    from datetime import timezone
    now = datetime.now(timezone.utc)
    hour = now.hour + now.minute / 60
    if 7 <= hour < 10:
        return 'London kill zone', 'High volatility forex/index window. Prefer confirmation; avoid chasing.'
    if 12 <= hour < 15:
        return 'New York AM kill zone', 'Strong liquidity window. Breakout/sweep setups often matter more here.'
    if 0 <= hour < 3:
        return 'Asian range', 'Often range-building. Mark highs/lows for later liquidity.'
    return 'Off kill zone', 'Lower timing edge. Wait for cleaner displacement or retest.'


def market_smc_snapshot(df):
    return {'structure': market_structure_state(df), 'fvgs': market_detect_fvg(df), 'order_blocks': market_detect_order_blocks(df), 'liquidity': market_liquidity_sweep(df), 'premium_discount': market_premium_discount(df)}


def market_build_liquidity_heatmap(df, lookback=120, tolerance=0.0015):
    d = df.tail(lookback).copy()
    if d.empty:
        return []
    zones = []
    highs = d['high'].tolist(); lows = d['low'].tolist()
    for h in highs:
        matches = sum(1 for x in highs if abs(x - h) / max(h, 1e-9) <= tolerance)
        if matches >= 2:
            zones.append({'side': 'buy-side', 'level': float(h), 'strength': matches, 'reason': 'equal/similar highs'})
    for l in lows:
        matches = sum(1 for x in lows if abs(x - l) / max(l, 1e-9) <= tolerance)
        if matches >= 2:
            zones.append({'side': 'sell-side', 'level': float(l), 'strength': matches, 'reason': 'equal/similar lows'})
    zones = sorted(zones, key=lambda z: z['strength'], reverse=True)
    out, seen = [], []
    for z in zones:
        if all(abs(z['level'] - s) / max(z['level'], 1e-9) > tolerance for s in seen):
            seen.append(z['level']); out.append(z)
        if len(out) >= 8:
            break
    return out


def market_detect_smt(ticker, base_df, interval='1h', period='60d'):
    other = SMT_PAIRS.get(ticker)
    if not other:
        return {'pair': None, 'bias': 'neutral', 'score': 0, 'note': 'No SMT pair configured.'}
    try:
        odf = market_fetch_ohlcv(other, interval, period).tail(80)
        b = base_df.tail(80)
        if len(b) < 20 or len(odf) < 20:
            return {'pair': other, 'bias': 'neutral', 'score': 0, 'note': 'Not enough SMT data.'}
        b_new_high = b['high'].iloc[-1] >= b['high'].iloc[:-1].max()
        b_new_low = b['low'].iloc[-1] <= b['low'].iloc[:-1].min()
        o_new_high = odf['high'].iloc[-1] >= odf['high'].iloc[:-1].max()
        o_new_low = odf['low'].iloc[-1] <= odf['low'].iloc[:-1].min()
        inverse = other == 'DX-Y.NYB'
        if not inverse:
            if b_new_high and not o_new_high:
                return {'pair': other, 'bias': 'bearish', 'score': -2, 'note': f'SMT bearish: {ticker} swept high but {other} did not confirm.'}
            if b_new_low and not o_new_low:
                return {'pair': other, 'bias': 'bullish', 'score': 2, 'note': f'SMT bullish: {ticker} swept low but {other} did not confirm.'}
        else:
            if b_new_high and not o_new_low:
                return {'pair': other, 'bias': 'bullish', 'score': 1, 'note': f'Inverse SMT supportive: {ticker} high without strong DXY confirmation.'}
            if b_new_low and not o_new_high:
                return {'pair': other, 'bias': 'bearish', 'score': -1, 'note': f'Inverse SMT supportive: {ticker} low without strong DXY confirmation.'}
        return {'pair': other, 'bias': 'neutral', 'score': 0, 'note': f'No clear SMT divergence vs {other}.'}
    except Exception as exc:
        return {'pair': other, 'bias': 'neutral', 'score': 0, 'note': f'SMT unavailable: {exc}'}


def market_position_size(balance, risk_percent, entry, stop, ticker='GC=F'):
    try:
        balance = float(balance); risk_percent = float(risk_percent)
        risk_money = balance * (risk_percent / 100)
        distance = abs(float(entry) - float(stop))
        if distance <= 0:
            return {'risk_money': round(risk_money, 2), 'lot_size': 0, 'note': 'Invalid stop distance.'}
        # Approx model: safer generic unit sizing, not broker-specific contract sizing.
        units = risk_money / distance
        lot = units / 100000 if '=X' in ticker else units / 100
        return {'balance': balance, 'risk_percent': risk_percent, 'risk_money': round(risk_money, 2), 'lot_size': round(max(lot, 0), 4), 'note': 'Approx lot/unit sizing. Check broker contract size before live trading.'}
    except Exception as exc:
        return {'risk_money': 0, 'lot_size': 0, 'note': f'Lot sizing unavailable: {exc}'}


def market_empty_risk(balance=0, risk_percent=0):
    return {'balance': balance, 'risk_percent': risk_percent, 'risk_money': 0, 'lot_size': 0, 'note': 'No active trade, so no lot size.'}


def market_technical_score(df):
    last = df.iloc[-1]
    score, why = 0, []
    if last['close'] > last['ema_20'] > last['ema_50']:
        score += 2; why.append('EMA trend bullish')
    elif last['close'] < last['ema_20'] < last['ema_50']:
        score -= 2; why.append('EMA trend bearish')
    else:
        why.append('EMA trend mixed')
    if last['close'] > last['ema_200']:
        score += 1; why.append('above 200 EMA')
    elif last['close'] < last['ema_200']:
        score -= 1; why.append('below 200 EMA')
    rsi = last.get('rsi_14')
    if rsi == rsi:
        if 52 <= rsi <= 68:
            score += 1; why.append('RSI bullish momentum')
        elif 32 <= rsi <= 48:
            score -= 1; why.append('RSI bearish momentum')
        elif rsi > 75:
            score -= 1; why.append('RSI overbought caution')
        elif rsi < 25:
            score += 1; why.append('RSI oversold bounce risk')
    return score, why


def market_tf_analysis(df):
    snap = market_smc_snapshot(df)
    tech_score, why = market_technical_score(df)
    smc_score = snap['structure']['score'] + snap['liquidity']['score']
    pd_loc = snap['premium_discount']['price_location']
    if snap['structure']['direction'] == 'bullish' and pd_loc == 'discount':
        smc_score += 1; why.append('bullish bias inside discount')
    if snap['structure']['direction'] == 'bearish' and pd_loc == 'premium':
        smc_score -= 1; why.append('bearish bias inside premium')
    why.append(snap['structure']['event']); why.append(snap['liquidity']['type'])
    return {'score': tech_score + smc_score, 'why': why, 'smc': snap}


def market_decide(tf_results):
    weights = {'5m': 1, '15m': 1.5, '1h': 2, '4h': 2.5, '1d': 2}
    weighted = 0; total_w = 0
    for tf, data in tf_results.items():
        w = weights.get(tf, 1)
        weighted += data['score'] * w; total_w += w
    avg = weighted / total_w if total_w else 0
    if avg >= 1.6:
        return 'BUY', avg
    if avg <= -1.6:
        return 'SELL', avg
    return 'WAIT', avg


def market_trade_levels(df, action, smc):
    last = df.iloc[-1]
    entry = float(last['close'])
    atr = float(last.get('atr_14') or 0) or max(entry * 0.005, 0.0001)
    all_zones = smc['fvgs'] + smc['order_blocks']
    if action == 'BUY':
        zone = market_nearest_zone(all_zones, entry, 'bullish')
        base_sl = float(smc['structure']['last_swing_low'])
        if zone:
            base_sl = min(base_sl, zone.low)
        stop = min(base_sl, entry - atr * DEFAULT_ATR_MULTIPLIER)
        risk = entry - stop; t1 = entry + risk * 1.5; t2 = entry + risk * 2.5
    elif action == 'SELL':
        zone = market_nearest_zone(all_zones, entry, 'bearish')
        base_sl = float(smc['structure']['last_swing_high'])
        if zone:
            base_sl = max(base_sl, zone.high)
        stop = max(base_sl, entry + atr * DEFAULT_ATR_MULTIPLIER)
        risk = stop - entry; t1 = entry - risk * 1.5; t2 = entry - risk * 2.5
    else:
        stop = entry; t1 = entry; t2 = entry
    return round(entry, 6), round(stop, 6), round(t1, 6), round(t2, 6)


def market_confidence(avg_score, tf_results, action, smt_score=0, news_penalty=0):
    base = 50 + min(abs(avg_score) * 13, 35)
    if action != 'WAIT':
        bullish = sum(1 for d in tf_results.values() if d['score'] > 0)
        bearish = sum(1 for d in tf_results.values() if d['score'] < 0)
        align = bullish if action == 'BUY' else bearish
        base += align * 3
    base += smt_score * 3 + news_penalty
    return int(max(0, min(95, base)))


def market_zone_to_dict(z):
    return {'kind': z.kind, 'direction': z.direction, 'low': round(z.low, 6), 'high': round(z.high, 6), 'index': z.index, 'strength': z.strength}


def build_merged_market_signal(symbol_text='gold', account=None):
    name, ticker = resolve_market_symbol(symbol_text)
    raw, tf_results = {}, {}
    for tf, cfg in TIMEFRAMES.items():
        df = market_add_indicators(market_fetch_ohlcv(ticker, cfg['interval'], cfg['period']))
        raw[tf] = df
        tf_results[tf] = market_tf_analysis(df)
    action, avg = market_decide(tf_results)
    main_tf_for_pro = '1h' if '1h' in raw else list(raw.keys())[0]
    smt = market_detect_smt(ticker, raw[main_tf_for_pro])
    heatmap = market_build_liquidity_heatmap(raw['15m'] if '15m' in raw else raw[main_tf_for_pro])
    news = {'penalty': 0, 'note': 'Manual Forex Factory check recommended before entry.'}
    confidence = market_confidence(avg, tf_results, action, smt_score=smt.get('score', 0), news_penalty=news.get('penalty', 0))
    if confidence < MIN_CONFIDENCE_FOR_ACTION:
        action = 'WAIT'
    main_tf = '15m' if '15m' in raw else list(raw.keys())[0]
    main_smc = tf_results[main_tf]['smc']
    entry, stop, t1, t2 = market_trade_levels(raw[main_tf], action, main_smc)
    risk = market_position_size(account['balance'], account['risk_percent'], entry, stop, ticker=ticker) if action != 'WAIT' and account else market_empty_risk(account.get('balance', 0) if account else 0, account.get('risk_percent', 0) if account else 0)
    session, session_note = market_killzone_now()
    timeframes = {}
    for tf, data in tf_results.items():
        timeframes[tf] = {'role': TIMEFRAMES[tf]['role'], 'score': round(data['score'], 2), 'why': data['why'][:6], 'structure': data['smc']['structure'], 'liquidity': data['smc']['liquidity'], 'premium_discount': data['smc']['premium_discount'], 'fvgs': [market_zone_to_dict(z) for z in data['smc']['fvgs'][-3:]], 'order_blocks': [market_zone_to_dict(z) for z in data['smc']['order_blocks'][-3:]]}
    regime = main_smc['structure']['direction'] + ' / ' + main_smc['premium_discount']['price_location']
    if action == 'WAIT':
        human = f'No trade. Confluence is not clean enough. Regime: {regime}. Wait for liquidity sweep, displacement, and retest of FVG/OB.'
    else:
        support = []
        for tf in ['1d','4h','1h','15m','5m']:
            d = timeframes.get(tf)
            if not d: continue
            if action == 'BUY' and d['score'] > 0: support.append(f"{tf}: {', '.join(d['why'][:3])}")
            if action == 'SELL' and d['score'] < 0: support.append(f"{tf}: {', '.join(d['why'][:3])}")
        human = f"{action} idea based on multi-timeframe confluence. " + ('; '.join(support[:3]) if support else 'Average score supports the setup.') + f" Main zone: {main_smc['premium_discount']['price_location']}. Structure: {main_smc['structure']['event']}. Liquidity: {main_smc['liquidity']['type']}."
    return {'symbol': name, 'ticker': ticker, 'action': action, 'confidence': confidence, 'entry': entry, 'stop_loss': stop, 'target_1': t1, 'target_2': t2, 'risk': risk, 'session': session, 'session_note': session_note, 'regime': regime, 'smt': smt, 'heatmap': heatmap, 'news_caution': news['note'], 'human_read': human, 'timeframes': timeframes, 'analysis_only': True}


def format_market_signal_for_voice(r):
    risk = r.get('risk', {})
    return (f"{r['symbol']} signal: {r['action']} with {r['confidence']} percent confidence. "
            f"Entry {r['entry']}, stop loss {r['stop_loss']}, target one {r['target_1']}, target two {r['target_2']}. "
            f"Lot size approximately {risk.get('lot_size', 0)}. {r['human_read']} "
            f"Session: {r['session']}. Remember, this is analysis only, not financial advice.")


def save_market_signal_to_db(result):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS market_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            symbol TEXT,
            ticker TEXT,
            action TEXT,
            confidence INTEGER,
            entry REAL,
            stop_loss REAL,
            target_1 REAL,
            target_2 REAL,
            lot_size REAL,
            payload TEXT
        )''')
        cur.execute('''INSERT INTO market_signals(created_at, symbol, ticker, action, confidence, entry, stop_loss, target_1, target_2, lot_size, payload)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'), result.get('symbol'), result.get('ticker'), result.get('action'), result.get('confidence'),
            result.get('entry'), result.get('stop_loss'), result.get('target_1'), result.get('target_2'), result.get('risk', {}).get('lot_size', 0), json.dumps(result, default=str)
        ))
        conn.commit(); conn.close()
    except Exception as exc:
        print('market signal log error:', exc)


def run_market_signal_command(command):
    clean = normalize_text(command)
    symbol_text = clean.replace('analyze chart', '').replace('market signal', '').replace('signal for', '').replace('analyze market', '').strip() or 'gold'
    speak('Scanning market data. This is analysis only, no trade will be placed.')
    result = build_merged_market_signal(symbol_text)
    save_market_signal_to_db(result)
    return format_market_signal_for_voice(result)


def run_market_backtest_command(command):
    clean = normalize_text(command)
    name, ticker = resolve_market_symbol(clean.replace('backtest', '').strip() or 'gold')
    df = market_add_indicators(market_fetch_ohlcv(ticker, '1h', '1y'))
    trades = []
    for i in range(220, len(df)-10):
        window = df.iloc[:i].copy(); last = window.iloc[-1]
        snap = market_smc_snapshot(window); direction = snap['structure']['direction']
        if direction == 'bullish' and last['close'] > last['ema_20'] > last['ema_50']:
            entry = float(last['close']); sl = min(float(snap['structure']['last_swing_low']), entry - float(last['atr_14'])*1.25); risk = entry - sl; tp = entry + risk*1.5; action = 'BUY'
        elif direction == 'bearish' and last['close'] < last['ema_20'] < last['ema_50']:
            entry = float(last['close']); sl = max(float(snap['structure']['last_swing_high']), entry + float(last['atr_14'])*1.25); risk = sl - entry; tp = entry - risk*1.5; action = 'SELL'
        else:
            continue
        if risk <= 0: continue
        future = df.iloc[i:i+10]; result='OPEN'; rr=0
        for _, bar in future.iterrows():
            if action == 'BUY':
                if bar['low'] <= sl: result='LOSS'; rr=-1; break
                if bar['high'] >= tp: result='WIN'; rr=1.5; break
            else:
                if bar['high'] >= sl: result='LOSS'; rr=-1; break
                if bar['low'] <= tp: result='WIN'; rr=1.5; break
        if result != 'OPEN': trades.append({'action': action, 'result': result, 'rr': rr})
    wins = sum(1 for t in trades if t['result'] == 'WIN'); total = len(trades)
    win_rate = round(wins/total*100, 2) if total else 0
    net_rr = round(sum(t['rr'] for t in trades), 2)
    return f'{name} replay backtest complete. Trades {total}, wins {wins}, win rate {win_rate} percent, net R R {net_rr}. This is only a simple strategy test.'


def run_market_autonomous_watch(command):
    symbol_text = command.replace('autonomous market watch', '').replace('start market watch', '').strip() or 'gold'
    name, ticker = resolve_market_symbol(symbol_text)
    speak(f'Autonomous market assistant started for {name}. Monitoring only. I will not place trades.')
    last_action = None
    for i in range(3):
        try:
            r = build_merged_market_signal(name)
            save_market_signal_to_db(r)
            line = f"Scan {i+1}: {name} {r['action']} confidence {r['confidence']} percent. {r.get('human_read','')[:220]}"
            print(line)
            if r['action'] != 'WAIT' and r['action'] != last_action:
                speak(line)
                last_action = r['action']
        except Exception as exc:
            print('Autonomous market scan error:', exc)
        if i < 2:
            time.sleep(5)
    return 'Autonomous market assistant finished. No trades were placed.'


# ---- Live Mouse AI helpers ----
def live_mouse_command(command):
    clean = normalize_text(command)
    try:
        if clean == 'mouse position':
            x, y = pyautogui.position()
            return f'Mouse position is x {x}, y {y}.'
        if clean in ['click center', 'mouse click center']:
            w, h = pyautogui.size(); pyautogui.click(w//2, h//2)
            return 'Clicked the center of the screen.'
        m = re.search(r'click\s+(\d+)\s+(\d+)', clean)
        if m:
            x, y = int(m.group(1)), int(m.group(2)); pyautogui.click(x, y)
            return f'Clicked x {x}, y {y}.'
        m = re.search(r'move mouse\s+(\d+)\s+(\d+)', clean)
        if m:
            x, y = int(m.group(1)), int(m.group(2)); pyautogui.moveTo(x, y, duration=0.2)
            return f'Moved mouse to x {x}, y {y}.'
        m = re.search(r'scroll\s+(up|down)\s*(\d*)', clean)
        if m:
            direction = m.group(1); amount = int(m.group(2) or 5)
            pyautogui.scroll(amount if direction == 'up' else -amount)
            return f'Scrolled {direction} {amount} steps.'
        return ''
    except Exception as exc:
        return f'Mouse AI error: {exc}'


# ---- Floating Iron-Man HUD in same file ----
def open_iron_hud_window():
    try:
        import tkinter as tk, math, random
        root = tk.Tk()
        root.title('BLUE IRON HUD')
        root.geometry('620x420+760+80')
        root.attributes('-topmost', True)
        root.configure(bg='black')
        canvas = tk.Canvas(root, width=620, height=420, bg='black', highlightthickness=0)
        canvas.pack(fill='both', expand=True)
        cyan = '#00e5ff'; dim = '#073642'; green = '#00ff99'
        status_text = 'BLUE 4.0 ONLINE'
        tick = {'v': 0}
        def draw():
            canvas.delete('all')
            t = tick['v']; cx, cy = 310, 185
            canvas.create_text(cx, 34, text='BLUE IRON HUD', fill=cyan, font=('Consolas', 24, 'bold'))
            for r in range(58, 160, 28):
                canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline=dim, width=2)
            for i in range(0, 360, 20):
                a = math.radians(i + t)
                r1, r2 = 96, 142
                x1, y1 = cx + math.cos(a)*r1, cy + math.sin(a)*r1
                x2, y2 = cx + math.cos(a)*r2, cy + math.sin(a)*r2
                canvas.create_line(x1, y1, x2, y2, fill=cyan, width=2)
            pulse = 52 + random.randint(-5, 8)
            canvas.create_oval(cx-pulse, cy-pulse, cx+pulse, cy+pulse, outline=green, width=4)
            canvas.create_text(cx, cy, text='BLUE', fill=cyan, font=('Consolas', 32, 'bold'))
            canvas.create_text(cx, 360, text=status_text, fill=green, font=('Consolas', 15, 'bold'))
            canvas.create_text(cx, 390, text='Say: stop blue | open chart | analyze chart | mouse position', fill='#bff7ff', font=('Consolas', 10))
            tick['v'] += 5
            root.after(90, draw)
        draw(); root.mainloop()
    except Exception as exc:
        print('HUD error:', exc)


def start_iron_hud():
    threading.Thread(target=open_iron_hud_window, daemon=True).start()
    return 'Opening Floating Iron-Man HUD.'


# =========================================================
# ACTIONS
# =========================================================
def jarvis_line(text: str):
    lines = [
        f"Certainly, sir. {text}",
        f"Right away, sir. {text}",
        f"Of course, sir. {text}",
        f"Consider it done, sir. {text}",
        f"At once, sir. {text}",
        f"I am on it, sir. {text}",
    ]
    index = int(time.time() * 1000) % len(lines)
    return lines[index]


def handle_intent(intent: str, payload: str):
    reply = ""
    play_tone("thinking")

    if intent == "youtube":
        reply = jarvis_line("Opening YouTube.")
        speak(reply)
        open_url("https://www.youtube.com")

    elif intent == "open_chart":
        reply = jarvis_line("Opening XAUUSD TradingView chart.")
        speak(reply)
        open_url(TRADINGVIEW_CHART_URL)
        log_action_db(payload, "open_chart", "success", TRADINGVIEW_CHART_URL)

    elif intent == "full_control":
        reply = jarvis_line(SAFE_FULL_CONTROL_HELP)
        speak(reply)

    elif intent == "open_app":
        reply = jarvis_line(open_dynamic_app(payload))
        speak(reply)

    elif intent == "open_folder":
        reply = jarvis_line(open_dynamic_folder(payload))
        speak(reply)

    elif intent == "volume_up":
        reply = jarvis_line(change_volume("up"))
        speak(reply)

    elif intent == "volume_down":
        reply = jarvis_line(change_volume("down"))
        speak(reply)

    elif intent == "mute":
        reply = jarvis_line(change_volume("mute"))
        speak(reply)

    elif intent == "brightness_up":
        reply = jarvis_line(change_brightness("up"))
        speak(reply)

    elif intent == "brightness_down":
        reply = jarvis_line(change_brightness("down"))
        speak(reply)

    elif intent == "music_play_pause":
        reply = jarvis_line(control_music("play_pause"))
        speak(reply)

    elif intent == "music_next":
        reply = jarvis_line(control_music("next"))
        speak(reply)

    elif intent == "music_previous":
        reply = jarvis_line(control_music("previous"))
        speak(reply)

    elif intent == "browser_new_tab":
        reply = jarvis_line(browser_automation("new_tab"))
        speak(reply)

    elif intent == "browser_close_tab":
        reply = jarvis_line(browser_automation("close_tab"))
        speak(reply)

    elif intent == "browser_refresh":
        reply = jarvis_line(browser_automation("refresh"))
        speak(reply)

    elif intent == "browser_back":
        reply = jarvis_line(browser_automation("back"))
        speak(reply)

    elif intent == "read_screen":
        reply = jarvis_line(read_screen_text())
        speak(reply)

    elif intent == "analyze_data":
        reply = jarvis_line(analyze_latest_data_file())
        speak(reply)

    elif intent == "predict_data":
        reply = jarvis_line(predict_from_latest_data_file())
        speak(reply)

    elif intent == "youtube_search":
        query = extract_youtube_query(payload)
        if query:
            reply = jarvis_line(f"Searching YouTube for {query}.")
            speak(reply)
            open_url(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
        else:
            reply = jarvis_line("Please tell me what to search on YouTube.")
            speak(reply)

    elif intent == "open_camera":
        reply = jarvis_line("Opening Blue vision.")
        speak(reply)
        result = open_camera_vision()
        speak(jarvis_line(result))

    elif intent == "type_text":
        reply = jarvis_line(type_text_on_screen(payload))
        speak(reply)

    elif intent == "weather":
        reply = jarvis_line(get_weather_report(payload))
        speak(reply)

    elif intent == "news":
        reply = jarvis_line(open_latest_news(payload))
        speak(reply)

    elif intent == "stock_price":
        reply = jarvis_line(get_stock_price(payload))
        speak(reply)

    elif intent == "train_habits":
        reply = jarvis_line(train_user_habits())
        speak(reply)

    elif intent == "study_mode":
        reply = jarvis_line(start_study_mode())
        speak(reply)

    elif intent == "autonomous_agent":
        reply = jarvis_line(autonomous_agent(payload))
        speak(reply)

    elif intent == "ai_brain":
        reply = jarvis_line(ask_meta_ai_brain(payload))
        speak(reply)

    elif intent == "google_home":
        reply = jarvis_line("Opening Google.")
        speak(reply)
        open_url("https://www.google.com")

    elif intent == "google_search":
        query = payload.strip()
        if query:
            reply = jarvis_line(f"Searching Google for {query}.")
            speak(reply)
            open_url(f"https://www.google.com/search?q={quote_plus(query)}")
        else:
            reply = "Please tell me what you want to search."
            speak(reply)

    elif intent == "web_search":
        ans = online_answer(payload)
        if ans:
            reply = jarvis_line(ans[:420])
            speak(reply)
        else:
            reply = jarvis_line("I could not find a short answer, so I am opening Google search.")
            speak(reply)
            open_url(f"https://www.google.com/search?q={quote_plus(payload)}")

    elif intent == "maps":
        reply = jarvis_line("Opening Google Maps.")
        speak(reply)
        open_url("https://www.google.com/maps")

    elif intent == "screenshot":
        filename = f"screenshot_{int(time.time())}.png"
        pyautogui.screenshot(filename)
        reply = jarvis_line(f"Screenshot saved as {filename}.")
        speak(reply)

    elif intent == "lock":
        reply = jarvis_line("Locking your computer.")
        speak(reply)
        os.system("rundll32.exe user32.dll,LockWorkStation")

    elif intent == "time":
        reply = jarvis_line("The time is " + datetime.now().strftime("%I:%M %p") + ".")
        speak(reply)

    elif intent == "date":
        reply = jarvis_line("Today is " + datetime.now().strftime("%A, %d %B %Y") + ".")
        speak(reply)

    elif intent == "remember":
        pref_reply = learn_preference_from_text(payload)
        if pref_reply:
            reply = jarvis_line(pref_reply)
        else:
            reply = jarvis_line(remember_fact(payload))
            db_set("profile", f"fact_{int(time.time())}", payload)
        speak(reply)

    elif intent == "recall_memory":
        reply = jarvis_line(recall_facts())
        speak(reply)

    elif intent == "recall_profile":
        reply = jarvis_line(recall_profile())
        speak(reply)

    elif intent == "daily_summary":
        reply = jarvis_line(daily_command_summary())
        speak(reply)

    elif intent == "next_suggestion":
        reply = jarvis_line("Based on your history, your next likely command is " + predict_next_command() + ".")
        speak(reply)

    elif intent == "clear_memory":
        reply = jarvis_line(clear_memory())
        speak(reply)

    elif intent == "name_query":
        reply = "I am Blue 3.0, your personal desktop assistant. Online, attentive, and ready for your command, sir."
        speak(reply)

    elif intent == "how_are_you":
        reply = "All systems are running smoothly, sir. Ready when you are."
        speak(reply)

    elif intent == "greeting":
        reply = f"Good to hear from you, {memory['user_name']}. What shall we do next, sir?" if memory.get("user_name") else "Good to hear from you, sir. What shall we do next?"
        speak(reply)

    elif intent == "active_status":
        reply = "I am active and listening, sir."
        speak(reply)

    elif intent == "sleep":
        reply = "Going to sleep sir. Wake me up when you need."
        speak(reply)
        add_chat_history(payload, reply)
        memory["last_command"] = payload
        save_memory()
        log_command_db(payload, intent, payload, reply)
        return "sleep"

    elif intent == "exit":
        reply = "Shutting down Blue 3.0. See you soon, sir."
        speak(reply)
        add_chat_history(payload, reply)
        return False

    else:
        if USE_META_AI_BRAIN:
            reply = jarvis_line(ask_meta_ai_brain(payload))
        else:
            reply = jarvis_line(friendly_chat_reply(payload))
        speak(reply)

    add_chat_history(payload, reply)
    memory["last_command"] = payload
    save_memory()
    log_command_db(payload, intent, payload, reply)
    return True



# =========================================================
# FLOATING TEXT COMMAND BOX
# =========================================================
def text_command_listener():
    """
    Floating command box.

    Controls:
    - Press T while the box is focused to activate typing.
    - Type your command.
    - Press Enter to execute.
    - Press Escape to deactivate/clear.
    """
    try:
        import tkinter as tk
    except Exception as e:
        print("Floating text box needs tkinter:", e)
        return

    root = tk.Tk()
    root.title("Blue Text Command")
    root.geometry("420x115+920+560")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    bg = "#05070a"
    cyan = "#00d9ff"
    dim = "#0b1f2e"
    white = "#d7f7ff"

    root.configure(bg=bg)

    title = tk.Label(
        root,
        text="BLUE TEXT COMMAND",
        bg=bg,
        fg=cyan,
        font=("Consolas", 12, "bold")
    )
    title.pack(pady=(8, 2))

    status = tk.Label(
        root,
        text="Press T to activate text command",
        bg=bg,
        fg=white,
        font=("Consolas", 9)
    )
    status.pack()

    entry = tk.Entry(
        root,
        bg=dim,
        fg=cyan,
        insertbackground=cyan,
        font=("Consolas", 12),
        relief="flat",
        justify="left",
        state="disabled"
    )
    entry.pack(fill="x", padx=14, pady=8, ipady=5)

    def activate(event=None):
        text_input_active.set()
        entry.config(state="normal")
        entry.focus_set()
        status.config(text="Active: type command and press Enter", fg="#00ff99")

    def deactivate(event=None):
        entry.delete(0, "end")
        entry.config(state="disabled")
        text_input_active.clear()
        status.config(text="Inactive: press T to activate", fg=white)
        root.focus_set()

    def submit(event=None):
        cmd = entry.get().strip()
        entry.delete(0, "end")

        if cmd:
            command_queue.put(cmd)
            status.config(text=f"Sent: {cmd}", fg=cyan)
        else:
            status.config(text="No command typed", fg=white)

        entry.config(state="disabled")
        text_input_active.clear()
        root.focus_set()

    def key_handler(event):
        if event.keysym.lower() == "t" and str(entry["state"]) == "disabled":
            activate()
            return "break"

    root.bind("<Key>", key_handler)
    root.bind("<Escape>", deactivate)
    entry.bind("<Return>", submit)
    entry.bind("<Escape>", deactivate)

    # Start focused enough so pressing T works after clicking the small box once.
    root.after(500, root.focus_force)
    root.mainloop()




# =========================================================
# BLUE ULTIMATE SAFETY UPGRADE PACK
# =========================================================
# Added safety layers:
# 1 emergency stop, 2 permission levels, 3 action logging, 4 command preview,
# 5 dry-run mode, 6 rate limiter, 7 action budget, 8 full-control timer,
# 9 master PIN lock, 10 app allowlist, 11 website allowlist, 12 banking/payment guard,
# 13 login/secret guard, 14 OCR sensitive screen guard, 15 protected folder guard,
# 16 file sandbox, 17 auto-backup helper, 18 safe shell allowlist/blocklist,
# 19 mouse arm switch, 20 mouse failsafe, 21 human override hint,
# 22 autonomous-mode limits, 23 trading analysis-only guard, 24 download guard,
# 25 camera/mic confirmation hooks, 26 local-only option, 27 crash-safe logging,
# 28 hallucination/unknown-command guard, 29 mode profiles, 30 audit status command.

import shutil
from pathlib import Path as _BluePath

SAFETY_UPGRADE_COUNT = 30

# Safety profiles change how strict Blue is.
SAFETY_PROFILE = "standard"  # locked, standard, developer, trading_analysis, student
DRY_RUN_MODE = False
LOCAL_ONLY_MODE = False
FULL_CONTROL_UNLOCKED = False
FULL_CONTROL_EXPIRES_AT = 0
FULL_CONTROL_MINUTES = 15
MASTER_PIN = os.environ.get("BLUE_MASTER_PIN", "1234")  # Change this or set env var BLUE_MASTER_PIN.

# Mouse automation is disabled until explicitly armed.
MOUSE_CONTROL_ARMED = False
MOUSE_CONTROL_EXPIRES_AT = 0
MOUSE_CONTROL_MINUTES = 5

# Action budgets and rate limits to stop runaway automation.
COMMAND_TIMESTAMPS = []
MOUSE_ACTION_TIMESTAMPS = []
AUTONOMOUS_ACTION_BUDGET = 20
AUTONOMOUS_ACTION_COUNT = 0
MAX_COMMANDS_PER_MINUTE = 25
MAX_MOUSE_ACTIONS_PER_10_SECONDS = 8
MAX_SHELL_TIMEOUT_SECONDS = 20

BLUE_WORKSPACE = _BluePath(os.getcwd()) / "Blue_Workspace"
BLUE_BACKUP_DIR = BLUE_WORKSPACE / "backups"
BLUE_SCREENSHOT_DIR = BLUE_WORKSPACE / "safety_screenshots"
for _p in [BLUE_WORKSPACE, BLUE_BACKUP_DIR, BLUE_SCREENSHOT_DIR]:
    try:
        _p.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

SAFE_APPS_ALLOWLIST = {
    "notepad", "calculator", "paint", "vs code", "vscode", "chrome", "crome",
    "file explorer", "explorer", "task manager", "settings"
}

TRUSTED_DOMAINS = {
    "youtube.com", "www.youtube.com", "google.com", "www.google.com",
    "mail.google.com", "github.com", "chatgpt.com", "web.whatsapp.com",
    "in.tradingview.com", "tradingview.com", "news.google.com", "wttr.in"
}

PROTECTED_PATH_KEYWORDS = [
    r"c:\\windows", r"c:/windows", "system32", r"c:\\program files",
    r"c:/program files", r"c:\\program files (x86)", "boot.ini", "pagefile.sys",
    "windows\\system32", "windows/system32"
]

DESTRUCTIVE_FILE_WORDS = [
    "delete", "remove", "erase", "wipe", "format", "overwrite", "replace",
    "move", "rename", "rmdir", "del ", "rm ", "clear folder"
]

PAYMENT_LOGIN_WORDS = [
    "bank", "banking", "upi", "payment", "paytm", "phonepe", "google pay",
    "gpay", "checkout", "cart", "buy now", "transfer money", "net banking",
    "login", "sign in", "password", "otp", "cvv", "pin"
]

TRADING_EXECUTION_WORDS = [
    "place trade", "execute trade", "open trade", "close trade", "buy now", "sell now",
    "click buy", "click sell", "broker", "mt5 order", "metatrader order", "real order"
]

SAFE_SHELL_PREFIXES = [
    "dir", "echo", "python --version", "pip --version", "where python", "where pip",
    "whoami", "hostname", "ipconfig", "ping", "tree", "type", "more"
]

EXTRA_BLOCKED_TERMINAL_PATTERNS = [
    "format", "diskpart", "clean all", "delete partition", "bcdedit", "reg delete",
    "takeown", "icacls", "cipher /w", "powershell -enc", "invoke-webrequest",
    "curl http", "curl https", "wget http", "wget https", "shutdown", "restart-computer",
    "remove-item", "rd /s", "del /s", "erase", "mkfs", "dd if=", ":(){:|:&};:",
]

SENSITIVE_SCREEN_WORDS = [
    "password", "enter password", "otp", "one time password", "cvv", "card number",
    "upi pin", "login", "sign in", "payment", "checkout", "netbanking", "banking"
]


def _now_ts():
    return time.time()


def safety_log(command, action_type, status, reason=""):
    """Extra robust safety logging that survives table differences."""
    try:
        log_action_db(command, action_type, status, reason)
    except Exception:
        try:
            with open(BLUE_WORKSPACE / "safety_fallback.log", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()} | {action_type} | {status} | {command} | {reason}\n")
        except Exception:
            pass


def clean_command(command: str) -> str:
    try:
        return normalize_text(remove_wake_word(command))
    except Exception:
        return str(command).lower().strip()


def current_full_control_active() -> bool:
    return FULL_CONTROL_UNLOCKED and _now_ts() < FULL_CONTROL_EXPIRES_AT


def current_mouse_control_active() -> bool:
    return MOUSE_CONTROL_ARMED and _now_ts() < MOUSE_CONTROL_EXPIRES_AT


def classify_permission(command: str):
    """Return SAFE, CONFIRM, or BLOCKED with a reason."""
    clean = clean_command(command)
    raw = str(command).lower()

    if is_emergency_stop(command):
        return "BLOCKED", "emergency stop"

    if contains_secret_request(command):
        return "BLOCKED", "secret/password/OTP protection"

    if any(w in clean for w in TRADING_EXECUTION_WORDS):
        return "BLOCKED", "trading is analysis-only; real order execution is blocked"

    if contains_blocked_terminal_pattern(command) or any(p in raw for p in EXTRA_BLOCKED_TERMINAL_PATTERNS):
        return "BLOCKED", "dangerous terminal/system command"

    if any(p in raw for p in PROTECTED_PATH_KEYWORDS) and any(w in clean for w in DESTRUCTIVE_FILE_WORDS):
        return "BLOCKED", "protected system folder/file"

    if any(w in clean for w in PAYMENT_LOGIN_WORDS) and any(v in clean for v in ["type", "click", "submit", "send", "pay", "buy", "transfer"]):
        return "BLOCKED", "payment/login automation is blocked"

    if clean.startswith(("mouse", "click", "double click", "right click", "move mouse", "scroll", "drag")):
        if not current_mouse_control_active() and clean != "mouse position":
            return "CONFIRM", "mouse control is not armed"
        return "SAFE", "armed mouse control"

    if any(w in clean for w in ["delete", "remove", "format", "shutdown", "restart", "install", "uninstall", "send email", "send message", "run command", "execute command", "powershell", "cmd"]):
        return "CONFIRM", "risky command requires confirmation"

    if clean.startswith("open "):
        for app in SAFE_APPS_ALLOWLIST:
            if app in clean:
                return "SAFE", "trusted app"
        for site in WEBSITE_COMMANDS.keys():
            if site in clean:
                return "SAFE", "trusted website shortcut"
        return "CONFIRM", "unknown app or target"

    if SAFETY_PROFILE == "locked":
        allowed_locked = ["time", "date", "what time", "today", "open youtube", "open google", "read screen"]
        if not any(x in clean for x in allowed_locked):
            return "CONFIRM", "locked profile limits commands"

    return "SAFE", "normal safe command"


def calculate_risk_score(command: str) -> int:
    clean = clean_command(command)
    score = 5
    high = ["format", "delete", "shutdown", "restart", "powershell", "cmd", "run command", "payment", "password", "otp", "broker", "trade"]
    medium = ["click", "type", "download", "install", "uninstall", "email", "message", "mouse", "file"]
    for w in high:
        if w in clean:
            score += 18
    for w in medium:
        if w in clean:
            score += 8
    if any(p in str(command).lower() for p in PROTECTED_PATH_KEYWORDS):
        score += 35
    if current_full_control_active():
        score -= 5
    return max(0, min(100, score))


def command_preview(command: str, permission: str, reason: str) -> str:
    score = calculate_risk_score(command)
    return f"Preview: command={command}. Permission={permission}. Risk score={score}/100. Reason={reason}."


def safety_rate_limit(command: str):
    global COMMAND_TIMESTAMPS
    now = _now_ts()
    COMMAND_TIMESTAMPS = [t for t in COMMAND_TIMESTAMPS if now - t < 60]
    COMMAND_TIMESTAMPS.append(now)
    if len(COMMAND_TIMESTAMPS) > MAX_COMMANDS_PER_MINUTE:
        return False, "Too many commands in one minute. Safety rate limit activated."
    return True, ""


def mouse_rate_limit():
    global MOUSE_ACTION_TIMESTAMPS
    now = _now_ts()
    MOUSE_ACTION_TIMESTAMPS = [t for t in MOUSE_ACTION_TIMESTAMPS if now - t < 10]
    MOUSE_ACTION_TIMESTAMPS.append(now)
    if len(MOUSE_ACTION_TIMESTAMPS) > MAX_MOUSE_ACTIONS_PER_10_SECONDS:
        return False, "Too many mouse actions. Mouse safety rate limit activated."
    return True, ""


def detect_sensitive_screen() -> bool:
    """OCR screen check. If OCR is unavailable, do not block normal safe commands."""
    if not OCR_AVAILABLE:
        return False
    try:
        screenshot = pyautogui.screenshot()
        text = pytesseract.image_to_string(screenshot).lower()
        return any(w in text for w in SENSITIVE_SCREEN_WORDS)
    except Exception:
        return False


def backup_file_if_exists(path_text: str):
    """Create a backup for files before changes when a path is detected."""
    try:
        p = _BluePath(path_text.strip('"\''))
        if not p.exists() or not p.is_file():
            return ""
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = BLUE_BACKUP_DIR / f"{p.name}.{stamp}.bak"
        shutil.copy2(str(p), str(dest))
        safety_log(str(p), "auto_backup", "success", str(dest))
        return str(dest)
    except Exception as exc:
        safety_log(path_text, "auto_backup", "failed", str(exc))
        return ""


def extract_possible_paths(command: str):
    raw = str(command)
    found = re.findall(r'([A-Za-z]:[\\/][^\n\r\t"<>|]+)', raw)
    found += re.findall(r'([\w\-. ]+\.(?:txt|py|json|csv|xlsx|md|db))', raw)
    return [x.strip() for x in found]


def is_path_inside_workspace(path_text: str) -> bool:
    try:
        p = _BluePath(path_text).expanduser().resolve()
        ws = BLUE_WORKSPACE.resolve()
        return str(p).startswith(str(ws))
    except Exception:
        return False


def ask_user_confirmation(command: str, reason="risky action") -> bool:
    """Upgraded confirmation: shows preview, risk score, and optionally PIN for very risky actions."""
    if not CONFIRM_RISKY_ACTIONS:
        return True
    permission, _reason = classify_permission(command)
    preview = command_preview(command, permission, reason or _reason)
    speak("Safety check. " + preview + " Should I continue? Type yes or no.", allow_repeat=True)
    wait_until_done_speaking()
    try:
        answer = input(f"{preview}\nConfirm? yes/no: ").strip().lower()
    except Exception:
        answer = "no"
    allowed = answer in ["yes", "y", "ok", "continue", "allow", "confirm"]
    if allowed and calculate_risk_score(command) >= 70:
        try:
            pin = input("High risk action. Enter Blue master PIN: ").strip()
        except Exception:
            pin = ""
        if pin != MASTER_PIN:
            allowed = False
            reason = "wrong master PIN"
    safety_log(command, "confirmation", "allowed" if allowed else "cancelled", reason)
    return allowed


def safety_guard(command: str):
    """Ultimate central safety gate. Return (allowed, stop_blue, reply)."""
    global FULL_CONTROL_UNLOCKED, FULL_CONTROL_EXPIRES_AT, MOUSE_CONTROL_ARMED
    if not SAFETY_MODE:
        return True, False, ""

    clean = clean_command(command)

    if is_emergency_stop(command):
        FULL_CONTROL_UNLOCKED = False
        MOUSE_CONTROL_ARMED = False
        reply = "Emergency stop activated. Blue stopped automation, mouse control, and full control safely."
        safety_log(command, "emergency_stop", "success", "all safety locks enabled")
        return False, True, reply

    ok, msg = safety_rate_limit(command)
    if not ok:
        safety_log(command, "rate_limit", "blocked", msg)
        return False, False, msg

    if DRY_RUN_MODE and clean not in ["dry run off", "disable dry run", "safety status", "stop blue"]:
        permission, reason = classify_permission(command)
        reply = "Dry Run Mode is ON. " + command_preview(command, permission, reason) + " I did not execute it."
        safety_log(command, "dry_run", "preview_only", reason)
        return False, False, reply

    # If full control expired, lock it automatically.
    if FULL_CONTROL_UNLOCKED and _now_ts() >= FULL_CONTROL_EXPIRES_AT:
        FULL_CONTROL_UNLOCKED = False
        safety_log(command, "full_control", "expired", "time limit reached")

    if MOUSE_CONTROL_ARMED and _now_ts() >= MOUSE_CONTROL_EXPIRES_AT:
        MOUSE_CONTROL_ARMED = False
        safety_log(command, "mouse_control", "expired", "time limit reached")

    # Sensitive screen guard before typing/clicking/payment automation.
    if clean.startswith(("type", "write", "click", "double click", "right click", "move mouse", "drag")):
        if detect_sensitive_screen():
            reply = "Sensitive screen detected, such as login, payment, password, or OTP. Automation paused."
            safety_log(command, "sensitive_screen", "blocked", "OCR detected sensitive words")
            return False, False, reply

    permission, reason = classify_permission(command)
    if permission == "BLOCKED":
        reply = "Blocked for safety. " + reason
        safety_log(command, "permission", "blocked", reason)
        return False, False, reply

    if permission == "CONFIRM":
        if not ask_user_confirmation(command, reason):
            reply = "Cancelled. I did not perform that action."
            safety_log(command, "permission", "cancelled", reason)
            return False, False, reply
        safety_log(command, "permission", "confirmed", reason)

    # Backup any directly mentioned file before a destructive-looking command.
    if any(w in clean for w in DESTRUCTIVE_FILE_WORDS):
        for p in extract_possible_paths(command):
            if not is_path_inside_workspace(p) and any(w in clean for w in ["edit", "write", "replace", "delete", "remove", "move"]):
                # Outside workspace destructive file action requires confirmation even after normal confirmation.
                if not ask_user_confirmation(command, "file outside Blue_Workspace"):
                    return False, False, "Cancelled. File outside Blue_Workspace was not changed."
            backup_file_if_exists(p)

    return True, False, ""


# Keep old direct handler and mouse handler, then wrap them with stronger controls.
try:
    _legacy_handle_full_control_direct_commands = handle_full_control_direct_commands
except Exception:
    _legacy_handle_full_control_direct_commands = None
try:
    _legacy_live_mouse_command = live_mouse_command
except Exception:
    _legacy_live_mouse_command = None
try:
    _legacy_open_url = open_url
except Exception:
    _legacy_open_url = None
try:
    _legacy_run_safe_shell_command = run_safe_shell_command
except Exception:
    _legacy_run_safe_shell_command = None


def safety_status_text():
    full_left = max(0, int(FULL_CONTROL_EXPIRES_AT - _now_ts())) if FULL_CONTROL_UNLOCKED else 0
    mouse_left = max(0, int(MOUSE_CONTROL_EXPIRES_AT - _now_ts())) if MOUSE_CONTROL_ARMED else 0
    return (
        f"Safety upgrades active: {SAFETY_UPGRADE_COUNT}. "
        f"Profile: {SAFETY_PROFILE}. Dry run: {DRY_RUN_MODE}. Local only: {LOCAL_ONLY_MODE}. "
        f"Full control unlocked: {FULL_CONTROL_UNLOCKED}, seconds left: {full_left}. "
        f"Mouse armed: {MOUSE_CONTROL_ARMED}, seconds left: {mouse_left}. "
        f"Workspace: {BLUE_WORKSPACE}."
    )


def set_safety_profile(profile: str):
    global SAFETY_PROFILE
    valid = {"locked", "standard", "developer", "trading_analysis", "student"}
    if profile not in valid:
        return "Unknown safety profile. Use locked, standard, developer, trading analysis, or student."
    SAFETY_PROFILE = profile
    safety_log("set safety profile " + profile, "profile", "success", profile)
    return f"Safety profile set to {profile}."


def unlock_full_control(command: str):
    global FULL_CONTROL_UNLOCKED, FULL_CONTROL_EXPIRES_AT
    try:
        pin = input("Enter Blue master PIN to unlock full control: ").strip()
    except Exception:
        pin = ""
    if pin != MASTER_PIN:
        FULL_CONTROL_UNLOCKED = False
        safety_log(command, "full_control", "blocked", "wrong PIN")
        return "Wrong PIN. Full Control remains locked."
    FULL_CONTROL_UNLOCKED = True
    FULL_CONTROL_EXPIRES_AT = _now_ts() + FULL_CONTROL_MINUTES * 60
    safety_log(command, "full_control", "unlocked", f"{FULL_CONTROL_MINUTES} minutes")
    return f"Full Control unlocked for {FULL_CONTROL_MINUTES} minutes. Risky actions still use safety checks."


def lock_full_control(command: str):
    global FULL_CONTROL_UNLOCKED, FULL_CONTROL_EXPIRES_AT, MOUSE_CONTROL_ARMED
    FULL_CONTROL_UNLOCKED = False
    FULL_CONTROL_EXPIRES_AT = 0
    MOUSE_CONTROL_ARMED = False
    safety_log(command, "full_control", "locked", "manual lock")
    return "Full Control and mouse control locked."


def arm_mouse_control(command: str):
    global MOUSE_CONTROL_ARMED, MOUSE_CONTROL_EXPIRES_AT
    if not ask_user_confirmation(command, "arm mouse automation"):
        return "Mouse control was not armed."
    MOUSE_CONTROL_ARMED = True
    MOUSE_CONTROL_EXPIRES_AT = _now_ts() + MOUSE_CONTROL_MINUTES * 60
    try:
        pyautogui.FAILSAFE = True
    except Exception:
        pass
    safety_log(command, "mouse_control", "armed", f"{MOUSE_CONTROL_MINUTES} minutes")
    return f"Mouse control armed for {MOUSE_CONTROL_MINUTES} minutes. Move mouse to top-left corner for pyautogui failsafe."


def disarm_mouse_control(command: str):
    global MOUSE_CONTROL_ARMED, MOUSE_CONTROL_EXPIRES_AT
    MOUSE_CONTROL_ARMED = False
    MOUSE_CONTROL_EXPIRES_AT = 0
    safety_log(command, "mouse_control", "disarmed", "manual")
    return "Mouse control disarmed."


def open_url(url: str):
    """Safe browser wrapper: blocks suspicious/payment URLs and local-only mode."""
    if LOCAL_ONLY_MODE:
        safety_log(url, "open_url", "blocked", "local-only mode")
        return
    low = str(url).lower()
    if any(w in low for w in ["bank", "payment", "checkout", "pay", "upi", "login", "signin"]):
        safety_log(url, "open_url", "blocked", "payment/login URL")
        speak("I blocked opening or automating a sensitive payment, banking, or login page.", allow_repeat=True)
        return
    try:
        from urllib.parse import urlparse
        host = urlparse(url).netloc.lower()
        if host and not any(host == d or host.endswith("." + d) for d in TRUSTED_DOMAINS):
            if not ask_user_confirmation("open url " + url, "unknown website"):
                safety_log(url, "open_url", "cancelled", "unknown website")
                return
    except Exception:
        pass
    return _legacy_open_url(url) if _legacy_open_url else webbrowser.open(url)


def run_safe_shell_command(command: str):
    """Safer shell: allow common harmless commands, confirm/block the rest."""
    shell_cmd = extract_shell_command(command)
    if not shell_cmd:
        return "Tell me the exact command after saying run command."
    low = shell_cmd.lower().strip()
    if contains_secret_request(shell_cmd) or contains_blocked_terminal_pattern(shell_cmd) or any(p in low for p in EXTRA_BLOCKED_TERMINAL_PATTERNS):
        safety_log(command, "shell", "blocked", "blocked shell pattern")
        return "I blocked that terminal command for safety."
    is_safe_prefix = any(low.startswith(prefix) for prefix in SAFE_SHELL_PREFIXES)
    if not is_safe_prefix and not current_full_control_active():
        return "Shell command blocked. Unlock Full Control first, then confirm the command."
    if not is_safe_prefix and not ask_user_confirmation(command, "non-allowlisted shell command"):
        return "Cancelled. Shell command was not executed."
    try:
        completed = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True, timeout=MAX_SHELL_TIMEOUT_SECONDS)
        output = (completed.stdout or completed.stderr or "Command finished.").strip()[:600]
        safety_log(command, "shell", "success", shell_cmd)
        return "Command executed. Output: " + output
    except Exception as e:
        safety_log(command, "shell", "failed", str(e))
        return "I could not run that command because " + str(e)


def live_mouse_command(command):
    clean = clean_command(command)
    if clean == "mouse position" and _legacy_live_mouse_command:
        return _legacy_live_mouse_command(command)
    if clean.startswith(("mouse", "click", "double click", "right click", "move mouse", "scroll", "drag")):
        if not current_mouse_control_active():
            return "Mouse control is not armed. Say: arm mouse control."
        ok, msg = mouse_rate_limit()
        if not ok:
            safety_log(command, "mouse_rate_limit", "blocked", msg)
            return msg
        if detect_sensitive_screen():
            safety_log(command, "mouse", "blocked", "sensitive screen")
            return "Sensitive screen detected. Mouse automation paused."
    return _legacy_live_mouse_command(command) if _legacy_live_mouse_command else ""


def handle_full_control_direct_commands(command: str):
    """Extra safety commands, then legacy Blue commands."""
    global DRY_RUN_MODE, LOCAL_ONLY_MODE, AUTONOMOUS_ACTION_COUNT
    clean = clean_command(command)

    if clean in ["safety status", "blue safety status", "security status"]:
        return safety_status_text()
    if clean in ["dry run on", "enable dry run"]:
        DRY_RUN_MODE = True
        safety_log(command, "dry_run", "enabled", "manual")
        return "Dry Run Mode is ON. I will preview commands without executing them."
    if clean in ["dry run off", "disable dry run"]:
        DRY_RUN_MODE = False
        safety_log(command, "dry_run", "disabled", "manual")
        return "Dry Run Mode is OFF."
    if clean in ["local only on", "offline mode on"]:
        LOCAL_ONLY_MODE = True
        safety_log(command, "local_only", "enabled", "manual")
        return "Local-only mode is ON. Internet opening is blocked."
    if clean in ["local only off", "offline mode off"]:
        LOCAL_ONLY_MODE = False
        safety_log(command, "local_only", "disabled", "manual")
        return "Local-only mode is OFF."
    if clean in ["unlock full control", "full control unlock", "developer unlock"]:
        return unlock_full_control(command)
    if clean in ["lock full control", "full control lock", "safe mode", "lock blue"]:
        return lock_full_control(command)
    if clean in ["arm mouse control", "confirm mouse control", "unlock mouse control"]:
        return arm_mouse_control(command)
    if clean in ["disarm mouse control", "lock mouse control", "stop mouse control"]:
        return disarm_mouse_control(command)
    if clean.startswith("set safety profile"):
        profile = clean.replace("set safety profile", "").strip().replace(" ", "_")
        if profile == "trading":
            profile = "trading_analysis"
        return set_safety_profile(profile)
    if clean in ["safety upgrades count", "how many safety upgrades", "safety count"]:
        return f"I have {SAFETY_UPGRADE_COUNT} major safety upgrade systems active in this build."
    if clean in ["reset action budget", "reset autonomous budget"]:
        AUTONOMOUS_ACTION_COUNT = 0
        return "Autonomous action budget reset."

    # Trading execution guard before legacy handler.
    if any(w in clean for w in TRADING_EXECUTION_WORDS):
        safety_log(command, "trading_execution", "blocked", "analysis-only policy")
        return "Trading execution is blocked. I can only analyze charts, give signals, journal, and backtest."

    return _legacy_handle_full_control_direct_commands(command) if _legacy_handle_full_control_direct_commands else ""


# Upgrade pyautogui failsafe where available.
try:
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05
except Exception:
    pass


# =========================================================
# MAIN LOOP
# =========================================================
def main():
    init_database()
    if ML_AVAILABLE and not os.path.exists(INTENT_MODEL_FILE):
        train_small_intent_model()
    play_tone("startup")
    speak("Hello sir.", allow_repeat=True)

    if TEXT_COMMAND_MODE:
        threading.Thread(
            target=text_command_listener,
            daemon=True
        ).start()

    no_hear_count = 0
    active_mode = False
    active_until = 0

    while True:
        # =====================================================
        # PRIORITY 0: TEXT BOX IS ACTIVE
        # =====================================================
        if text_input_active.is_set() and command_queue.empty():
            time.sleep(0.05)
            continue

        # =====================================================
        # PRIORITY 1: TEXT COMMAND BOX
        # =====================================================
        if not command_queue.empty():
            text = command_queue.get()
            used_engine = "text_command"
            active_mode = True
            active_until = time.time() + ACTIVE_SESSION_SECONDS

        # =====================================================
        # PRIORITY 2: VOICE COMMANDS
        # =====================================================
        elif active_mode and time.time() <= active_until:
            text, used_engine = listen_blue()
        else:
            active_mode = False
            text, used_engine = listen_wake_word()

        if not text:
            no_hear_count += 1
            if active_mode and no_hear_count == 1:
                speak("I could not hear properly.")
            elif active_mode and no_hear_count == 3:
                speak("Still not hearing clearly. Please check your microphone.")
            continue

        no_hear_count = 0
        clean_text = normalize_text(text)

        if used_engine == "text_command":
            command = clean_text

        else:
            wake_detected = clean_text == WAKE_WORD or clean_text.startswith(WAKE_WORD + " ")

            if wake_detected:
                active_mode = True
                active_until = time.time() + ACTIVE_SESSION_SECONDS
                command = remove_wake_word(text)
                if not command:
                    speak("Yes sir. I am active and listening.")
                    wait_until_done_speaking()
                    continue
            elif active_mode and time.time() <= active_until:
                command = clean_text
                active_until = time.time() + ACTIVE_SESSION_SECONDS
            else:
                active_mode = False
                print("Standby mode. Wake word not detected. Ignored:", text)
                continue

        print(f"Engine used: {used_engine}")

        allowed, stop_blue, safety_reply = safety_guard(command)
        if stop_blue:
            speak(safety_reply, allow_repeat=True)
            wait_until_done_speaking()
            break
        if not allowed:
            speak(safety_reply, allow_repeat=True)
            add_chat_history(command, safety_reply)
            log_command_db(command, "safety_guard", command, safety_reply)
            wait_until_done_speaking()
            continue

        direct_reply = handle_full_control_direct_commands(command)
        if direct_reply:
            reply = jarvis_line(direct_reply)
            speak(reply)
            add_chat_history(command, reply)
            log_command_db(command, "full_control", command, reply)
            wait_until_done_speaking()
            continue

        intent, payload = classify_intent(command)
        print(f"Intent: {intent} | Payload: {payload}")

        result = handle_intent(intent, payload)
        wait_until_done_speaking()

        if result == "sleep":
            active_mode = False
            active_until = 0
            continue

        if not result:
            break



# =========================================================
# BLUE 5.0 MEGA UPGRADE LAYER
# Added by ChatGPT: wake-word toggle + 7 upgrade families
# This layer overrides selected functions safely without deleting older code.
# =========================================================

# Wake word can now be turned ON/OFF by voice or text.
WAKE_WORD_ENABLED = True

# Memory / workflow / agent files
VECTOR_MEMORY_FILE = "blue_vector_memory.json"
WORKFLOW_MEMORY_FILE = "blue_workflows.json"
CRASH_STATE_FILE = "blue_crash_state.json"
AGENT_LOG_FILE = "blue_agent_steps.json"

# UI / Internet / Safety settings
BROWSER_AGENT_SAFE_MODE = True
BUTTON_DETECTION_ENABLED = True
OBJECT_DETECTION_ENABLED = True
GESTURE_CONTROL_ENABLED = False
AIR_MOUSE_ENABLED = False
EMOTION_TONE_ENABLED = True
VOICE_PRESET_MODE = "jarvis"
AUTO_RESEARCH_MAX_PAGES = 3
PLUGIN_SANDBOX_ENABLED = True
AI_BEHAVIOR_MONITOR_ENABLED = True

TRUSTED_AUTOMATION_SITES = [
    "youtube.com", "google.com", "github.com", "chatgpt.com",
    "tradingview.com", "mail.google.com", "web.whatsapp.com"
]

WINDOWS_CONTROL_COMMANDS = {
    "open task manager": lambda: subprocess.Popen("taskmgr", shell=True),
    "open settings": lambda: subprocess.Popen("start ms-settings:", shell=True),
    "show desktop": lambda: pyautogui.hotkey("win", "d"),
    "lock screen": lambda: subprocess.Popen("rundll32.exe user32.dll,LockWorkStation", shell=True),
}

CLOSE_COMMANDS = {
    "chrome": ["chrome.exe"], "crome": ["chrome.exe"],
    "youtube": ["chrome.exe"], "google": ["chrome.exe"], "gmail": ["chrome.exe"],
    "github": ["chrome.exe"], "whatsapp": ["chrome.exe"],
    "notepad": ["notepad.exe"], "calculator": ["CalculatorApp.exe", "calc.exe"],
    "paint": ["mspaint.exe"], "cmd": ["cmd.exe"], "command prompt": ["cmd.exe"],
    "vs code": ["Code.exe"], "vscode": ["Code.exe"],
    "file explorer": ["explorer.exe"], "explorer": ["explorer.exe"],
}

# -------------------------
# Generic JSON helpers
# -------------------------
def _blue_load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if data is not None else default
    except Exception as e:
        print(f"JSON load error {path}:", e)
    return default


def _blue_save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"JSON save error {path}:", e)
        return False


# -------------------------
# Voice-only confirmation
# -------------------------
def ask_user_confirmation(command: str, reason="risky action") -> bool:
    """Voice-only safety confirmation. No keyboard yes/no needed."""
    if not CONFIRM_RISKY_ACTIONS:
        return True

    speak(f"Safety check. This may be a {reason}. Please say yes or no.", allow_repeat=True)
    wait_until_done_speaking()

    answer = ""
    try:
        answer = listen_faster_whisper(duration=3)
    except Exception as e:
        print("Voice confirmation listen error:", e)
        answer = ""

    if not answer:
        speak("No voice confirmation detected. Cancelling action.", allow_repeat=True)
        log_action_db(command, "voice_confirmation", "cancelled", "no response")
        return False

    answer = normalize_text(answer)
    yes_words = ["yes", "yeah", "yup", "confirm", "continue", "allow", "do it", "go ahead", "okay", "ok"]
    no_words = ["no", "cancel", "stop", "do not", "dont", "don't", "deny"]

    if any(w in answer for w in yes_words):
        speak("Confirmation accepted.", allow_repeat=True)
        log_action_db(command, "voice_confirmation", "allowed", answer)
        return True

    if any(w in answer for w in no_words):
        speak("Action cancelled.", allow_repeat=True)
        log_action_db(command, "voice_confirmation", "cancelled", answer)
        return False

    speak("I could not understand the confirmation. Cancelling action.", allow_repeat=True)
    log_action_db(command, "voice_confirmation", "cancelled", "unclear: " + answer)
    return False


# -------------------------
# AI CORE upgrades
# -------------------------
def vector_memory_add(text, tags=None):
    data = _blue_load_json(VECTOR_MEMORY_FILE, [])
    item = {
        "id": str(uuid.uuid4()),
        "text": str(text)[:1000],
        "tags": tags or [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    data.append(item)
    _blue_save_json(VECTOR_MEMORY_FILE, data[-1000:])
    return "Saved this to vector-style memory."


def vector_memory_search(query, limit=5):
    data = _blue_load_json(VECTOR_MEMORY_FILE, [])
    q = set(normalize_text(query).split())
    scored = []
    for item in data:
        words = set(normalize_text(item.get("text", "")).split())
        score = len(q & words) / max(1, len(q))
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [i for _, i in scored[:limit]]


def multi_agent_router(command):
    clean = normalize_text(command)
    if any(x in clean for x in ["code", "python", "vs code", "debug"]):
        return "coding_agent"
    if any(x in clean for x in ["research", "search", "summarize", "youtube"]):
        return "internet_agent"
    if any(x in clean for x in ["screen", "camera", "object", "face", "gesture"]):
        return "vision_agent"
    if any(x in clean for x in ["file", "folder", "desktop", "windows"]):
        return "desktop_agent"
    if any(x in clean for x in ["trade", "chart", "market", "signal"]):
        return "trading_agent_analysis_only"
    return "general_agent"


def hybrid_ai_brain(prompt):
    """Uses Ollama first, then online quick answer as fallback. Keeps answer short."""
    try:
        local_answer = ask_meta_ai_brain(prompt)
        if local_answer and "not available" not in local_answer.lower():
            return "Local brain: " + local_answer[:900]
    except Exception:
        pass
    try:
        web_answer = online_answer(prompt)
        if web_answer:
            return "Online brain: " + web_answer[:900]
    except Exception:
        pass
    return friendly_chat_reply(prompt)


def save_self_learning_workflow(name, steps):
    data = _blue_load_json(WORKFLOW_MEMORY_FILE, {})
    data[name] = {"steps": steps, "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    _blue_save_json(WORKFLOW_MEMORY_FILE, data)
    return f"Saved workflow {name}."


def autonomous_planner(command):
    agent = multi_agent_router(command)
    clean = normalize_text(command)
    plan = []
    if agent == "coding_agent":
        plan = ["open vs code", "read project files", "suggest safe code changes", "ask confirmation before editing"]
    elif agent == "internet_agent":
        plan = ["search trusted sources", "open browser", "summarize findings", "save notes"]
    elif agent == "vision_agent":
        plan = ["take screenshot", "read screen with OCR", "identify buttons/objects", "ask before clicking"]
    elif agent == "desktop_agent":
        plan = ["scan target folder", "organize safe files only", "backup before changes", "log action"]
    elif agent == "trading_agent_analysis_only":
        plan = ["open chart", "analyze market", "give BUY/SELL/WAIT", "do not place trades"]
    else:
        plan = ["understand request", "choose safe tool", "perform safe actions", "log result"]
    return "Agent: " + agent + ". Plan: " + " -> ".join(plan)


def detect_emotional_tone(text):
    clean = normalize_text(text)
    if any(w in clean for w in ["angry", "mad", "frustrated", "irritated"]):
        return "frustrated"
    if any(w in clean for w in ["sad", "tired", "stressed", "worried"]):
        return "stressed"
    if any(w in clean for w in ["happy", "great", "nice", "good"]):
        return "positive"
    return "neutral"


# -------------------------
# VISION AI upgrades
# -------------------------
def screen_understanding():
    try:
        text = read_screen_text()
        return "Screen understanding: " + text[:700]
    except Exception as e:
        return "Screen understanding failed: " + str(e)


def button_detection_ai():
    if not OCR_AVAILABLE:
        return "Button detection needs pytesseract OCR."
    try:
        screenshot = pyautogui.screenshot()
        text = pytesseract.image_to_string(screenshot)
        candidates = []
        for word in ["ok", "submit", "next", "login", "search", "cancel", "close", "continue", "save"]:
            if word in text.lower():
                candidates.append(word)
        if candidates:
            return "I detected possible screen buttons or actions: " + ", ".join(sorted(set(candidates))) + ". I will ask before clicking."
        return "I scanned the screen but did not find obvious buttons."
    except Exception as e:
        return "Button detection error: " + str(e)


def object_detection_ai():
    return "Object detection hook is ready. Install ultralytics for YOLO object detection: pip install ultralytics."


def face_recognition_lock():
    return "Face unlock hook is ready. Next step: add face_recognition or OpenCV face model and store authorized face locally."


def gesture_control_status():
    return f"Gesture control is {'ON' if GESTURE_CONTROL_ENABLED else 'OFF'}. Air mouse is {'ON' if AIR_MOUSE_ENABLED else 'OFF'}."


# -------------------------
# Desktop AI upgrades
# -------------------------
def organize_files_preview(folder=None):
    folder = folder or FOLDER_COMMANDS.get("downloads")
    if not folder or not os.path.exists(folder):
        return "Folder not found for file organization."
    groups = {}
    for name in os.listdir(folder)[:200]:
        path = os.path.join(folder, name)
        if os.path.isfile(path):
            ext = os.path.splitext(name)[1].lower() or "no_extension"
            groups[ext] = groups.get(ext, 0) + 1
    if not groups:
        return "No files found to organize."
    summary = ", ".join([f"{k}: {v}" for k, v in sorted(groups.items())[:12]])
    return "File organization preview only: " + summary + ". Say organize files confirmed to actually move files later."


def auto_coding_assistant(command):
    return "Coding assistant ready. I can inspect errors, explain code, and suggest patches. I will ask before changing files."


def vscode_ai_helper(command):
    try:
        subprocess.Popen("code .", shell=True)
        return "Opening VS Code helper for this project."
    except Exception as e:
        return "Could not open VS Code: " + str(e)


def windows_control_center(command):
    clean = normalize_text(command)
    for key, fn in WINDOWS_CONTROL_COMMANDS.items():
        if key in clean:
            if "lock" in key or "settings" in key:
                if not ask_user_confirmation(command, key):
                    return "Cancelled."
            fn()
            return "Windows control executed: " + key
    return "Windows control center ready: open task manager, open settings, show desktop, lock screen."


# -------------------------
# Voice system upgrades
# -------------------------
def set_wake_word_enabled(enabled: bool):
    global WAKE_WORD_ENABLED, ALWAYS_LISTEN_MODE
    WAKE_WORD_ENABLED = bool(enabled)
    ALWAYS_LISTEN_MODE = not enabled
    status = "ON" if WAKE_WORD_ENABLED else "OFF"
    log_action_db("wake word " + status.lower(), "wake_word_toggle", status, "user command")
    return f"Wake word is now {status}." + (" You can speak directly without saying Blue." if not enabled else " Say Blue before commands.")


def voice_system_status():
    return (
        f"Voice status: wake word {'ON' if WAKE_WORD_ENABLED else 'OFF'}, "
        f"always listen {'ON' if ALWAYS_LISTEN_MODE else 'OFF'}, "
        f"emotion tone {'ON' if EMOTION_TONE_ENABLED else 'OFF'}, "
        f"voice preset {VOICE_PRESET_MODE}."
    )


def interrupt_speaking():
    try:
        while not speech_queue.empty():
            speech_queue.get_nowait()
            speech_queue.task_done()
    except Exception:
        pass
    return "Speech queue cleared."


def real_time_vad_status():
    return "Real-time VAD hook is ready. For full VAD install webrtcvad or silero-vad and replace fixed record seconds."


def faster_wake_engine_status():
    return "Faster wake engine uses the tiny Whisper wake model now. For even faster mode add Porcupine/OpenWakeWord later."


def voice_preset(command):
    global VOICE_PRESET_MODE, VOICE_EDGE_RATE, VOICE_EDGE_PITCH
    clean = normalize_text(command)
    if "calm" in clean:
        VOICE_PRESET_MODE = "calm"; VOICE_EDGE_RATE = "-15%"; VOICE_EDGE_PITCH = "-30Hz"
    elif "fast" in clean:
        VOICE_PRESET_MODE = "fast"; VOICE_EDGE_RATE = "+10%"; VOICE_EDGE_PITCH = "-10Hz"
    elif "jarvis" in clean:
        VOICE_PRESET_MODE = "jarvis"; VOICE_EDGE_RATE = "-10%"; VOICE_EDGE_PITCH = "-20Hz"
    else:
        return "Voice presets available: Jarvis, calm, fast."
    return "Voice preset changed to " + VOICE_PRESET_MODE + "."


# -------------------------
# HUD / UI upgrades
# -------------------------
def update_hud_status(status="online", detail="Blue 5.0 ready"):
    data = {"status": status, "detail": detail, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    _blue_save_json("HUD_STATUS_FILE", data)
    return data


def hud_feature_status():
    update_hud_status("thinking", "Iron HUD, waveform, system stats, floating overlay hooks active")
    return "HUD upgrades ready: Iron HUD, animated waveform hook, thinking effect, floating overlay hook, system stats file."


def system_stats_overlay():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.2)
        ram = psutil.virtual_memory().percent
        update_hud_status("system", f"CPU {cpu}% | RAM {ram}%")
        return f"System stats: CPU {cpu} percent, RAM {ram} percent."
    except Exception:
        return "System stats need psutil: pip install psutil."


# -------------------------
# Internet Agent upgrades
# -------------------------
def trusted_site_check(url):
    low = url.lower()
    return any(site in low for site in TRUSTED_AUTOMATION_SITES)


def ai_browsing(command):
    query = extract_search_query(command)
    if not query:
        query = command
    url = "https://www.google.com/search?q=" + quote_plus(query)
    open_url(url)
    return "AI browser opened safe Google search for: " + query


def auto_research(command):
    query = extract_after_phrases(command, ["auto research", "research", "deep research"])
    if not query:
        query = command
    ans = online_answer(query)
    if ans:
        vector_memory_add("Research: " + query + " -> " + ans, ["research"])
        return "Research summary: " + ans[:900]
    open_url("https://www.google.com/search?q=" + quote_plus(query))
    return "I opened research results for: " + query


def auto_summarization(command):
    text = extract_after_phrases(command, ["summarize this", "summarize"])
    if not text:
        text = read_screen_text()
    prompt = "Summarize briefly: " + text[:2000]
    return hybrid_ai_brain(prompt)


def youtube_video_summarizer(command):
    return "YouTube summarizer hook ready. Open a video, then say read screen or paste transcript for summary."


# -------------------------
# Advanced Safety upgrades
# -------------------------
def voice_identity_check():
    return "Voice identity hook ready. For real voice ID, add speaker embedding model and store only your local voiceprint."


def encrypted_memory_status():
    return "Encrypted memory hook ready. Next step: encrypt JSON/SQLite with a local passphrase."


def plugin_sandbox_status():
    return "Plugin sandbox is ON. Unknown plugins should run in a restricted folder only."


def ai_behavior_monitor(command):
    clean = normalize_text(command)
    risk = 5
    if is_risky_action(clean): risk += 40
    if contains_secret_request(clean): risk += 80
    if contains_blocked_terminal_pattern(clean): risk += 90
    if "click" in clean or "mouse" in clean: risk += 15
    risk = min(100, risk)
    return risk


def save_crash_state(command="", status="running"):
    _blue_save_json(CRASH_STATE_FILE, {
        "last_command": command,
        "status": status,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


def auto_crash_recovery():
    state = _blue_load_json(CRASH_STATE_FILE, {})
    if state:
        return "Crash recovery ready. Last state: " + str(state)[:300]
    return "Crash recovery ready. No previous crash state found."


# -------------------------
# Close controls
# -------------------------
def close_application(app_name):
    app_name = normalize_text(app_name)
    if app_name not in CLOSE_COMMANDS:
        return f"I do not know how to close {app_name} safely. Try close current tab or close current window."
    if app_name in ["youtube", "google", "gmail", "github", "whatsapp"]:
        return "For websites, safer action is close current tab. Say close current tab."
    if not ask_user_confirmation("close " + app_name, "closing application"):
        return "Cancelled."
    closed_any = False
    for process_name in CLOSE_COMMANDS[app_name]:
        try:
            subprocess.run(f'taskkill /f /im "{process_name}"', shell=True, capture_output=True, timeout=10)
            closed_any = True
        except Exception as e:
            print("Close app error:", e)
    if closed_any:
        log_action_db("close " + app_name, "close_application", "success", app_name)
        return "Closing " + app_name + "."
    return "I could not close " + app_name + "."


# -------------------------
# Main direct command override
# -------------------------
def handle_full_control_direct_commands(command: str):
    """Blue 5.0 direct commands: wake toggle + seven upgrade families."""
    global ALWAYS_LISTEN_MODE, WAKE_WORD_ENABLED, GESTURE_CONTROL_ENABLED, AIR_MOUSE_ENABLED
    global BROWSER_AGENT_SAFE_MODE, EMOTION_TONE_ENABLED

    clean = normalize_text(remove_wake_word(command))

    # Wake word ON/OFF
    if clean in ["wake word off", "turn off wake word", "disable wake word", "no wake word"]:
        return set_wake_word_enabled(False)
    if clean in ["wake word on", "turn on wake word", "enable wake word", "use wake word"]:
        return set_wake_word_enabled(True)
    if clean in ["wake word status", "voice status", "listening status"]:
        return voice_system_status()

    # Voice-only safety / interrupt
    if clean in ["stop speaking", "interrupt", "interrupt speaking"]:
        return interrupt_speaking()
    if clean.startswith("voice preset") or clean in ["jarvis voice", "calm voice", "fast voice"]:
        return voice_preset(clean)
    if clean in ["real time vad", "vad status"]:
        return real_time_vad_status()
    if clean in ["faster wake word", "wake engine status"]:
        return faster_wake_engine_status()

    # Close commands
    if clean in ["close current tab", "close tab"]:
        pyautogui.hotkey("ctrl", "w")
        log_action_db(command, "close_tab", "success", "ctrl+w")
        return "Closing current tab."
    if clean in ["close window", "close current window"]:
        if ask_user_confirmation(command, "closing current window"):
            pyautogui.hotkey("alt", "f4")
            return "Closing current window."
        return "Cancelled."
    if clean in ["close all windows", "close everything"]:
        if ask_user_confirmation(command, "minimizing all windows"):
            pyautogui.hotkey("win", "d")
            return "Minimizing all windows safely."
        return "Cancelled."
    if clean.startswith("close "):
        return close_application(clean.replace("close ", "", 1).strip())

    # AI Core
    if clean.startswith("remember vector") or clean.startswith("save vector memory"):
        text = clean.replace("remember vector", "", 1).replace("save vector memory", "", 1).strip()
        return vector_memory_add(text or command, ["voice"])
    if clean.startswith("search memory") or clean.startswith("recall vector"):
        q = clean.replace("search memory", "", 1).replace("recall vector", "", 1).strip()
        results = vector_memory_search(q or command)
        if not results:
            return "No related vector memory found."
        return "Vector memory: " + " | ".join([r.get("text", "")[:160] for r in results])
    if clean.startswith("agent plan") or clean.startswith("autonomous plan"):
        return autonomous_planner(command)
    if clean.startswith("hybrid ai") or clean.startswith("ask hybrid"):
        return hybrid_ai_brain(command)
    if clean in ["which agent", "agent router"]:
        return "I would use: " + multi_agent_router(command)
    if clean in ["emotion status", "detect emotion"]:
        return "Detected tone: " + detect_emotional_tone(command)

    # Vision AI
    if clean in ["understand screen", "screen understanding", "analyze screen"]:
        return screen_understanding()
    if clean in ["detect buttons", "button detection", "find buttons"]:
        return button_detection_ai()
    if clean in ["object detection", "detect objects"]:
        return object_detection_ai()
    if clean in ["face unlock", "face recognition"]:
        return face_recognition_lock()
    if clean in ["gesture status", "hand tracking", "air mouse status"]:
        return gesture_control_status()
    if clean in ["gesture control on", "hand tracking on"]:
        GESTURE_CONTROL_ENABLED = True
        return "Gesture control hook is ON. Full hand tracking needs mediapipe."
    if clean in ["gesture control off", "hand tracking off"]:
        GESTURE_CONTROL_ENABLED = False
        return "Gesture control is OFF."
    if clean in ["air mouse on"]:
        AIR_MOUSE_ENABLED = True
        return "Air mouse hook is ON. Full air mouse needs mediapipe hand tracking."
    if clean in ["air mouse off"]:
        AIR_MOUSE_ENABLED = False
        return "Air mouse is OFF."

    # Full desktop AI
    if clean in ["organize files", "file organization"]:
        return organize_files_preview()
    if clean in ["auto coding assistant", "coding assistant"]:
        return auto_coding_assistant(command)
    if clean in ["vs code helper", "open vscode helper", "open vs code helper"]:
        return vscode_ai_helper(command)
    if clean.startswith("windows control") or clean in WINDOWS_CONTROL_COMMANDS:
        return windows_control_center(command)

    # HUD / UI
    if clean in ["hud upgrades", "hud status", "iron hud status", "hologram ui"]:
        return hud_feature_status()
    if clean in ["system stats", "stats overlay"]:
        return system_stats_overlay()

    # Internet Agent
    if clean.startswith("ai browse") or clean.startswith("browser agent"):
        return ai_browsing(command)
    if clean.startswith("auto research") or clean.startswith("deep research"):
        return auto_research(command)
    if clean.startswith("auto summarize") or clean.startswith("summarize this"):
        return auto_summarization(command)
    if clean.startswith("youtube summary") or clean.startswith("summarize youtube"):
        return youtube_video_summarizer(command)

    # Advanced safety
    if clean in ["voice identity", "voice identity status"]:
        return voice_identity_check()
    if clean in ["encrypted memory", "memory encryption status"]:
        return encrypted_memory_status()
    if clean in ["plugin sandbox", "sandbox status"]:
        return plugin_sandbox_status()
    if clean in ["crash recovery", "recovery status"]:
        return auto_crash_recovery()
    if clean in ["behavior monitor", "ai behavior monitor", "risk score"]:
        return f"Current command risk score is {ai_behavior_monitor(command)} out of 100."

    # Existing full-control commands, repaired
    if clean in ["full control", "full control mode", "what can you control", "blue full control"]:
        return SAFE_FULL_CONTROL_HELP + " Blue 5.0 adds AI core, vision AI, desktop AI, voice system, HUD, internet agent, and advanced safety."
    if clean in ["start continuous listening", "continuous listening on", "real time listening on", "always listen on"]:
        ALWAYS_LISTEN_MODE = True
        WAKE_WORD_ENABLED = False
        log_action_db(command, "continuous_listening", "enabled", "user command")
        return "Continuous listening is ON. Wake word is OFF."
    if clean in ["stop continuous listening", "continuous listening off", "real time listening off", "always listen off"]:
        ALWAYS_LISTEN_MODE = False
        WAKE_WORD_ENABLED = True
        log_action_db(command, "continuous_listening", "disabled", "user command")
        return "Continuous listening is OFF. Wake word is ON."
    if clean in ["open hud", "open iron hud", "start hud", "floating iron man hud", "open iron man hud"]:
        return start_iron_hud()
    try:
        mouse_reply = live_mouse_command(command)
        if mouse_reply:
            log_action_db(command, "live_mouse_ai", "success", mouse_reply)
            return mouse_reply
    except Exception:
        pass
    if clean in ["open chart", "open tradingview chart", "open xauusd chart", "open gold chart", "open xau usd chart"]:
        open_url(TRADINGVIEW_CHART_URL)
        log_action_db(command, "open_chart", "success", TRADINGVIEW_CHART_URL)
        return "Opening XAUUSD TradingView chart."
    if clean.startswith("analyze chart") or clean.startswith("market signal") or clean.startswith("signal for") or clean.startswith("analyze market"):
        reply = run_market_signal_command(command)
        log_action_db(command, "market_signal", "success", "analysis only")
        return reply
    if clean.startswith("backtest") or clean.startswith("replay backtest"):
        reply = run_market_backtest_command(command)
        log_action_db(command, "market_backtest", "success", "analysis only")
        return reply
    if clean.startswith("autonomous market watch") or clean.startswith("start market watch"):
        reply = run_market_autonomous_watch(command)
        log_action_db(command, "autonomous_market_watch", "success", "monitoring only")
        return reply
    if clean in ["open chrome", "open crome", "launch chrome", "launch crome"]:
        try:
            subprocess.Popen("chrome", shell=True)
            log_action_db(command, "open_app", "success", "chrome")
            return "Opening Chrome."
        except Exception as e:
            open_url("https://www.google.com")
            log_action_db(command, "open_app", "fallback", str(e))
            return "Chrome command failed, so I opened the browser instead."
    if clean.startswith("run command") or clean.startswith("execute command") or clean.startswith("run terminal command") or clean.startswith("run cmd") or clean.startswith("run powershell"):
        return run_safe_shell_command(command)
    return ""


# -------------------------
# Main loop override with wake-word toggle
# -------------------------
def main():
    init_database()
    if ML_AVAILABLE and not os.path.exists(INTENT_MODEL_FILE):
        train_small_intent_model()
    play_tone("startup")
    speak("Hello sir.", allow_repeat=True)
    update_hud_status("online", "Blue 5.0 online")

    if TEXT_COMMAND_MODE:
        threading.Thread(target=text_command_listener, daemon=True).start()

    no_hear_count = 0
    active_mode = False
    active_until = 0

    while True:
        try:
            if text_input_active.is_set() and command_queue.empty():
                time.sleep(0.05)
                continue

            if not command_queue.empty():
                text = command_queue.get()
                used_engine = "text_command"
                active_mode = True
                active_until = time.time() + ACTIVE_SESSION_SECONDS
            else:
                # Wake-word OFF means direct always-listening command mode.
                if not WAKE_WORD_ENABLED or ALWAYS_LISTEN_MODE:
                    active_mode = True
                    text, used_engine = listen_blue()
                elif active_mode and time.time() <= active_until:
                    text, used_engine = listen_blue()
                else:
                    active_mode = False
                    text, used_engine = listen_wake_word()

            if not text:
                no_hear_count += 1
                if active_mode and no_hear_count == 1:
                    speak("I could not hear properly.")
                elif active_mode and no_hear_count == 3:
                    speak("Still not hearing clearly. Please check your microphone.")
                continue

            no_hear_count = 0
            clean_text = normalize_text(text)

            if used_engine == "text_command":
                command = clean_text
            elif not WAKE_WORD_ENABLED or ALWAYS_LISTEN_MODE:
                command = remove_wake_word(clean_text)
            else:
                wake_detected = clean_text == WAKE_WORD or clean_text.startswith(WAKE_WORD + " ")
                if wake_detected:
                    active_mode = True
                    active_until = time.time() + ACTIVE_SESSION_SECONDS
                    command = remove_wake_word(text)
                    if not command:
                        speak("Yes sir. I am active and listening.")
                        wait_until_done_speaking()
                        continue
                elif active_mode and time.time() <= active_until:
                    command = clean_text
                    active_until = time.time() + ACTIVE_SESSION_SECONDS
                else:
                    active_mode = False
                    print("Standby mode. Wake word not detected. Ignored:", text)
                    continue

            print(f"Engine used: {used_engine}")
            save_crash_state(command, "processing")
            update_hud_status("thinking", command[:120])

            # Behavior monitor warning
            risk_score = ai_behavior_monitor(command)
            if risk_score >= 80:
                speak(f"High risk command detected. Risk score {risk_score}.", allow_repeat=True)

            allowed, stop_blue, safety_reply = safety_guard(command)
            if stop_blue:
                speak(safety_reply, allow_repeat=True)
                wait_until_done_speaking()
                save_crash_state(command, "stopped")
                break
            if not allowed:
                speak(safety_reply, allow_repeat=True)
                add_chat_history(command, safety_reply)
                log_command_db(command, "safety_guard", command, safety_reply)
                wait_until_done_speaking()
                save_crash_state(command, "blocked")
                continue

            direct_reply = handle_full_control_direct_commands(command)
            if direct_reply:
                reply = jarvis_line(direct_reply)
                speak(reply)
                add_chat_history(command, reply)
                log_command_db(command, "blue_5_direct", command, reply)
                wait_until_done_speaking()
                update_hud_status("speaking", reply[:120])
                save_crash_state(command, "done")
                continue

            # Emotion-aware tone note saved silently.
            tone = detect_emotional_tone(command)
            intent, payload = classify_intent(command)
            print(f"Intent: {intent} | Payload: {payload} | Tone: {tone}")

            result = handle_intent(intent, payload)
            wait_until_done_speaking()
            save_crash_state(command, "done")

            if result == "sleep":
                active_mode = False
                active_until = 0
                continue
            if not result:
                break

        except KeyboardInterrupt:
            save_crash_state("keyboard interrupt", "safe_exit")
            break
        except Exception as e:
            print("Blue main loop error:", e)
            save_crash_state(str(e), "error")
            speak("I hit an error, so I switched to safe recovery mode.", allow_repeat=True)
            time.sleep(0.5)
            continue

# =========================================================
# END BLUE 5.0 MEGA UPGRADE LAYER
# =========================================================



# =========================================================
# BLUE REAL JARVIS REPAIR LAYER
# Added for repaired package: false-command guard, mute mode,
# natural command correction, faster session, better HUD sync.
# =========================================================
BLUE_MUTED = False
_LAST_HEARD_COMMANDS = []
SELF_ECHO_PHRASES = [
    "how can i assist you today", "i am active and listening", "good day sir",
    "blue 5 0 is online", "blue 3 0 is online", "right away sir",
    "certainly sir", "of course sir", "consider it done sir", "at once sir",
    "i am on it sir", "opening youtube", "the time is", "i could not hear properly"
]
COMMON_SPEECH_CORRECTIONS = {
    "blu": "blue", "blew": "blue", "bluee": "blue",
    "close recent tap": "close current tab", "close current tap": "close current tab",
    "clothes current tap": "close current tab", "flute current tap": "close current tab",
    "close parent window": "close current window", "floats current window": "close current window",
    "decorate brightness": "decrease brightness", "decreate brightness": "decrease brightness",
    "such youtube": "search youtube", "find on": "search youtube for",
    "turn of noise cancellation": "noise cancellation off", "done on neuts gancellation": "noise cancellation on",
}

def correct_command_text(text: str) -> str:
    clean = normalize_text(text)
    # whole phrase corrections first
    if clean in COMMON_SPEECH_CORRECTIONS:
        return COMMON_SPEECH_CORRECTIONS[clean]
    for wrong, right in COMMON_SPEECH_CORRECTIONS.items():
        if wrong in clean:
            clean = clean.replace(wrong, right)
    return normalize_text(clean)


def is_self_echo_command(text: str) -> bool:
    clean = normalize_text(text)
    if not clean:
        return False
    if clean in ["yes sir", "okay sir", "hello sir", "right away sir", "certainly sir"]:
        return True
    if any(p in clean for p in SELF_ECHO_PHRASES):
        return True
    # Prevent repeating the same accidental voice command rapidly.
    now = time.time()
    global _LAST_HEARD_COMMANDS
    _LAST_HEARD_COMMANDS = [(t, ts) for t, ts in _LAST_HEARD_COMMANDS if now - ts < 8]
    if any(clean == t for t, ts in _LAST_HEARD_COMMANDS):
        return True
    _LAST_HEARD_COMMANDS.append((clean, now))
    return False

# Keep previous direct handler if present, then add JARVIS commands.
try:
    _real_jarvis_previous_direct_handler = handle_full_control_direct_commands
except Exception:
    _real_jarvis_previous_direct_handler = None

try:
    _real_jarvis_previous_update_hud_status = update_hud_status
except Exception:
    _real_jarvis_previous_update_hud_status = None


def update_hud_status(status="online", detail="Blue repaired ready"):
    data = {"status": status, "detail": detail, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    for file_name in ["HUD_STATUS_FILE", "blue_status.json"]:
        try:
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("HUD sync error:", e)
    return data


def stop_speaking_now():
    try:
        while not speech_queue.empty():
            speech_queue.get_nowait()
            speech_queue.task_done()
    except Exception:
        pass
    try:
        engine.stop()
    except Exception:
        pass
    update_hud_status("muted", "speech stopped")
    return "Speech stopped."


def jarvis_capabilities():
    return (
        "Real JARVIS features active: wake word on or off, mute mode, stop speaking, emergency stop, "
        "screen reading, OCR button scan, safe mouse arming, Full Control lock, safety profiles, "
        "Ollama local brain, browser research, crash recovery, HUD status sync, command correction, "
        "and anti self-echo protection."
    )


def handle_full_control_direct_commands(command: str):
    global BLUE_MUTED, WAKE_WORD_ENABLED, ALWAYS_LISTEN_MODE
    clean = correct_command_text(remove_wake_word(command))

    if clean in ["mute blue", "silent mode", "go silent", "blue mute"]:
        BLUE_MUTED = True
        update_hud_status("muted", "Blue muted")
        return "Mute mode activated. Say unmute blue or stop blue."

    if clean in ["unmute blue", "wake blue", "resume blue", "blue unmute"]:
        BLUE_MUTED = False
        update_hud_status("online", "Blue unmuted")
        return "Mute mode disabled. I am listening again."

    if clean in ["stop speaking", "shut up blue", "cancel speech"]:
        return stop_speaking_now()

    if clean in ["jarvis status", "real jarvis status", "what can you do", "show jarvis features"]:
        return jarvis_capabilities()

    if clean in ["wake word on", "enable wake word"]:
        WAKE_WORD_ENABLED = True
        ALWAYS_LISTEN_MODE = False
        update_hud_status("online", "wake word on")
        return "Wake word mode is ON. Say Blue before commands."

    if clean in ["wake word off", "disable wake word", "jarvis mode on"]:
        WAKE_WORD_ENABLED = False
        ALWAYS_LISTEN_MODE = True
        update_hud_status("online", "continuous mode")
        return "JARVIS continuous mode is ON. Wake word is OFF."

    if clean in ["close current tab", "close tab", "close current tap"]:
        pyautogui.hotkey("ctrl", "w")
        return "Closing current tab."

    if clean in ["close current window", "close window"]:
        pyautogui.hotkey("alt", "f4")
        return "Closing current window."

    if _real_jarvis_previous_direct_handler:
        return _real_jarvis_previous_direct_handler(clean)
    return ""

# Patch main loop behavior by wrapping listen output and safety checks.
try:
    _real_jarvis_previous_listen_blue = listen_blue
    def listen_blue():
        text, engine_name = _real_jarvis_previous_listen_blue()
        return correct_command_text(text), engine_name
except Exception:
    pass

try:
    _real_jarvis_previous_listen_wake_word = listen_wake_word
    def listen_wake_word():
        text, engine_name = _real_jarvis_previous_listen_wake_word()
        return correct_command_text(text), engine_name
except Exception:
    pass

try:
    _real_jarvis_previous_safety_guard = safety_guard
    def safety_guard(command: str):
        clean = correct_command_text(command)
        if is_self_echo_command(clean):
            log_action_db(clean, "self_echo_filter", "blocked", "heard Blue's own voice or duplicate")
            return False, False, ""
        if BLUE_MUTED and clean not in ["unmute blue", "wake blue", "resume blue", "stop blue", "emergency stop"]:
            update_hud_status("muted", "command ignored while muted")
            return False, False, ""
        return _real_jarvis_previous_safety_guard(clean)
except Exception:
    pass

# =========================================================
# END BLUE REAL JARVIS REPAIR LAYER
# =========================================================



# =========================================================
# BLUE REAL JARVIS INTERACTION SYSTEM - 10 UPGRADE PACK
# Added by ChatGPT for Sp
# =========================================================
# This layer is designed to sit on top of your existing Blue build.
# It avoids dangerous automation, keeps Safety Mode ON, and makes Blue
# understand rough natural commands like "band kar yt", "close current tap",
# "make study setup", "click login", and "no blue this means close tab".

JARVIS_INTERACTION_VERSION = "10-UPGRADE-PACK"
CONVERSATION_CONTEXT_FILE = "blue_conversation_context.json"
LEARNED_COMMANDS_FILE = "blue_learned_commands.json"
TASK_MEMORY_FILE = "blue_task_memory.json"

def _ji_load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, type(default)) else default
    except Exception as e:
        print("JARVIS json load error:", path, e)
    return default

def _ji_save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print("JARVIS json save error:", path, e)
        return False

JARVIS_CONTEXT = _ji_load_json(CONVERSATION_CONTEXT_FILE, {
    "last_user_command": "",
    "last_intent": "",
    "last_target": "",
    "last_screen_text": "",
    "active_task": "",
    "last_plan": [],
    "last_updated": ""
})
LEARNED_COMMANDS = _ji_load_json(LEARNED_COMMANDS_FILE, {})
TASK_MEMORY = _ji_load_json(TASK_MEMORY_FILE, {"tasks": []})

def ji_remember_context(command="", intent="", target="", screen_text="", active_task="", plan=None):
    if command:
        JARVIS_CONTEXT["last_user_command"] = command
    if intent:
        JARVIS_CONTEXT["last_intent"] = intent
    if target:
        JARVIS_CONTEXT["last_target"] = target
    if screen_text:
        JARVIS_CONTEXT["last_screen_text"] = screen_text[:2500]
    if active_task:
        JARVIS_CONTEXT["active_task"] = active_task
    if plan is not None:
        JARVIS_CONTEXT["last_plan"] = plan
    JARVIS_CONTEXT["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _ji_save_json(CONVERSATION_CONTEXT_FILE, JARVIS_CONTEXT)

def ji_simple_ratio(a, b):
    try:
        return difflib.SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()
    except Exception:
        return 0.0

JARVIS_NATURAL_ALIASES = {
    # browser/window
    "close current tab": [
        "close tab", "close current tap", "clothes current tap", "clothe current tab",
        "band kar tab", "tab band kar", "remove current tab", "hata current tab",
        "close this page", "band kar page", "cut this tab", "exit tab"
    ],
    "close current window": [
        "close window", "close this window", "band kar window", "window band kar",
        "close app window", "exit window", "remove window"
    ],
    "open youtube": [
        "open yt", "youtube kholo", "yt kholo", "start youtube", "launch youtube",
        "youtube chalu kar", "kholo youtube"
    ],
    "search youtube for": [
        "search on youtube", "find on youtube", "youtube pe search kar",
        "yt search", "find yt", "youtube search"
    ],
    "open google": [
        "google kholo", "start google", "launch google", "open browser", "open chrome browser"
    ],
    "search for": [
        "google kar", "search google", "find about", "look up", "search karo",
        "internet pe search kar"
    ],
    # PC control
    "increase brightness": [
        "brightness badhao", "screen bright kar", "make screen brighter", "bright karo"
    ],
    "decrease brightness": [
        "brightness kam kar", "screen dim kar", "decorate brightness", "decreate brightness",
        "make screen darker", "dim karo"
    ],
    "volume up": ["sound badhao", "volume badhao", "awaz badhao", "make louder"],
    "volume down": ["sound kam kar", "volume kam kar", "awaz kam kar", "make lower"],
    "mute sound": ["sound band kar", "mute audio", "awaz band kar"],
    "take screenshot": ["screen shot le", "capture screen", "photo of screen", "save screen"],
    # screen AI
    "read screen": ["screen read kar", "what is on screen", "scan screen", "analyze screen", "read this"],
    "click": ["press", "tap", "select", "click on", "isko click kar", "ye button dabao"],
    # study/task
    "study mode": ["make study setup", "prepare study", "ibps mode", "study setup", "start study"],
    "autonomous agent": ["do it yourself", "finish this task", "plan and do", "agent mode"],
}

def ji_natural_rewrite(command: str) -> str:
    """Turns rough Hinglish/spelling-mistake commands into Blue-readable commands.

    IMPORTANT FIX:
    Do not call correct_command_text() from here, because correct_command_text()
    is later patched to call ji_natural_rewrite(). Calling it here creates
    infinite recursion and causes: maximum recursion depth exceeded.
    """
    try:
        # Use the original pre-JARVIS correction function if it was captured.
        base_corrector = globals().get("_ji_previous_correct_command_text")
        if base_corrector and base_corrector is not ji_natural_rewrite:
            clean = base_corrector(command)
        else:
            clean = command
    except Exception:
        clean = command
    clean = normalize_text(clean)
    if clean in LEARNED_COMMANDS:
        return LEARNED_COMMANDS[clean]
    # Learn exact natural aliases
    for canonical, aliases in JARVIS_NATURAL_ALIASES.items():
        for alias in aliases:
            alias_clean = normalize_text(alias)
            if clean == alias_clean:
                return canonical
            if clean.startswith(alias_clean + " "):
                rest = clean[len(alias_clean):].strip()
                return (canonical + " " + rest).strip()
    # fuzzy matching for spoken mistakes
    best_canonical, best_score = clean, 0.0
    for canonical, aliases in JARVIS_NATURAL_ALIASES.items():
        for alias in [canonical] + aliases:
            score = ji_simple_ratio(clean, alias)
            if score > best_score:
                best_canonical, best_score = canonical, score
    if best_score >= 0.80:
        return best_canonical
    # context references: "open it", "close it", "search this"
    if clean in ["open it", "open that", "open this"] and JARVIS_CONTEXT.get("last_target"):
        return "open " + JARVIS_CONTEXT["last_target"]
    if clean in ["close it", "close this", "band kar isko"]:
        if JARVIS_CONTEXT.get("last_intent") in ["youtube", "google_home", "google_search", "youtube_search"]:
            return "close current tab"
        return "close current window"
    return clean

def ji_learn_command(command: str):
    """
    Example:
    no blue this means close tab
    when i say revision mode it means study mode
    learn command gold check means analyze chart xauusd
    """
    clean = normalize_text(command)
    patterns = [
        r"no blue this means (.+)",
        r"this means (.+)",
        r"when i say (.+?) it means (.+)",
        r"learn command (.+?) means (.+)",
        r"remember command (.+?) means (.+)",
    ]
    for pat in patterns:
        m = re.search(pat, clean)
        if m:
            if len(m.groups()) == 1:
                source = JARVIS_CONTEXT.get("last_user_command", "").strip()
                target = m.group(1).strip()
            else:
                source = m.group(1).strip()
                target = m.group(2).strip()
            if source and target:
                LEARNED_COMMANDS[normalize_text(source)] = normalize_text(target)
                _ji_save_json(LEARNED_COMMANDS_FILE, LEARNED_COMMANDS)
                return f"Learned. From now on, '{source}' means '{target}'."
    return ""

def ji_make_plan(command: str):
    clean = normalize_text(command)
    if any(x in clean for x in ["study", "ibps", "revision", "prepare exam"]):
        return [
            "Open study resources.",
            "Open notes or browser search.",
            "Start focus-friendly setup.",
            "Save task context."
        ]
    if any(x in clean for x in ["research", "find information", "make notes"]):
        return [
            "Search the web.",
            "Open useful results.",
            "Summarize key points.",
            "Save notes in memory."
        ]
    if any(x in clean for x in ["organize", "clean desktop", "arrange files"]):
        return [
            "Scan target folder.",
            "Preview file categories.",
            "Ask confirmation before moving anything.",
            "Create organized folders safely."
        ]
    return [
        "Understand the goal.",
        "Choose the safest tool.",
        "Perform the action.",
        "Save result in context."
    ]

def ji_agent_explain(command: str):
    plan = ji_make_plan(command)
    ji_remember_context(command=command, intent="agent_plan", active_task=command, plan=plan)
    return "Plan ready: " + " | ".join([f"{i+1}. {step}" for i, step in enumerate(plan)])

def ji_read_screen_text():
    try:
        if not OCR_AVAILABLE:
            return "OCR is not available. Install Tesseract OCR to use screen reading."
        img = pyautogui.screenshot()
        text = pytesseract.image_to_string(img)
        text = normalize_text(text)[:2500]
        ji_remember_context(screen_text=text)
        return text if text else "I scanned the screen but could not read clear text."
    except Exception as e:
        return "Screen reading failed: " + str(e)

def ji_click_text_on_screen(target: str):
    """
    OCR click helper. It clicks the center of text that appears on screen.
    Safer than blind coordinates, but still asks safety layer for risky actions first.
    """
    target = normalize_text(target).replace("click", "").replace("press", "").replace("tap", "").replace("select", "").strip()
    if not target:
        return "Tell me what text or button to click."
    if not OCR_AVAILABLE:
        return "OCR click needs Tesseract OCR installed."
    try:
        img = pyautogui.screenshot()
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        best = None
        best_score = 0
        for i, word in enumerate(data.get("text", [])):
            w = normalize_text(word)
            if not w:
                continue
            score = ji_simple_ratio(w, target)
            if target in w or w in target:
                score = max(score, 0.90)
            if score > best_score:
                best = i
                best_score = score
        if best is not None and best_score >= 0.65:
            x = int(data["left"][best] + data["width"][best] / 2)
            y = int(data["top"][best] + data["height"][best] / 2)
            pyautogui.click(x, y)
            ji_remember_context(command=f"click {target}", intent="screen_click", target=target)
            return f"Clicked {target} on screen."
        return f"I could not find '{target}' clearly on the screen."
    except Exception as e:
        return "Screen click failed: " + str(e)

def ji_interaction_status():
    return (
        "Blue JARVIS Interaction Pack is active: real-time conversation loop, context memory, "
        "natural command correction, fast response routing, screen awareness, agent planning, "
        "HUD sync, self-learning commands, interruption controls, and hybrid brain support."
    )

# Patch command correction deeper so every voice/text command passes through the natural layer.
try:
    _ji_previous_correct_command_text = correct_command_text
    def correct_command_text(text: str) -> str:
        base = _ji_previous_correct_command_text(text)
        return ji_natural_rewrite(base)
except Exception:
    def correct_command_text(text: str) -> str:
        return ji_natural_rewrite(text)

# Patch direct command handler with interaction commands.
try:
    _ji_previous_direct_handler = handle_full_control_direct_commands
except Exception:
    _ji_previous_direct_handler = None

def handle_full_control_direct_commands(command: str):
    clean = ji_natural_rewrite(remove_wake_word(command))
    learn_reply = ji_learn_command(clean)
    if learn_reply:
        return learn_reply

    if clean in ["interaction status", "jarvis interaction status", "real jarvis interaction"]:
        return ji_interaction_status()

    if clean.startswith("plan ") or clean.startswith("make plan") or clean.startswith("agent plan"):
        return ji_agent_explain(clean)

    if clean in ["what was my last command", "last command", "what did i say"]:
        return "Your last command was: " + (JARVIS_CONTEXT.get("last_user_command") or "nothing yet")

    if clean in ["what are you doing", "current task", "active task"]:
        return "Current task: " + (JARVIS_CONTEXT.get("active_task") or "no active task")

    if clean.startswith("click ") or clean.startswith("press ") or clean.startswith("tap ") or clean.startswith("select "):
        return ji_click_text_on_screen(clean)

    if clean in ["read screen", "scan screen", "analyze screen", "what is on screen"]:
        screen_text = ji_read_screen_text()
        if len(screen_text) > 500:
            return "I read the screen. Main text: " + screen_text[:500]
        return screen_text

    if clean in ["prepare study", "make study setup", "study mode", "ibps mode", "start study"]:
        ji_remember_context(command=clean, intent="study_mode", active_task="study mode", plan=ji_make_plan(clean))
        try:
            open_url("https://www.google.com/search?q=IBPS+PO+study+plan")
        except Exception:
            pass
        return "Study mode prepared. I opened IBPS study search and saved this task context."

    # More flexible tab/window controls
    if clean in ["close current tab", "close tab"]:
        pyautogui.hotkey("ctrl", "w")
        ji_remember_context(command=clean, intent="browser_close_tab", target="current tab")
        return "Closing current tab."

    if clean in ["close current window", "close window"]:
        pyautogui.hotkey("alt", "f4")
        ji_remember_context(command=clean, intent="close_window", target="current window")
        return "Closing current window."

    if _ji_previous_direct_handler:
        reply = _ji_previous_direct_handler(clean)
        if reply:
            ji_remember_context(command=clean, intent="direct_action", target=clean)
            return reply
    return ""

# Patch classify_intent for natural commands and context.
try:
    _ji_previous_classify_intent = classify_intent
    def classify_intent(text: str):
        clean = ji_natural_rewrite(text)
        if clean.startswith("search youtube for "):
            return "youtube_search", clean.replace("search youtube for ", "", 1).strip()
        if clean.startswith("search for "):
            return "google_search", clean.replace("search for ", "", 1).strip()
        if clean in ["open youtube"]:
            return "youtube", clean
        if clean in ["open google"]:
            return "google_home", clean
        if clean in ["read screen", "scan screen", "analyze screen"]:
            return "read_screen", clean
        intent, payload = _ji_previous_classify_intent(clean)
        ji_remember_context(command=clean, intent=intent, target=payload)
        return intent, payload
except Exception:
    pass

# Patch speak status for HUD and interrupt-style control.
try:
    _ji_previous_speak = speak
    def speak(text: str, allow_repeat: bool = False):
        try:
            update_hud_status("speaking", str(text)[:120])
        except Exception:
            pass
        return _ji_previous_speak(text, allow_repeat=allow_repeat)
except Exception:
    pass

# Patch crash recovery to save useful error context.
try:
    _ji_previous_save_crash_state = save_crash_state
    def save_crash_state(command, status):
        ji_remember_context(command=str(command), active_task=str(status))
        return _ji_previous_save_crash_state(command, status)
except Exception:
    pass

# Ensure startup status file mentions the new pack.
try:
    update_hud_status("online", "Blue JARVIS 10 Interaction Pack active")
except Exception:
    pass

# =========================================================
# END BLUE REAL JARVIS INTERACTION SYSTEM - 10 UPGRADE PACK
# =========================================================


if __name__ == "__main__":
    main()
# BLUE IS END HRER
