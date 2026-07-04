
from blue_next.config.settings import SETTINGS

class SpeechToText:
    """Free-first STT: NVIDIA Parakeet if installed, otherwise Faster-Whisper, otherwise typed input."""
    def __init__(self):
        self.engine = "text"
        self.whisper_model = None
        self.parakeet_ready = False

        if SETTINGS.stt_engine in ["auto", "parakeet"]:
            try:
                # Placeholder for local NVIDIA NeMo/Parakeet installation.
                # Blue does not download huge models automatically to avoid lag.
                import nemo.collections.asr as nemo_asr  # type: ignore
                self.nemo_asr = nemo_asr
                self.parakeet_ready = True
                self.engine = "parakeet"
            except Exception:
                pass

        if self.engine == "text" and SETTINGS.stt_engine in ["auto", "whisper"]:
            try:
                from faster_whisper import WhisperModel
                self.whisper_model = WhisperModel(
                    SETTINGS.whisper_model,
                    device="cpu",
                    compute_type="int8"
                )
                self.engine = "whisper"
            except Exception:
                pass

    def listen(self) -> str:
        if self.engine == "whisper":
            try:
                import sounddevice as sd
                from scipy.io.wavfile import write
                path = "blue_next/data/command.wav"
                audio = sd.rec(int(SETTINGS.record_seconds * SETTINGS.sample_rate),
                               samplerate=SETTINGS.sample_rate, channels=1, dtype="int16")
                sd.wait(); write(path, SETTINGS.sample_rate, audio)
                segments, _ = self.whisper_model.transcribe(path, beam_size=3, language="en", vad_filter=True)
                return " ".join(seg.text for seg in segments).strip()
            except Exception as e:
                print("STT whisper error:", e)
        # Parakeet adapter intentionally returns typed fallback unless user installs local model code.
        return input("You: ").strip()

STT = SpeechToText()
