
import asyncio, os, uuid
from blue_next.config.settings import SETTINGS
from blue_next.core.status import set_status

class TextToSpeech:
    """Free-first TTS: Edge TTS -> XTTS-v2 placeholder -> pyttsx3 -> print."""
    def __init__(self):
        self.edge_ready = False
        self.pyttsx3_engine = None
        try:
            import edge_tts, playsound
            self.edge_tts = edge_tts
            self.playsound = playsound.playsound
            self.edge_ready = True
        except Exception:
            pass
        try:
            import pyttsx3
            self.pyttsx3_engine = pyttsx3.init()
            self.pyttsx3_engine.setProperty("rate", 175)
        except Exception:
            pass

    async def _edge_speak(self, text):
        fname = f"blue_next/data/voice_{uuid.uuid4().hex}.mp3"
        communicate = self.edge_tts.Communicate(
            text, voice=SETTINGS.edge_voice, rate=SETTINGS.edge_rate, pitch=SETTINGS.edge_pitch
        )
        await communicate.save(fname)
        self.playsound(fname)
        try: os.remove(fname)
        except Exception: pass

    def speak(self, text: str):
        text = str(text).strip()
        if not text: return
        print("Blue:", text)
        set_status("speaking", text[:120])
        if self.edge_ready:
            try:
                asyncio.run(self._edge_speak(text))
                set_status("online", "Ready")
                return
            except Exception:
                pass
        if self.pyttsx3_engine:
            try:
                self.pyttsx3_engine.say(text)
                self.pyttsx3_engine.runAndWait()
            except Exception:
                pass
        set_status("online", "Ready")

TTS = TextToSpeech()
