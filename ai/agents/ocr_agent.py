import json
import re
import streamlit as st

from models.ocr_model import extract_text


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
# 🧠 MAIN OCR AGENT
# ----------------------------------------
def run_ocr_agent(text_input=None, image_path=None, structured=True):

    result = {
        "raw_text": "",
        "cleaned_text": "",
        "components": [],
        "lines": [],
        "metadata": {},
        "error": None
    }

    try:
        # ----------------------------------------
        # 📷 IMAGE-BASED OCR
        # ----------------------------------------
        if image_path:
            ocr_data = extract_text(image_path)

            raw_text = ocr_data.get("full_text", "") or ocr_data.get("text", "")
            lines = ocr_data.get("lines", [])

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

        result.update({
            "raw_text": raw_text,
            "cleaned_text": cleaned,
            "components": components,
            "lines": lines,
            "metadata": {
                "num_lines": len(lines),
                "num_components_detected": len(components)
            }
        })

    except Exception as e:
        result["error"] = str(e)

    return result


# ----------------------------------------
# ⚡ QUICK OCR MODE
# ----------------------------------------
def quick_ocr(image_path):

    try:
        ocr_data = extract_text(image_path)
        text = ocr_data.get("full_text", "")

        return clean_text(text)

    except Exception as e:
        return f"OCR Error: {str(e)}"


# ----------------------------------------
# 📊 OCR SUMMARY
# ----------------------------------------
def ocr_summary(ocr_output):

    return {
        "text_length": len(ocr_output.get("cleaned_text", "")),
        "components_found": ocr_output.get("components", []),
        "num_lines": ocr_output.get("metadata", {}).get("num_lines", 0)
    }


# ----------------------------------------
# 🔍 VALIDATE OCR QUALITY
# ----------------------------------------
def validate_ocr(ocr_output):

    text = ocr_output.get("cleaned_text", "")

    if not text:
        return {
            "valid": False,
            "reason": "No text detected"
        }

    if len(text) < 5:
        return {
            "valid": False,
            "reason": "Too little text"
        }

    return {
        "valid": True,
        "reason": "OCR looks good"
    }


# ----------------------------------------
# 🔄 CACHE WRAPPER
# ----------------------------------------
@st.cache_data(show_spinner=False)
def cached_ocr_agent(image_path):

    return run_ocr_agent(image_path=image_path)


# ----------------------------------------
# 🧠 POST-PROCESSING (OPTIONAL)
# ----------------------------------------
def enrich_ocr_with_llm(memory):

    from ai.llm import invoke_with_memory

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
    
