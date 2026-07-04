
from blue_next.core.natural_router import route
from blue_next.core.safety import check_safety
from blue_next.automation import pc_control
from blue_next.vision import screen_ai
from blue_next.brain.llm_router import ask_brain
from blue_next.memory.memory_store import MEMORY
from blue_next.memory.vector_memory import VECTOR_MEMORY
from blue_next.learning.internet_learning import background_research, research_url
from blue_next.core.status import set_status

def plan_steps(command: str):
    prompt = f"Create a short safe step plan for this desktop assistant command: {command}"
    answer = ask_brain(prompt, fast=True)
    return answer

def execute(command: str):
    set_status("thinking", command[:120])
    safety = check_safety(command)
    if safety.get("stop"):
        set_status("stopped", "Emergency stop")
        return "Emergency stop activated. Blue is shutting down safely.", True
    if not safety.get("allowed"):
        set_status("blocked", safety["reason"])
        return "Blocked for safety: " + safety["reason"], False
    if safety.get("needs_confirmation"):
        ans = input(f"Safety confirmation needed ({safety['reason']}). Continue? yes/no: ").lower().strip()
        if ans not in ["yes","y","ok","continue","allow"]:
            return "Cancelled. I did not perform that action.", False

    r = route(command)
    intent = r["intent"]
    MEMORY.add_event("command", intent, command)
    VECTOR_MEMORY.add(command, {"kind":"command","intent":intent})

    if intent in ["open_website","open_dynamic"] and r.get("url"):
        return pc_control.open_url(r["url"]), False
    if intent == "open_app":
        return pc_control.open_app(r["clean"].replace("open","")), False
    if intent == "close_tab":
        return pc_control.close_current_tab(), False
    if intent == "close_window":
        return pc_control.close_current_window(), False
    if intent == "search_web":
        return pc_control.search_web(r.get("query","")), False
    if intent == "youtube_search":
        return pc_control.search_youtube(r.get("query","")), False
    if intent == "read_screen":
        return screen_ai.read_screen_text()[:1200], False
    if intent == "click_text":
        return screen_ai.click_text_on_screen(r.get("text","")), False
    if intent == "teach":
        phrase, meaning = r.get("phrase",""), r.get("meaning","")
        if phrase and meaning:
            MEMORY.teach_command(phrase, meaning)
            return f"Learned: when you say '{phrase}', it means '{meaning}'.", False
        return "Teach me like: when I say revision mode it means study mode.", False
    if intent == "plan":
        return plan_steps(command), False
    if intent == "internet_learn":
        clean = r["clean"]
        # Allow explicit trusted URL learning; otherwise save pending request.
        parts = clean.split()
        urls = [p for p in parts if p.startswith("http://") or p.startswith("https://")]
        if urls:
            return research_url(urls[0], r.get("topic","internet research")), False
        return background_research(r.get("topic","AI technology")), False
    if intent == "status":
        last = MEMORY.last_event()
        return f"Blue Ultimate Free JARVIS online. Last memory: {last}. Safety is active. LLM target: llama3.1:8b.", False

    return ask_brain(command), False
