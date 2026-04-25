# utils/file.py

import os
import tempfile
import hashlib
from typing import Union, Tuple, Optional


# ----------------------------------------
# 📤 SAVE UPLOADED FILE (STREAMLIT SAFE)
# ----------------------------------------
def save_uploaded_file(uploaded_file) -> Optional[str]:
    """
    Save a Streamlit UploadedFile to a temp file and return its path.
    """

    if uploaded_file is None:
        return None

    try:
        suffix = _infer_suffix(uploaded_file.name)

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            data = uploaded_file.read()

            if not data:
                raise ValueError("Uploaded file is empty")

            tmp.write(data)

            # 🔥 CRITICAL FIX (prevents OpenCV/PIL issues)
            tmp.flush()
            tmp.seek(0)

            return tmp.name

    except Exception as e:
        print(f"[FILE ERROR] save_uploaded_file: {e}")
        return None


# ----------------------------------------
# 📦 SAVE BYTES TO FILE
# ----------------------------------------
def save_bytes_to_file(data: bytes, suffix: str = ".bin") -> Optional[str]:

    try:
        if not data:
            raise ValueError("Empty byte data")

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data)
            tmp.flush()
            tmp.seek(0)

            return tmp.name

    except Exception as e:
        print(f"[FILE ERROR] save_bytes_to_file: {e}")
        return None


# ----------------------------------------
# 📥 READ FILE AS BYTES
# ----------------------------------------
def read_file_bytes(path: str) -> bytes:

    if not path or not os.path.exists(path):
        return b""

    with open(path, "rb") as f:
        return f.read()


# ----------------------------------------
# 🧾 READ FILE AS TEXT
# ----------------------------------------
def read_file_text(path: str, encoding: str = "utf-8") -> str:

    if not path or not os.path.exists(path):
        return ""

    with open(path, "r", encoding=encoding, errors="ignore") as f:
        return f.read()


# ----------------------------------------
# 🗑️ SAFE DELETE FILE
# ----------------------------------------
def safe_delete(path: Optional[str]) -> bool:

    try:
        if path and os.path.exists(path):
            os.remove(path)
            return True

    except Exception as e:
        print(f"[FILE ERROR] safe_delete: {e}")

    return False


# ----------------------------------------
# 🧹 CLEANUP MULTIPLE FILES
# ----------------------------------------
def cleanup_files(paths):

    results = []

    for p in paths:
        results.append(safe_delete(p))

    return all(results)


# ----------------------------------------
# 🔐 FILE HASH (FOR CACHING / DEDUP)
# ----------------------------------------
def file_hash_from_bytes(data: bytes) -> str:

    if not data:
        return ""

    return hashlib.sha256(data).hexdigest()


def file_hash_from_path(path: str) -> str:

    if not path or not os.path.exists(path):
        return ""

    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)

    return h.hexdigest()


# ----------------------------------------
# 🏷️ FILE INFO
# ----------------------------------------
def get_file_info(path: str) -> dict:

    if not path or not os.path.exists(path):
        return {"exists": False}

    return {
        "exists": True,
        "size_bytes": os.path.getsize(path),
        "filename": os.path.basename(path),
        "extension": os.path.splitext(path)[1],
    }


# ----------------------------------------
# 🔎 VALIDATE FILE TYPE
# ----------------------------------------
def validate_file_type(path: str, allowed_types=None) -> Tuple[bool, str]:

    if not path or not os.path.exists(path):
        return False, "File does not exist"

    if allowed_types:
        ext = os.path.splitext(path)[1].lower().replace(".", "")

        if ext not in allowed_types:
            return False, f"Unsupported file type: {ext}"

    return True, "Valid file"


# ----------------------------------------
# 🔎 HELPER: INFER SUFFIX
# ----------------------------------------
def _infer_suffix(filename: str) -> str:

    ext = os.path.splitext(filename)[1]
    return ext if ext else ".tmp"


# ----------------------------------------
# 🧠 FRONT/BACK PAIR SAVE
# ----------------------------------------
def save_front_back(front_file, back_file) -> Tuple[Optional[str], Optional[str]]:

    front_path = save_uploaded_file(front_file)
    back_path = save_uploaded_file(back_file)

    return front_path, back_path


# ----------------------------------------
# ⚡ TEMP DIRECTORY CLEANUP (OPTIONAL)
# ----------------------------------------
def cleanup_temp_dir():

    try:
        temp_dir = tempfile.gettempdir()

        for file in os.listdir(temp_dir):
            path = os.path.join(temp_dir, file)

            if os.path.isfile(path):
                try:
                    os.remove(path)
                except:
                    pass

        return True

    except Exception as e:
        print(f"[CLEANUP ERROR] {e}")
        return False
        
