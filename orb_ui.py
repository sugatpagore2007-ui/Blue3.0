
import customtkinter as ctk
import random, json, os, time
from pathlib import Path

ctk.set_appearance_mode("dark")

STATUS_FILES = ["HUD_STATUS_FILE", "blue_status.json"]

def read_status():
    for f in STATUS_FILES:
        try:
            if Path(f).exists():
                with open(f, "r", encoding="utf-8") as fp:
                    return json.load(fp)
        except Exception:
            pass
    return {"status": "online", "detail": "Blue JARVIS ready"}

app = ctk.CTk()
app.geometry("560x560")
app.title("Blue JARVIS HUD")

canvas = ctk.CTkCanvas(app, width=560, height=560, bg="black", highlightthickness=0)
canvas.pack(fill="both", expand=True)

rings = []
for i in range(5):
    rings.append(canvas.create_oval(160-i*12,160-i*12,400+i*12,400+i*12, outline="#00ccff", width=2))

orb = canvas.create_oval(190,190,370,370, fill="#00ccff", outline="#66ffff", width=4)
title = canvas.create_text(280, 70, text="BLUE JARVIS", fill="#66ffff", font=("Consolas", 30, "bold"))
state_text = canvas.create_text(280, 430, text="ONLINE", fill="#00ff99", font=("Consolas", 22, "bold"))
detail_text = canvas.create_text(280, 465, text="10 Interaction Pack Active", fill="#bff7ff", font=("Consolas", 13), width=500)
stats_text = canvas.create_text(280, 505, text="listening • thinking • speaking • safe control", fill="#6ee7ff", font=("Consolas", 11), width=500)

def color_for_status(status):
    status = (status or "").lower()
    if "speak" in status: return "#00ccff"
    if "think" in status or "process" in status: return "#ffaa00"
    if "mute" in status: return "#777777"
    if "error" in status or "blocked" in status: return "#ff4444"
    return "#00ff99"

tick = 0
def animate():
    global tick
    tick += 1
    data = read_status()
    status = str(data.get("status", "online")).upper()
    detail = str(data.get("detail", "Blue ready"))[:90]
    color = color_for_status(status)

    pulse = random.randint(0, 18)
    canvas.coords(orb, 190-pulse, 190-pulse, 370+pulse, 370+pulse)
    canvas.itemconfig(orb, fill=color, outline="#ccffff")
    canvas.itemconfig(state_text, text=status, fill=color)
    canvas.itemconfig(detail_text, text=detail)

    for idx, r in enumerate(rings):
        grow = (tick * (idx+1) * 2) % 45
        canvas.coords(r, 160-grow,160-grow,400+grow,400+grow)
        canvas.itemconfig(r, outline=color)

    app.after(140, animate)

animate()
app.mainloop()
