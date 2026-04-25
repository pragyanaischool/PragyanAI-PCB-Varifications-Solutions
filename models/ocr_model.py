"""
OCR Model for PCB Text Extraction

Features:
- Image preprocessing (grayscale, thresholding)
- OCR extraction using pytesseract
- PCB component label extraction (U1, R2, C3, etc.)
- Structured output
"""

from PIL import Image, ImageOps
import pytesseract
import re
from typing import Dict, List


# ----------------------------------------
# 🧠 MAIN OCR FUNCTION
# ----------------------------------------
def extract_text(image_path: str) -> Dict:

    result = {
        "text": "",
        "lines": [],
        "components": [],
        "confidence": 0.0,
        "error": None
    }

    try:
        # ----------------------------------------
        # 🖼️ LOAD IMAGE
        # ----------------------------------------
        img = Image.open(image_path)

        # ----------------------------------------
        # 🎯 PREPROCESSING
        # ----------------------------------------
        gray = ImageOps.grayscale(img)

        # Improve contrast (simple thresholding)
        binary = gray.point(lambda x: 0 if x < 150 else 255, '1')

        # ----------------------------------------
        # 🔤 OCR
        # ----------------------------------------
        text = pytesseract.image_to_string(binary)

        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # ----------------------------------------
        # 🔍 COMPONENT EXTRACTION
        # ----------------------------------------
        components = extract_components(text)

        # ----------------------------------------
        # 📊 CONFIDENCE (simple heuristic)
        # ----------------------------------------
        confidence = min(1.0, len(components) / 10 + 0.3)

        # ----------------------------------------
        # 📦 OUTPUT
        # ----------------------------------------
        result.update({
            "text": text,
            "lines": lines,
            "components": components,
            "confidence": round(confidence, 2)
        })

    except Exception as e:
        result["error"] = str(e)

    return result


# ----------------------------------------
# 🔍 COMPONENT EXTRACTION (PCB-AWARE)
# ----------------------------------------
def extract_components(text: str) -> List[str]:

    # Common PCB labels
    pattern = r"\b(U\d+|R\d+|C\d+|L\d+|D\d+|Q\d+|IC\d+|J\d+|X\d+)\b"

    matches = re.findall(pattern, text)

    return list(set(matches))


# ----------------------------------------
# ⚡ QUICK OCR (FAST MODE)
# ----------------------------------------
def quick_ocr(image_path: str) -> Dict:

    try:
        img = Image.open(image_path).convert("L")

        text = pytesseract.image_to_string(img)

        return {
            "text": text,
            "components": extract_components(text),
            "mode": "quick"
        }

    except Exception as e:
        return {
            "error": str(e),
            "mode": "quick"
        }


# ----------------------------------------
# 🔄 SAFE OCR (NO CRASH GUARANTEE)
# ----------------------------------------
def safe_ocr(image_path: str) -> Dict:

    try:
        return extract_text(image_path)
    except Exception as e:
        return {
            "text": "",
            "components": [],
            "error": f"OCR failed: {str(e)}"
        }


# ----------------------------------------
# 🧠 OCR POST-PROCESSING
# ----------------------------------------
def clean_text(text: str) -> str:

    # Remove special chars
    text = re.sub(r"[^\w\s]", " ", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ----------------------------------------
# 🔍 EXTRACT NETS / SIGNAL NAMES
# ----------------------------------------
def extract_nets(text: str) -> List[str]:

    pattern = r"\b(VCC|GND|CLK|DATA|RESET|TX|RX)\b"

    return list(set(re.findall(pattern, text)))


# ----------------------------------------
# 🧪 TEST FUNCTION
# ----------------------------------------
if __name__ == "__main__":

    sample = "sample_pcb.png"

    result = extract_text(sample)

    print("OCR RESULT:")
    print(result)
