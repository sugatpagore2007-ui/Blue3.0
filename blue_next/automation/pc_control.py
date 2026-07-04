
import os, subprocess, webbrowser
from urllib.parse import quote_plus
import pyautogui

APPS = {
    "notepad": "notepad",
    "calculator": "calc",
    "chrome": "chrome",
    "vs code": "code",
    "vscode": "code",
    "explorer": "explorer",
    "file explorer": "explorer",
    "settings": "start ms-settings:",
}

def open_url(url: str):
    webbrowser.open(url)
    return f"Opening {url}"

def search_web(query: str):
    return open_url("https://www.google.com/search?q=" + quote_plus(query))

def search_youtube(query: str):
    return open_url("https://www.youtube.com/results?search_query=" + quote_plus(query))

def open_app(name: str):
    name = name.lower().strip()
    for key, cmd in APPS.items():
        if key in name:
            subprocess.Popen(cmd, shell=True)
            return f"Opening {key}"
    return f"I don't know that app yet: {name}"

def close_current_tab():
    pyautogui.hotkey("ctrl","w")
    return "Closing current tab."

def close_current_window():
    pyautogui.hotkey("alt","f4")
    return "Closing current window."

def screenshot():
    path = os.path.abspath("blue_next/data/screenshot.png")
    img = pyautogui.screenshot()
    img.save(path)
    return f"Screenshot saved: {path}"
