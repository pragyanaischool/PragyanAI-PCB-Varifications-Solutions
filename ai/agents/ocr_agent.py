# ai/agents/ocr_agent.py

import json
import re
import streamlit as st

from models.ocr_model import extract_text
from ai.llm import invoke_with_memory


# ----------------------------------------
# 🧾 CLEAN TEXT FUNCTION
# ----------------------------------------
def clean_text(text):

    if not text:
        return ""

    text = text.strip()
    text = re.sub(r"\s+", " ", text)

    return text


# ----------------------------------------
# 🔍 EXTRACT COMPONENT LABELS
# ----------------------------------------
def extract_labels(text):

    if not text:
        return []

    pattern = r"\b(U\d+|R\d+|C\d+|L\d+|D\d+|Q\d+)\b"

    return list(set(re.findall(pattern, text)))


# ----------------------------------------
# 🧠 NORMALIZE OCR OUTPUT
# ----------------------------------------
def normalize_ocr_output(ocr_data):

    if not isinstance(ocr_data, dict):
        return {"text": "", "lines": []}

    text = (
        ocr_data.get("full_text")
        or ocr_data.get("text")
        or ""
    )

    lines = ocr_data.get("lines")

    if not lines:
        lines = text.split("\n")

    return {
        "text": text,
        "lines": lines
    }


# ----------------------------------------
# 🧠 MAIN OCR AGENT
# ----------------------------------------
def run_ocr_agent(text_input=None, image_path=None, memory=None, structured=True):

    result = {
        "raw_text": "",
        "cleaned_text": "",
        "components": [],
        "lines": [],
        "metadata": {},
        "confidence": 0.0,
        "error": None
    }

    try:

        # ----------------------------------------
        # 📷 IMAGE OCR
        # ----------------------------------------
        if image_path:

            try:
                ocr_data = extract_text(image_path)
            except Exception as e:
                return {"error": f"OCR failed: {str(e)}"}

            normalized = normalize_ocr_output(ocr_data)

            raw_text = normalized["text"]
            lines = normalized["lines"]

        # ----------------------------------------
        # 📝 TEXT INPUT
        # ----------------------------------------
        else:
            raw_text = text_input or ""
            lines = raw_text.split("\n")

        # ----------------------------------------
        # 🧠 PROCESSING
        # ----------------------------------------
        cleaned = clean_text(raw_text)
        components = extract_labels(cleaned)

        confidence = min(1.0, len(cleaned) / 200)  # simple heuristic

        result.update({
            "raw_text": raw_text,
            "cleaned_text": cleaned,
            "components": components,
            "lines": lines,
            "confidence": round(confidence, 2),
            "metadata": {
                "num_lines": len(lines),
                "num_components_detected": len(components)
            }
        })

        # ----------------------------------------
        # 🧠 OPTIONAL MEMORY ENRICHMENT
        # ----------------------------------------
        if memory:
            memory.update("ocr_raw", raw_text)
            memory.update("ocr_components", components)

    except Exception as e:
        result["error"] = str(e)

    return result


# ----------------------------------------
# ⚡ QUICK OCR MODE
# ----------------------------------------
def quick_ocr(image_path):

    try:
        ocr_data = extract_text(image_path)
        normalized = normalize_ocr_output(ocr_data)

        return clean_text(normalized["text"])

    except Exception as e:
        return f"OCR Error: {str(e)}"


# ----------------------------------------
# 📊 OCR SUMMARY
# ----------------------------------------
def ocr_summary(ocr_output):

    return {
        "text_length": len(ocr_output.get("cleaned_text", "")),
        "components_found": ocr_output.get("components", []),
        "num_lines": ocr_output.get("metadata", {}).get("num_lines", 0),
        "confidence": ocr_output.get("confidence", 0)
    }


# ----------------------------------------
# 🔍 VALIDATE OCR QUALITY
# ----------------------------------------
def validate_ocr(ocr_output):

    text = ocr_output.get("cleaned_text", "")

    if not text:
        return {"valid": False, "reason": "No text detected"}

    if len(text) < 5:
        return {"valid": False, "reason": "Too little text"}

    if ocr_output.get("confidence", 0) < 0.2:
        return {"valid": False, "reason": "Low OCR confidence"}

    return {"valid": True, "reason": "OCR looks good"}


# ----------------------------------------
# 🔄 CACHE WRAPPER
# ----------------------------------------
@st.cache_data(show_spinner=False)
def cached_ocr_agent(image_path):

    return run_ocr_agent(image_path=image_path)


# ----------------------------------------
# 🧠 LLM ENRICHMENT (ADVANCED)
# ----------------------------------------
def enrich_ocr_with_llm(memory):

    prompt = """
    Analyze OCR extracted PCB labels.

    Identify:
    - Missing components
    - Label inconsistencies
    - Suspicious naming
    """

    return invoke_with_memory(
        memory,
        "PCB OCR Analyst",
        prompt
    )


# ----------------------------------------
# 🔧 FILTER NOISE LABELS
# ----------------------------------------
def filter_noise_components(components):

    return [c for c in components if len(c) <= 5]
    
