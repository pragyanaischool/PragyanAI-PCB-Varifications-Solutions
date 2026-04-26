# services/pdf_parser.py

"""
PDF Parser for PCB AI System

✔ Extracts text from PDFs
✔ Supports OCR fallback (scanned PDFs)
✔ Extracts metadata
✔ Splits into chunks for RAG
✔ Handles errors safely
"""

import os
from typing import Dict, List

# Text extraction
from PyPDF2 import PdfReader

# OCR fallback
try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except:
    OCR_AVAILABLE = False


# ----------------------------------------
# 📄 BASIC TEXT EXTRACTION
# ----------------------------------------
def extract_text_from_pdf(file_path: str) -> str:

    text = ""

    try:
        reader = PdfReader(file_path)

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    except Exception as e:
        return f"[ERROR] {str(e)}"

    return text


# ----------------------------------------
# 🔍 OCR FALLBACK (SCANNED PDF)
# ----------------------------------------
def extract_text_with_ocr(file_path: str) -> str:

    if not OCR_AVAILABLE:
        return "[OCR NOT AVAILABLE] Install pytesseract + pdf2image"

    text = ""

    try:
        images = convert_from_path(file_path)

        for img in images:
            text += pytesseract.image_to_string(img) + "\n"

    except Exception as e:
        return f"[OCR ERROR] {str(e)}"

    return text


# ----------------------------------------
# 🧠 SMART EXTRACTION (AUTO SWITCH)
# ----------------------------------------
def extract_pdf_text(file_path: str) -> str:

    text = extract_text_from_pdf(file_path)

    # If text too small → likely scanned PDF
    if len(text.strip()) < 50:
        ocr_text = extract_text_with_ocr(file_path)

        if "[OCR ERROR]" not in ocr_text:
            return ocr_text

    return text


# ----------------------------------------
# 📊 METADATA EXTRACTION
# ----------------------------------------
def extract_metadata(file_path: str) -> Dict:

    try:
        reader = PdfReader(file_path)

        meta = reader.metadata

        return {
            "title": meta.get("/Title", ""),
            "author": meta.get("/Author", ""),
            "pages": len(reader.pages)
        }

    except:
        return {
            "title": "",
            "author": "",
            "pages": 0
        }


# ----------------------------------------
# ✂️ CHUNK TEXT (FOR RAG)
# ----------------------------------------
def chunk_text(text: str, chunk_size=500, overlap=50) -> List[str]:

    chunks = []

    start = 0
    length = len(text)

    while start < length:
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# ----------------------------------------
# 🧠 MAIN PARSER FUNCTION
# ----------------------------------------
def parse_pdf(file_path: str) -> Dict:

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    try:
        text = extract_pdf_text(file_path)

        metadata = extract_metadata(file_path)

        chunks = chunk_text(text)

        return {
            "text": text,
            "chunks": chunks,
            "metadata": metadata,
            "num_chunks": len(chunks),
            "length": len(text)
        }

    except Exception as e:
        return {"error": str(e)}


# ----------------------------------------
# ⚡ QUICK PARSE (FAST MODE)
# ----------------------------------------
def quick_parse_pdf(file_path: str) -> Dict:

    try:
        text = extract_text_from_pdf(file_path)

        return {
            "text_preview": text[:1000],
            "length": len(text)
        }

    except Exception as e:
        return {"error": str(e)}


# ----------------------------------------
# 📊 SUMMARY (FOR UI)
# ----------------------------------------
def pdf_summary(parsed_pdf: Dict) -> Dict:

    if "error" in parsed_pdf:
        return {"valid": False}

    return {
        "valid": True,
        "pages": parsed_pdf.get("metadata", {}).get("pages", 0),
        "length": parsed_pdf.get("length", 0),
        "chunks": parsed_pdf.get("num_chunks", 0)
    }
