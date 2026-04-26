# services/parser.py

"""
PCB Parser Service (FINAL SAFE VERSION)

✔ No OpenCV (Streamlit-safe)
✔ Pipeline + OCR fallback
✔ Netlist support
✔ Debug-friendly
✔ Never crashes
"""

import os
import re
import json
from typing import Dict, Any, List

# Safe imports
try:
    from PIL import Image
except Exception:
    Image = None

try:
    import pytesseract
except Exception:
    pytesseract = None

# Optional pipeline (safe import)
try:
    from models.pipeline import PCBPipeline
except Exception:
    PCBPipeline = None

# Safe utils import (IMPORTANT)
try:
    from utils.file import get_file_info, file_hash_from_path
except Exception:
    def get_file_info(path): return {}
    def file_hash_from_path(path): return ""


# ----------------------------------------
# 🧠 MAIN ENTRY
# ----------------------------------------
def parse_pcb(file_path: str) -> Dict[str, Any]:

    if not file_path:
        return _error("Empty file path")

    if not os.path.exists(file_path):
        return _error(f"File does not exist: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
        return parse_from_image(file_path)

    elif ext in [".json"]:
        return parse_from_json(file_path)

    elif ext in [".txt", ".net", ".netlist"]:
        return parse_netlist(file_path)

    return _error(f"Unsupported file format: {ext}")


# ----------------------------------------
# 🖼️ IMAGE PARSER (PIPELINE + FALLBACK)
# ----------------------------------------
def parse_from_image(image_path: str) -> Dict[str, Any]:

    debug = {}

    # ----------------------------------------
    # 🧾 FILE CHECK
    # ----------------------------------------
    if not os.path.exists(image_path):
        return _error(f"File not found: {image_path}")

    debug["file_size"] = os.path.getsize(image_path)

    if debug["file_size"] == 0:
        return _error("File is empty")

    # ----------------------------------------
    # 🖼️ LOAD IMAGE (PIL ONLY)
    # ----------------------------------------
    try:
        img = Image.open(image_path).convert("RGB")
        width, height = img.size

        debug["image_size"] = img.size

    except Exception as e:
        return _error(f"Image load failed: {str(e)}")

    # ----------------------------------------
    # 🤖 TRY PIPELINE FIRST
    # ----------------------------------------
    if PCBPipeline:

        try:
            pipeline = PCBPipeline()
            perception = pipeline.safe_run(image_path)

            return {
                "components": perception.get("components", []),
                "ocr": perception.get("ocr", {}),
                "segmentation": perception.get("segmentation", {}),
                "metadata": {
                    **perception.get("metadata", {}),
                    "image_size": {"width": width, "height": height},
                    "file_info": get_file_info(image_path),
                    "file_hash": file_hash_from_path(image_path),
                },
                "errors": perception.get("errors", []),
                "debug": debug,
                "error": None
            }

        except Exception as e:
            debug["pipeline_error"] = str(e)

    # ----------------------------------------
    # 🔤 FALLBACK OCR MODE
    # ----------------------------------------
    text = ""
    if pytesseract:
        try:
            gray = img.convert("L")
            text = pytesseract.image_to_string(gray)
            debug["ocr_length"] = len(text)
        except Exception as e:
            debug["ocr_error"] = str(e)
    else:
        debug["ocr"] = "pytesseract not installed"

    components = extract_components_from_text(text)
    nets = build_dummy_nets(components)

    return {
        "components": components,
        "nets": nets,
        "ocr": {"text": text},
        "segmentation": {},
        "metadata": {
            "image_size": {"width": width, "height": height}
        },
        "debug": debug,
        "error": None
    }


# ----------------------------------------
# 📄 JSON PARSER
# ----------------------------------------
def parse_from_json(file_path: str) -> Dict[str, Any]:

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)

        return {
            "components": data.get("components", []),
            "nets": data.get("nets", []),
            "metadata": {"source": "json"},
            "error": None
        }

    except Exception as e:
        return _error(f"JSON parsing failed: {str(e)}")


# ----------------------------------------
# 📜 NETLIST PARSER
# ----------------------------------------
def parse_netlist(file_path: str) -> Dict[str, Any]:

    components = set()
    nets = []

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

    except Exception as e:
        return _error(f"Netlist read failed: {str(e)}")

    for line in lines:
        tokens = re.findall(r"\b[A-Z]+\d+\b", line)

        if len(tokens) >= 2:
            components.update(tokens)
            nets.append((tokens[0], tokens[1]))

    return {
        "components": list(components),
        "nets": nets,
        "metadata": {"source": "netlist"},
        "error": None
    }


# ----------------------------------------
# 🔍 COMPONENT EXTRACTION
# ----------------------------------------
def extract_components_from_text(text: str) -> List[str]:

    pattern = r"\b(U\d+|R\d+|C\d+|L\d+|D\d+|Q\d+)\b"
    return list(set(re.findall(pattern, text)))


# ----------------------------------------
# 🔗 DUMMY NET BUILDER
# ----------------------------------------
def build_dummy_nets(components: List[str]):

    nets = []

    for i in range(len(components) - 1):
        nets.append((components[i], components[i + 1]))

    return nets


# ----------------------------------------
# ❌ ERROR HANDLER
# ----------------------------------------
def _error(message: str):

    return {
        "components": [],
        "nets": [],
        "metadata": {},
        "error": message
    }
    
