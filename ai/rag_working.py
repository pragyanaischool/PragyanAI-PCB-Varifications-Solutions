# ai/rag.py

"""
Modern RAG Pipeline for PCB AI System

✔ LangChain LCEL-style pipeline
✔ FAISS retriever integration
✔ Multi-turn chat memory
✔ PCB context + document fusion
✔ Clean modular design
"""

from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from ai.llm import get_llm
from ai.vector_store import load_vector_store


# ----------------------------------------
# 🔍 RETRIEVER
# ----------------------------------------
def get_retriever(k: int = 4):

    db = load_vector_store()

    if db is None:
        return None

    return db.as_retriever(search_kwargs={"k": k})


# ----------------------------------------
# 🧠 FORMAT DOCUMENTS
# ----------------------------------------
def format_docs(docs):

    return "\n\n".join([d.page_content for d in docs])


# ----------------------------------------
# 🧠 BUILD PROMPT
# ----------------------------------------
def get_prompt():

    return ChatPromptTemplate.from_template("""
You are an expert PCB Design Engineer AI.

Use the following context to answer:

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

Provide:
- Clear explanation
- Engineering insight
- Practical fixes
""")


# ----------------------------------------
# 🚀 BUILD RAG CHAIN (LCEL)
# ----------------------------------------
def build_rag_chain(memory):

    retriever = get_retriever()

    llm = get_llm()

    prompt = get_prompt()

    if retriever is None:
        # fallback (no vector DB)
        return RunnableLambda(lambda x: llm.invoke(x["question"]).content)

    chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
            "pcb_context": lambda x: memory.get_limited_context(),
            "chat_history": lambda x: memory.get_chat_context()
        }
        | prompt
        | llm
    )

    return chain


# ----------------------------------------
# 💬 MAIN CHAT FUNCTION
# ----------------------------------------
def chat_with_rag(user_query: str, memory):

    try:
        chain = build_rag_chain(memory)

        response = chain.invoke(user_query)

        if hasattr(response, "content"):
            response_text = response.content
        else:
            response_text = str(response)

        # Save to memory
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

    prompt = f"""
    Answer using this context:

    {context}

    Question:
    {query}
    """

    return llm.invoke(prompt).content


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
        "docs": [d.page_content[:300] for d in docs]
    }
