
from dataclasses import dataclass, field
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "blue_next" / "data"
LOG_DIR = ROOT_DIR / "blue_next" / "logs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class BlueSettings:
    # FREE-FIRST: paid/cloud systems are optional and disabled by default.
    use_paid_services: bool = False
    llm_primary: str = "llama3.1:8b"
    llm_fast: str = "mistral"
    ollama_url: str = "http://localhost:11434/api/generate"

    # Speech to text priority: parakeet -> faster_whisper -> text fallback.
    stt_engine: str = "auto"  # auto, parakeet, whisper, text
    whisper_model: str = "medium"  # use tiny/base if PC lags
    sample_rate: int = 16000
    record_seconds: int = 3

    # Deepgram is optional only; disabled unless user adds key and flips use_paid_services.
    deepgram_enabled: bool = False

    # TTS priority: edge -> xtts -> pyttsx3 -> print fallback.
    tts_engine: str = "auto"
    edge_voice: str = "en-US-GuyNeural"
    edge_rate: str = "-10%"
    edge_pitch: str = "-20Hz"

    # Wake word priority: openwakeword -> porcupine -> keyboard/text fallback.
    wake_word: str = "blue"
    wake_engine: str = "auto"
    always_listen: bool = True

    # Safety and performance
    full_pc_control: bool = True
    safety_mode: bool = True
    confirm_risky_actions: bool = True
    max_background_workers: int = 2
    low_lag_mode: bool = True

    # Memory and learning
    chroma_enabled: bool = True
    faiss_enabled: bool = True
    internet_learning_enabled: bool = False  # user can turn on with command, never blindly
    trusted_domains: list[str] = field(default_factory=lambda: [
        "wikipedia.org", "docs.python.org", "learn.microsoft.com", "github.com",
        "pypi.org", "ollama.com", "opencv.org"
    ])

SETTINGS = BlueSettings()
