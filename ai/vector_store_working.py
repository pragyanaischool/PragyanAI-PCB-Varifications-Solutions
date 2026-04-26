# ai/vector_store.py

"""
Vector Store (FAISS) for PCB RAG System

✔ Build vector DB from text/chunks
✔ Save & load locally
✔ Incrementally add documents
✔ Query relevant chunks
✔ Supports PDF, BOM, netlist, docs
"""

import os
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ----------------------------------------
# ⚙️ CONFIG
# ----------------------------------------
VECTOR_DB_PATH = "data/vector_store"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ----------------------------------------
# 🧠 LOAD EMBEDDINGS
# ----------------------------------------
def get_embeddings():

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )


# ----------------------------------------
# ✂️ CHUNK TEXT
# ----------------------------------------
def split_text(text: str, chunk_size=500, overlap=50):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )

    return splitter.create_documents([text])


# ----------------------------------------
# 🚀 BUILD VECTOR STORE (FRESH)
# ----------------------------------------
def build_vector_store(text: str):

    if not text or len(text.strip()) == 0:
        print("[VECTOR] Empty text, skipping build")
        return None

    docs = split_text(text)

    embeddings = get_embeddings()

    db = FAISS.from_documents(docs, embeddings)

    os.makedirs(VECTOR_DB_PATH, exist_ok=True)

    db.save_local(VECTOR_DB_PATH)

    print(f"[VECTOR] Built DB with {len(docs)} chunks")

    return db


# ----------------------------------------
# ➕ ADD DOCUMENTS (INCREMENTAL)
# ----------------------------------------
def add_to_vector_store(text: str):

    if not text or len(text.strip()) == 0:
        print("[VECTOR] Empty text, skipping add")
        return None

    embeddings = get_embeddings()

    docs = split_text(text)

    # Load existing or create new
    if os.path.exists(VECTOR_DB_PATH):

        db = FAISS.load_local(
            VECTOR_DB_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

        db.add_documents(docs)

    else:
        db = FAISS.from_documents(docs, embeddings)

    db.save_local(VECTOR_DB_PATH)

    print(f"[VECTOR] Added {len(docs)} new chunks")

    return db


# ----------------------------------------
# 📥 LOAD VECTOR STORE
# ----------------------------------------
def load_vector_store():

    if not os.path.exists(VECTOR_DB_PATH):
        print("[VECTOR] No DB found")
        return None

    embeddings = get_embeddings()

    return FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )


# ----------------------------------------
# 🔍 QUERY VECTOR STORE
# ----------------------------------------
def query_vector_store(query: str, k: int = 3) -> List[str]:

    db = load_vector_store()

    if db is None:
        return []

    results = db.similarity_search(query, k=k)

    return [r.page_content for r in results]


# ----------------------------------------
# 🔍 QUERY WITH SCORES (ADVANCED)
# ----------------------------------------
def query_with_scores(query: str, k: int = 3):

    db = load_vector_store()

    if db is None:
        return []

    results = db.similarity_search_with_score(query, k=k)

    return [
        {
            "text": doc.page_content,
            "score": float(score)
        }
        for doc, score in results
    ]


# ----------------------------------------
# 🧹 RESET VECTOR STORE
# ----------------------------------------
def reset_vector_store():

    if os.path.exists(VECTOR_DB_PATH):

        for file in os.listdir(VECTOR_DB_PATH):
            os.remove(os.path.join(VECTOR_DB_PATH, file))

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
