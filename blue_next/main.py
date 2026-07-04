
from blue_next.voice.stt import STT
from blue_next.voice.tts import TTS
from blue_next.voice.wake import WAKE
from blue_next.core.agent import execute
from blue_next.core.status import set_status

def main():
    set_status("online", "Blue Ultimate Free JARVIS started")
    TTS.speak("Blue Ultimate Free JARVIS is online. Free mode active. Safety is on.")
    while True:
        try:
            WAKE.wait()
            cmd = STT.listen()
            if not cmd:
                continue
            reply, should_stop = execute(cmd)
            TTS.speak(reply)
            if should_stop:
                break
        except KeyboardInterrupt:
            break
        except Exception as e:
            set_status("error", str(e))
            print("Blue error:", e)

if __name__ == "__main__":
    main()
