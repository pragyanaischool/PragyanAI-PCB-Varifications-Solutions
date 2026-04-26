# services/parser.py

"""
PCB Parser (Enhanced)

Supports:
✔ Image-based parsing (pipeline)
✔ JSON parsing (netlist / structured input)
✔ Safe fallback (never crashes)
✔ Debug + validation
✔ File metadata support

Output:
{
    "components": [...],
    "ocr": {...},
    "segmentation": {...},
    "metadata": {...},
    "errors": [],
    "error": None
}
"""

from typing import Dict, Any
from PIL import Image
import os
import json
import traceback

# Pipeline
from models.pipeline import PCBPipeline

# Utils (optional but useful)
from utils.file import get_file_info, file_hash_from_path


# ----------------------------------------
# 🧠 MAIN PARSER
# ----------------------------------------
def parse_pcb(file_path: str) -> Dict[str, Any]:

    if not file_path or not os.path.exists(file_path):
        return _error("File not found")

    ext = file_path.split(".")[-1].lower()

    # ----------------------------------------
    # 📷 IMAGE PARSING
    # ----------------------------------------
    if ext in ["png", "jpg", "jpeg", "bmp"]:
        return parse_from_image(file_path)

    # ----------------------------------------
    # 📄 JSON PARSING
    # ----------------------------------------
    if ext in ["json"]:
        return parse_from_json(file_path)

    return _error(f"Unsupported file type: {ext}")


# ----------------------------------------
# 📷 IMAGE PARSER (ROBUST)
# ----------------------------------------
def parse_from_image(image_path: str) -> Dict[str, Any]:

    # ----------------------------------------
    # 🔍 VALIDATE IMAGE
    # ----------------------------------------
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")  # ensure consistent format
        width, height = img.size

    except Exception as e:
        return _error(f"Invalid image: {str(e)}")

    # ----------------------------------------
    # 🧠 PIPELINE EXECUTION
    # ----------------------------------------
    try:
        pipeline = PCBPipeline()

        perception = pipeline.safe_run(image_path)

        # ----------------------------------------
        # 🧾 FILE INFO
        # ----------------------------------------
        file_info = get_file_info(image_path)
        file_hash = file_hash_from_path(image_path)

        return {
            "components": perception.get("components", []),
            "ocr": perception.get("ocr", {}),
            "segmentation": perception.get("segmentation", {}),
            "metadata": {
                **perception.get("metadata", {}),
                "image_size": {
                    "width": width,
                    "height": height
                },
                "file_info": file_info,
                "file_hash": file_hash
            },
            "errors": perception.get("errors", []),
            "error": None
        }

    except Exception as e:
        return _error(f"Pipeline failed: {str(e)}")


# ----------------------------------------
# 📄 JSON PARSER (NETLIST / STRUCTURED)
# ----------------------------------------
def parse_from_json(file_path: str) -> Dict[str, Any]:

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)

        return {
            "components": data.get("components", []),
            "nets": data.get("nets", []),
            "metadata": {
                "source": "json",
                "file": os.path.basename(file_path)
            },
            "errors": [],
            "error": None
        }

    except Exception as e:
        return _error(f"JSON parsing failed: {str(e)}")


# ----------------------------------------
# ⚡ QUICK PARSER (FAST MODE)
# ----------------------------------------
def quick_parse(image_path: str):

    try:
        pipeline = PCBPipeline()

        result = pipeline.quick_run(image_path)

        return {
            "ocr": result.get("ocr", {}),
            "mode": "quick",
            "error": None
        }

    except Exception as e:
        return _error(str(e))


# ----------------------------------------
# 🔍 VALIDATION
# ----------------------------------------
def validate_parsed_data(parsed):

    issues = []

    if not parsed.get("components"):
        issues.append("No components detected")

    if parsed.get("errors"):
        issues.extend(parsed["errors"])

    if parsed.get("error"):
        issues.append(parsed["error"])

    return {
        "valid": len(issues) == 0,
        "issues": issues
    }


# ----------------------------------------
# 📊 SUMMARY (NEW)
# ----------------------------------------
def parser_summary(parsed):

    return {
        "num_components": len(parsed.get("components", [])),
        "has_ocr": bool(parsed.get("ocr")),
        "has_segmentation": bool(parsed.get("segmentation")),
        "has_errors": bool(parsed.get("errors")),
        "valid": parsed.get("error") is None
    }


# ----------------------------------------
# 🧾 ERROR HANDLER
# ----------------------------------------
def _error(message: str):

    return {
        "components": [],
        "ocr": {},
        "segmentation": {},
        "metadata": {},
        "errors": [],
        "error": message
    }
    
