# ai/vector_store.py

"""
Vector Store (FAISS) for PCB RAG System (ENHANCED)

✔ Cached embeddings (fast)
✔ In-memory + disk persistence
✔ Metadata support
✔ Incremental updates
✔ Streamlit-friendly
✔ Stable for multi-turn chat
"""

import os
from typing import List, Optional, Dict

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ----------------------------------------
# ⚙️ CONFIG
# ----------------------------------------
VECTOR_DB_PATH = "data/vector_store"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ----------------------------------------
# 🧠 GLOBAL CACHE (IMPORTANT)
# ----------------------------------------
_embedding_model = None
_vector_db = None


# ----------------------------------------
# 🧠 LOAD EMBEDDINGS (CACHED)
# ----------------------------------------
def get_embeddings():
    global _embedding_model

    if _embedding_model is None:
        print("[VECTOR] Loading embedding model...")
        _embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )

    return _embedding_model


# ----------------------------------------
# ✂️ CHUNK TEXT
# ----------------------------------------
def split_text(text: str, metadata: Optional[Dict] = None,
               chunk_size=500, overlap=50):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )

    docs = splitter.create_documents([text])

    # Attach metadata (VERY IMPORTANT)
    if metadata:
        for d in docs:
            d.metadata.update(metadata)

    return docs


# ----------------------------------------
# 🚀 BUILD VECTOR STORE (FRESH)
# ----------------------------------------
def build_vector_store(text: str, metadata: Optional[Dict] = None):

    global _vector_db

    if not text or not text.strip():
        print("[VECTOR] Empty text, skipping build")
        return None

    docs = split_text(text, metadata)

    embeddings = get_embeddings()

    _vector_db = FAISS.from_documents(docs, embeddings)

    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    _vector_db.save_local(VECTOR_DB_PATH)

    print(f"[VECTOR] Built DB with {len(docs)} chunks")

    return _vector_db


# ----------------------------------------
# ➕ ADD DOCUMENTS (INCREMENTAL)
# ----------------------------------------
def add_to_vector_store(text: str, metadata: Optional[Dict] = None):

    global _vector_db

    if not text or not text.strip():
        print("[VECTOR] Empty text, skipping add")
        return None

    embeddings = get_embeddings()
    docs = split_text(text, metadata)

    if _vector_db is None:
        _vector_db = load_vector_store()

    if _vector_db:
        _vector_db.add_documents(docs)
    else:
        _vector_db = FAISS.from_documents(docs, embeddings)

    _vector_db.save_local(VECTOR_DB_PATH)

    print(f"[VECTOR] Added {len(docs)} chunks")

    return _vector_db


# ----------------------------------------
# 📥 LOAD VECTOR STORE (CACHED)
# ----------------------------------------
def load_vector_store():

    global _vector_db

    if _vector_db:
        return _vector_db

    if not os.path.exists(VECTOR_DB_PATH):
        print("[VECTOR] No DB found")
        return None

    embeddings = get_embeddings()

    _vector_db = FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    print("[VECTOR] Loaded existing DB")

    return _vector_db


# ----------------------------------------
# 🔍 QUERY VECTOR STORE
# ----------------------------------------
def query_vector_store(query: str, k: int = 4) -> List[str]:

    db = load_vector_store()

    if db is None:
        return []

    results = db.similarity_search(query, k=k)

    return [r.page_content for r in results]


# ----------------------------------------
# 🔍 QUERY WITH METADATA
# ----------------------------------------
def query_with_metadata(query: str, k: int = 4):

    db = load_vector_store()

    if db is None:
        return []

    results = db.similarity_search_with_score(query, k=k)

    return [
        {
            "text": doc.page_content,
            "score": float(score),
            "metadata": doc.metadata
        }
        for doc, score in results
    ]


# ----------------------------------------
# 🧹 RESET VECTOR STORE
# ----------------------------------------
def reset_vector_store():

    global _vector_db

    if os.path.exists(VECTOR_DB_PATH):

        for f in os.listdir(VECTOR_DB_PATH):
            os.remove(os.path.join(VECTOR_DB_PATH, f))

        _vector_db = None

        print("[VECTOR] Reset complete")
        return True

    return False


# ----------------------------------------
# 📊 VECTOR STORE INFO
# ----------------------------------------
def vector_store_info():

    if not os.path.exists(VECTOR_DB_PATH):
        return {"exists": False}

    files = os.listdir(VECTOR_DB_PATH)

    return {
        "exists": True,
        "files": files,
        "num_files": len(files)
    }
