
import os, time
import pyautogui
from blue_next.config.settings import DATA_DIR

def take_screenshot():
    path = DATA_DIR / "latest_screen.png"
    img = pyautogui.screenshot()
    img.save(path)
    return path

def read_screen_text():
    path = take_screenshot()
    try:
        import pytesseract
        from PIL import Image
        text = pytesseract.image_to_string(Image.open(path))
        return text.strip() or "I could not read text from the screen."
    except Exception as e:
        return f"OCR unavailable. Install Tesseract OCR. Error: {e}"

def click_text_on_screen(target: str):
    target = (target or "").strip().lower()
    if not target:
        return "Tell me what visible text/button to click."
    path = take_screenshot()
    try:
        import pytesseract
        from PIL import Image
        data = pytesseract.image_to_data(Image.open(path), output_type=pytesseract.Output.DICT)
        for i, word in enumerate(data.get("text", [])):
            if target in (word or "").lower():
                x = data["left"][i] + data["width"][i]//2
                y = data["top"][i] + data["height"][i]//2
                pyautogui.click(x,y)
                return f"Clicked visible text: {word}"
        return f"I could not find '{target}' on screen."
    except Exception as e:
        return f"Click-by-text needs Tesseract OCR. Error: {e}"

def yolo_status():
    try:
        import cv2
        return "OpenCV ready. YOLO can be added by placing weights/models in blue_next/data/models."
    except Exception as e:
        return f"OpenCV unavailable: {e}"

def omniparser_status():
    return "OmniParser adapter placeholder ready. It is heavy, so Blue loads it only when you install its model files."
