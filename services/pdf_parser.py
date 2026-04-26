# services/pdf_parser.py

"""
PDF Parser for PCB AI System

✔ Extract text from PDFs
✔ OCR fallback for scanned PDFs
✔ Extract metadata
✔ Extract tables (basic)
✔ Chunk text for RAG / FAISS
✔ Safe + production-ready
"""

import os
from typing import Dict, List

# Text extraction
from PyPDF2 import PdfReader

# Optional OCR
try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except:
    OCR_AVAILABLE = False

# Optional table extraction
try:
    import pdfplumber
    TABLE_AVAILABLE = True
except:
    TABLE_AVAILABLE = False


# ----------------------------------------
# 📄 TEXT EXTRACTION (STANDARD)
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
# 🔍 OCR EXTRACTION (SCANNED PDFs)
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
# 🧠 SMART TEXT EXTRACTION
# ----------------------------------------
def extract_pdf_text(file_path: str) -> str:

    text = extract_text_from_pdf(file_path)

    # If too small → fallback to OCR
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
# 📋 TABLE EXTRACTION (BASIC BOM SUPPORT)
# ----------------------------------------
def extract_tables(file_path: str) -> List:

    if not TABLE_AVAILABLE:
        return []

    tables = []

    try:
        with pdfplumber.open(file_path) as pdf:

            for page in pdf.pages:
                page_tables = page.extract_tables()

                for table in page_tables:
                    tables.append(table)

    except:
        return []

    return tables


# ----------------------------------------
# ✂️ CHUNK TEXT FOR RAG
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
# 🧠 MAIN PARSER
# ----------------------------------------
def parse_pdf(file_path: str) -> Dict:

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    try:
        text = extract_pdf_text(file_path)
        metadata = extract_metadata(file_path)
        tables = extract_tables(file_path)
        chunks = chunk_text(text)

        return {
            "text": text,
            "chunks": chunks,
            "tables": tables,
            "metadata": metadata,
            "num_chunks": len(chunks),
            "num_tables": len(tables),
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
# 📊 SUMMARY FOR UI
# ----------------------------------------
def pdf_summary(parsed_pdf: Dict) -> Dict:

    if "error" in parsed_pdf:
        return {
            "valid": False,
            "error": parsed_pdf["error"]
        }

    return {
        "valid": True,
        "pages": parsed_pdf.get("metadata", {}).get("pages", 0),
        "length": parsed_pdf.get("length", 0),
        "chunks": parsed_pdf.get("num_chunks", 0),
        "tables": parsed_pdf.get("num_tables", 0)
    }
    
