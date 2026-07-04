
from blue_next.config.settings import SETTINGS

class WakeWord:
    """Free-first wake: OpenWakeWord if installed, Porcupine optional, otherwise always-listen/text fallback."""
    def __init__(self):
        self.engine = "always" if SETTINGS.always_listen else "text"
        try:
            import openwakeword  # type: ignore
            self.engine = "openwakeword-ready"
        except Exception:
            pass

    def wait(self):
        # Low-lag starter: always listening is handled by command loop.
        return True

WAKE = WakeWord()
