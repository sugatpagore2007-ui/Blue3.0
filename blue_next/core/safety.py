
import re

SECRET_WORDS = [
    "password","passcode","otp","one time password","pin","cvv","card number",
    "atm pin","upi pin","secret key","api key","private key","recovery phrase","seed phrase"
]

BLOCKED_PATTERNS = [
    "format c:", "format d:", "diskpart", "clean all", "delete partition",
    "rm -rf /", "rm -rf *", "del /f /s /q", "rmdir /s /q", "cipher /w",
    "bcdedit", "reg delete", "takeown /f c:\\", "shutdown /s /t 0",
    "shutdown /r /t 0"
]

RISKY_WORDS = [
    "delete", "remove file", "erase", "format", "shutdown", "restart", "install",
    "uninstall", "send email", "send mail", "send message", "whatsapp message",
    "payment", "pay ", "upi", "terminal", "cmd", "powershell", "run command",
    "execute command", "shell"
]

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s:/\\.-]", " ", text.lower())).strip()

def check_safety(command: str):
    clean = normalize(command)
    if clean in ["stop blue", "blue stop", "emergency stop", "kill blue"]:
        return {"allowed": False, "stop": True, "needs_confirmation": False, "reason": "emergency stop"}
    if any(w in clean for w in SECRET_WORDS):
        return {"allowed": False, "stop": False, "needs_confirmation": False, "reason": "secret/private data blocked"}
    if any(p in clean for p in BLOCKED_PATTERNS):
        return {"allowed": False, "stop": False, "needs_confirmation": False, "reason": "dangerous destructive command blocked"}
    if any(w in clean for w in RISKY_WORDS):
        return {"allowed": True, "stop": False, "needs_confirmation": True, "reason": "risky action confirmation required"}
    return {"allowed": True, "stop": False, "needs_confirmation": False, "reason": "safe"}
