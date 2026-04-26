# ui/chat_panel.py

import streamlit as st
from datetime import datetime

from ai.rag import chat_with_rag
from ai.memory import PCBMemory


# ----------------------------------------
# 🧠 INIT SESSION STATE
# ----------------------------------------
def init_chat():

    if "pcb_memory" not in st.session_state:
        st.session_state.pcb_memory = PCBMemory()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "chat_initialized" not in st.session_state:
        st.session_state.chat_initialized = True


# ----------------------------------------
# 🧠 LOAD PCB ANALYSIS INTO MEMORY
# ----------------------------------------
def load_analysis_into_memory(results):

    memory = st.session_state.pcb_memory

    if not results:
        return

    # Add all system outputs
    for key in [
        "vision",
        "ocr",
        "gnn",
        "power",
        "signal",
        "thermal",
        "layout",
        "tools",
        "final"
    ]:
        if key in results:
            memory.update(key, results[key])


# ----------------------------------------
# 💬 MAIN CHAT PANEL
# ----------------------------------------
def show_chat_panel(results):

    st.subheader("💬 PCB AI Assistant")

    init_chat()

    # Load analysis once
    if results:
        load_analysis_into_memory(results)

    memory = st.session_state.pcb_memory

    # ----------------------------------------
    # 📜 DISPLAY CHAT HISTORY
    # ----------------------------------------
    for msg in st.session_state.chat_history:

        role = msg["role"]

        with st.chat_message(role):
            st.markdown(msg["content"])

            # Show timestamp
            st.caption(msg["time"])

    # ----------------------------------------
    # 💬 USER INPUT
    # ----------------------------------------
    user_input = st.chat_input("Ask about your PCB...")

    if user_input:

        timestamp = datetime.now().strftime("%H:%M:%S")

        # Save user message
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "time": timestamp
        })

        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)

        # ----------------------------------------
        # 🤖 AI RESPONSE
        # ----------------------------------------
        with st.chat_message("assistant"):
            with st.spinner("Analyzing PCB..."):

                response = chat_with_rag(user_input, memory)

                st.markdown(response)

        # Save AI response
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response,
            "time": timestamp
        })


# ----------------------------------------
# 🧠 SIDEBAR CONTROLS
# ----------------------------------------
def chat_controls():

    st.sidebar.markdown("### 💬 Chat Controls")

    if st.sidebar.button("🧹 Clear Chat"):
        st.session_state.chat_history = []

    if st.sidebar.button("🧠 Reset Memory"):
        st.session_state.pcb_memory = PCBMemory()

    if st.sidebar.button("📊 Show Memory"):
        st.sidebar.json(st.session_state.pcb_memory.get_all())


# ----------------------------------------
# ⚡ QUICK QUESTIONS (SMART UX)
# ----------------------------------------
def quick_questions():

    st.markdown("### ⚡ Quick Questions")

    questions = [
        "What are the main issues in this PCB?",
        "Are there power integrity problems?",
        "Explain signal routing issues",
        "Suggest fixes for this design",
        "Is thermal management adequate?"
    ]

    cols = st.columns(2)

    for i, q in enumerate(questions):

        if cols[i % 2].button(q):

            st.session_state.chat_history.append({
                "role": "user",
                "content": q,
                "time": datetime.now().strftime("%H:%M:%S")
            })


# ----------------------------------------
# 📊 DEBUG PANEL (OPTIONAL)
# ----------------------------------------
def debug_chat():

    with st.expander("🧪 Debug Chat"):

        st.write("### Memory")
        st.json(st.session_state.pcb_memory.get_all())

        st.write("### Chat History")
        st.json(st.session_state.chat_history)
