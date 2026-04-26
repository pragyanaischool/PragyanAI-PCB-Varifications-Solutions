# ui/chat_panel.py

"""
Advanced Chat Panel for PCB AI System

✔ ChatGPT-style UI
✔ RAG + Memory integration
✔ Streaming UX
✔ Debug + retrieval view
✔ Suggested prompts
✔ Session persistence
"""

import streamlit as st
from ai.rag import chat_with_rag, debug_rag
from ai.memory import PCBMemory


# ----------------------------------------
# 🧠 INIT SESSION STATE
# ----------------------------------------
def init_chat():

    if "pcb_memory" not in st.session_state:
        st.session_state.pcb_memory = PCBMemory()

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    if "last_query" not in st.session_state:
        st.session_state.last_query = ""


# ----------------------------------------
# 💬 DISPLAY CHAT HISTORY
# ----------------------------------------
def display_chat():

    for msg in st.session_state.chat_messages:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


# ----------------------------------------
# 🧠 ADD MESSAGE
# ----------------------------------------
def add_message(role, content):

    st.session_state.chat_messages.append({
        "role": role,
        "content": content
    })


# ----------------------------------------
# ⚡ SUGGESTED PROMPTS
# ----------------------------------------
def suggested_prompts():

    st.markdown("### ⚡ Quick Prompts")

    prompts = [
        "What are the critical issues in this PCB?",
        "How to fix power integrity problems?",
        "Explain routing issues",
        "Improve thermal performance",
        "Check grounding design",
    ]

    cols = st.columns(len(prompts))

    for i, p in enumerate(prompts):
        if cols[i].button(p):
            st.session_state.last_query = p


# ----------------------------------------
# 📊 SYSTEM STATUS
# ----------------------------------------
def show_system_status(memory):

    with st.expander("🧠 System Status"):

        summary = memory.summary()

        st.json({
            "memory_keys": summary["keys"],
            "chat_turns": summary["chat_turns"],
            "rag_chunks": summary["rag_chunks"]
        })


# ----------------------------------------
# 🔍 DEBUG PANEL
# ----------------------------------------
def show_debug_panel(query):

    with st.expander("🔍 Retrieval Debug"):

        debug = debug_rag(query)

        st.json(debug)


# ----------------------------------------
# 🚀 MAIN CHAT PANEL
# ----------------------------------------
def show_chat_panel(results):

    init_chat()

    memory = st.session_state.pcb_memory

    st.subheader("💬 PCB AI Engineer")

    # ----------------------------------------
    # 📦 LOAD PCB CONTEXT INTO MEMORY (ONCE)
    # ----------------------------------------
    if results and "loaded_context" not in st.session_state:

        memory.update("pcb_results", results)

        st.session_state.loaded_context = True

    # ----------------------------------------
    # 💬 CHAT HISTORY
    # ----------------------------------------
    display_chat()

    # ----------------------------------------
    # ⚡ SUGGESTIONS
    # ----------------------------------------
    suggested_prompts()

    # ----------------------------------------
    # 💬 INPUT
    # ----------------------------------------
    user_input = st.chat_input("Ask about your PCB...")

    # Support button-triggered prompts
    if st.session_state.last_query:
        user_input = st.session_state.last_query
        st.session_state.last_query = ""

    if user_input:

        # ----------------------------------------
        # ➕ USER MESSAGE
        # ----------------------------------------
        add_message("user", user_input)

        with st.chat_message("user"):
            st.markdown(user_input)

        # ----------------------------------------
        # 🤖 AI RESPONSE (WITH LOADER)
        # ----------------------------------------
        with st.chat_message("assistant"):

            placeholder = st.empty()

            with st.spinner("Analyzing PCB..."):

                response = chat_with_rag(user_input, memory)

            placeholder.markdown(response)

        add_message("assistant", response)

        # ----------------------------------------
        # 🔍 DEBUG
        # ----------------------------------------
        show_debug_panel(user_input)

    # ----------------------------------------
    # 📊 SYSTEM INFO
    # ----------------------------------------
    show_system_status(memory)

    # ----------------------------------------
    # 🧹 CLEAR CHAT
    # ----------------------------------------
    if st.button("🧹 Clear Chat"):
        st.session_state.chat_messages = []
        memory.clear()
        st.session_state.loaded_context = False
        st.rerun()
