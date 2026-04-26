# ai/rag.py

"""
Production RAG Pipeline for PCB AI System

✔ Cached retriever + chain
✔ Multi-turn chat memory
✔ Robust fallback handling
✔ Context + PCB fusion
✔ Streamlit-ready
"""

from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from ai.llm import get_llm
from ai.vector_store import load_vector_store


# ----------------------------------------
# 🧠 GLOBAL CACHE (IMPORTANT)
# ----------------------------------------
_rag_chain = None
_retriever = None


# ----------------------------------------
# 🔍 RETRIEVER (CACHED)
# ----------------------------------------
def get_retriever(k: int = 4):

    global _retriever

    if _retriever:
        return _retriever

    db = load_vector_store()

    if db is None:
        return None

    _retriever = db.as_retriever(search_kwargs={"k": k})

    return _retriever


# ----------------------------------------
# 🧠 FORMAT DOCUMENTS
# ----------------------------------------
def format_docs(docs):

    if not docs:
        return "No relevant PCB documents found."

    return "\n\n".join([d.page_content for d in docs])


# ----------------------------------------
# 🧠 PROMPT TEMPLATE (IMPROVED)
# ----------------------------------------
def get_prompt():

    return ChatPromptTemplate.from_template("""
You are an expert PCB Design Engineer AI.

Follow these rules:
- Use retrieved knowledge strictly when relevant
- If context is missing, rely on PCB engineering principles
- Avoid hallucination
- Be precise and practical

---------------------
PCB CONTEXT:
{pcb_context}

RETRIEVED KNOWLEDGE:
{context}

CHAT HISTORY:
{chat_history}
---------------------

User Question:
{question}

Answer with:
- Explanation
- Root cause
- Fix suggestions
""")


# ----------------------------------------
# 🚀 BUILD RAG CHAIN (CACHED)
# ----------------------------------------
def build_rag_chain(memory):

    global _rag_chain

    if _rag_chain:
        return _rag_chain

    retriever = get_retriever()
    llm = get_llm()
    prompt = get_prompt()

    if retriever is None:
        # Fallback chain
        _rag_chain = RunnableLambda(
            lambda x: llm.invoke(f"""
Answer as PCB expert:

Question: {x}
""").content
        )
        return _rag_chain

    _rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
            "pcb_context": lambda x: memory.get_context(),
            "chat_history": lambda x: memory.get_chat_context()
        }
        | prompt
        | llm
    )

    return _rag_chain


# ----------------------------------------
# 💬 MAIN CHAT FUNCTION (FIXED)
# ----------------------------------------
def chat_with_rag(user_query: str, memory):

    try:
        chain = build_rag_chain(memory)

        response = chain.invoke(user_query)

        # Normalize response
        if hasattr(response, "content"):
            response_text = response.content
        else:
            response_text = str(response)

        # Save conversation
        memory.add_chat(user_query, response_text)

        return response_text

    except Exception as e:
        return f"RAG Error: {str(e)}"


# ----------------------------------------
# ⚡ QUICK RAG (NO MEMORY)
# ----------------------------------------
def quick_rag(query: str):

    retriever = get_retriever()

    if retriever is None:
        return "No vector DB available"

    docs = retriever.invoke(query)

    context = format_docs(docs)

    llm = get_llm()

    return llm.invoke(f"""
Use this PCB context:

{context}

Question:
{query}
""").content


# ----------------------------------------
# 📊 DEBUG RAG
# ----------------------------------------
def debug_rag(query: str):

    retriever = get_retriever()

    if retriever is None:
        return {"error": "No DB"}

    docs = retriever.invoke(query)

    return {
        "query": query,
        "num_docs": len(docs),
        "docs": [d.page_content[:200] for d in docs]
    }


# ----------------------------------------
# 🔄 RESET CACHE (OPTIONAL)
# ----------------------------------------
def reset_rag():

    global _rag_chain, _retriever

    _rag_chain = None
    _retriever = None
