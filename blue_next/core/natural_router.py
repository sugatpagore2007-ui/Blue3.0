
import re, difflib
from blue_next.memory.memory_store import MEMORY

CORRECTIONS = {
    "blu": "blue", "bleu": "blue", "yt": "youtube", "youtub": "youtube",
    "crome": "chrome", "tap": "tab", "clothes": "close", "clode": "close",
    "decorade": "decrease", "decorate brightness": "decrease brightness",
    "band kar": "close", "hata": "close", "khol": "open", "kholo": "open",
    "neuts gancellation": "noise cancellation", "flute current tab": "close current tab",
    "close recent tab": "close current tab", "close recent tap": "close current tab",
}

INTENTS = {
    "open_website": ["open youtube","open google","open gmail","open github","open whatsapp","open chatgpt"],
    "open_app": ["open chrome","open calculator","open notepad","open vs code","open explorer","open settings"],
    "close_tab": ["close current tab","close tab","band kar tab","remove current tab"],
    "close_window": ["close window","close current window","band kar window"],
    "read_screen": ["read screen","scan screen","what is on screen","analyze screen"],
    "click_text": ["click", "press", "select"],
    "search_web": ["search for","google","look up","find about"],
    "youtube_search": ["search youtube","youtube search","find on youtube"],
    "remember": ["remember that","save this","note this"],
    "teach": ["when i say","no blue this means","this means"],
    "plan": ["plan","make setup","prepare","do task","agent"],
    "internet_learn": ["learn from internet","research internet","background learning","internet learning"],
    "status": ["jarvis status","blue status","what are you doing","system status"],
    "stop": ["stop blue","emergency stop","kill blue"],
}

WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "whatsapp": "https://web.whatsapp.com",
    "chatgpt": "https://chatgpt.com",
}

def normalize(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r"[^\w\s:/.-]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    for wrong, right in CORRECTIONS.items():
        t = t.replace(wrong, right)
    return t

def fuzzy_intent(text: str):
    clean = normalize(text)
    learned = MEMORY.get_learned_command(clean)
    if learned:
        return learned, clean
    best = ("chat", 0.0)
    for intent, patterns in INTENTS.items():
        for p in patterns:
            if p in clean:
                return intent, clean
            score = difflib.SequenceMatcher(None, clean, p).ratio()
            if score > best[1]: best = (intent, score)
    if best[1] > 0.66:
        return best[0], clean
    if clean.startswith("open "): return "open_dynamic", clean
    if clean.startswith("close "): return "close_dynamic", clean
    return "chat", clean

def parse_teach(clean: str):
    # "when i say revision mode it means study mode"
    m = re.search(r"when i say (.+?) it means (.+)", clean)
    if m: return m.group(1).strip(), m.group(2).strip()
    m = re.search(r"no blue (.+?) means (.+)", clean)
    if m: return m.group(1).strip(), m.group(2).strip()
    m = re.search(r"(.+?) this means (.+)", clean)
    if m: return m.group(1).strip(), m.group(2).strip()
    return "", ""

def route(command: str):
    intent, clean = fuzzy_intent(command)
    payload = {"raw": command, "clean": clean, "intent": intent}
    if intent in ["open_website","open_dynamic"]:
        for name, url in WEBSITES.items():
            if name in clean:
                payload.update({"target": name, "url": url})
                return payload
    if intent == "youtube_search":
        q = clean.replace("search youtube for","").replace("search youtube","").replace("youtube search","").strip()
        payload["query"] = q or "latest ai"
    if intent == "search_web":
        q = clean.replace("search for","").replace("google","").replace("look up","").strip()
        payload["query"] = q or clean
    if intent == "click_text":
        payload["text"] = clean.split(" ",1)[1] if " " in clean else ""
    if intent == "teach":
        phrase, meaning = parse_teach(clean)
        payload.update({"phrase": phrase, "meaning": meaning})
    if intent == "internet_learn":
        payload["topic"] = clean.replace("learn from internet","").replace("research internet","").replace("background learning","").strip() or "AI technology"
    return payload
