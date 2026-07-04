# Blue Ultimate Free JARVIS Upgrade

This package preserves your old Blue files and adds a new modular free-first JARVIS system in `blue_next/`.

## What was added

### 1. Speech to text
- Free-first: NVIDIA Parakeet adapter placeholder if NeMo is installed.
- Fallback: Faster Whisper.
- Deepgram is not used because you asked not to use paid things. It can be added later only as optional.

### 2. Voice output
- Edge TTS first.
- XTTS-v2 adapter placeholder for later local/offline custom voice.
- pyttsx3 fallback.

### 3. AI brain
- Ollama local brain.
- Primary LLM: `llama3.1:8b`.
- Fast local option: `mistral`.
- GPT-4o is not enabled because you asked no paid things. Optional adapter is disabled.

### 4. Wake word
- OpenWakeWord ready.
- Porcupine is not enabled by default because it usually needs an access key.
- Always-listen fallback included.

### 5. Vision
- OCR screen reading.
- OpenCV ready.
- YOLO and OmniParser placeholders are included as lazy/heavy modules.

### 6. Memory
- SQLite memory.
- ChromaDB vector memory.
- FAISS listed for advanced local search.

### 7. UI
- Current CustomTkinter HUD preserved.
- PyQt6/Electron are marked as later advanced UI options. Electron needs Node.js.

### 8. LLM
- Uses `llama3.1:8b` through Ollama.

### 9. Neural networking + ML
- Command learning system.
- Natural command correction.
- ML-ready memory logs.
- Vector memory for semantic recall.

### 10. Internet learning
Safe internet learning is included but does not blindly learn from random sites.
It stores trusted-source summaries only when you provide/approve a URL.

Example:
```text
learn from internet https://docs.python.org/3/tutorial/ topic python
```

## Install

```bash
pip install -r requirements_ultimate_free.txt
```

For local LLM:
```bash
ollama run llama3.1:8b
ollama run mistral
```

For OCR:
Install Tesseract OCR separately and make sure it is in PATH.

## Run

```bash
python run_ultimate_blue.py
```

Or Windows:
```bat
START_BLUE_ULTIMATE_FREE.bat
```

## Test commands

```text
jarvis status
open youtube
search for python tutorial
search youtube for AI news
read screen
click login
when i say revision mode it means study mode
learn from internet https://docs.python.org/3/tutorial/ topic python
plan my IBPS study task
stop blue
```

## Important note

Deepgram and GPT-4o are paid/cloud systems, so this build does not depend on them.  
Porcupine may require a key, so OpenWakeWord is the free default.


## Recursion Fix Note
If you see `maximum recursion depth exceeded`, use this fixed build. The old natural-command wrapper called itself through `correct_command_text`; that has been repaired. Prefer running `python run_ultimate_blue.py` or `START_BLUE_ULTIMATE_FREE.bat`.
