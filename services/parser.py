# services/parser.py

"""
PCB Parser

Supports:
- Image-based parsing (via pipeline)
- JSON-based parsing (future netlist support)
- Safe fallback mode

Output:
{
    "components": [...],
    "metadata": {...},
    "error": None
}
"""

from typing import Dict, Any
from PIL import Image
import os
import json

# Pipeline
from models.pipeline import PCBPipeline


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
    # 📄 JSON PARSING (FUTURE SUPPORT)
    # ----------------------------------------
    if ext in ["json"]:
        return parse_from_json(file_path)

    return _error(f"Unsupported file type: {ext}")


# ----------------------------------------
# 📷 IMAGE PARSER (CORE)
# ----------------------------------------
def parse_from_image(image_path: str) -> Dict[str, Any]:

    try:
        # Validate image
        img = Image.open(image_path)
        img.verify()

    except Exception as e:
        return _error(f"Invalid image: {str(e)}")

    try:
        pipeline = PCBPipeline()

        perception = pipeline.safe_run(image_path)

        return {
            "components": perception.get("components", []),
            "ocr": perception.get("ocr", {}),
            "segmentation": perception.get("segmentation", {}),
            "metadata": perception.get("metadata", {}),
            "errors": perception.get("errors", [])
        }

    except Exception as e:
        return _error(f"Pipeline failed: {str(e)}")


# ----------------------------------------
# 📄 JSON PARSER (NETLIST / FUTURE)
# ----------------------------------------
def parse_from_json(file_path: str) -> Dict[str, Any]:

    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        return {
            "components": data.get("components", []),
            "nets": data.get("nets", []),
            "metadata": {
                "source": "json"
            },
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
            "mode": "quick"
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

    return {
        "valid": len(issues) == 0,
        "issues": issues
    }


# ----------------------------------------
# 🧾 ERROR HANDLER
# ----------------------------------------
def _error(message: str):

    return {
        "components": [],
        "metadata": {},
        "error": message
    }
    
