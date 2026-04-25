import streamlit as st
import json
import re
import time
import requests

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage


# ----------------------------------------
# 🔐 CONFIG
# ----------------------------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
HF_API_TOKEN = st.secrets.get("HF_API_TOKEN", "")

HF_MODEL_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"


# ----------------------------------------
# 🧠 LOAD LLM (CACHED)
# ----------------------------------------
@st.cache_resource
def get_llm():
    return ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=0.2,
        groq_api_key=GROQ_API_KEY
    )


# ----------------------------------------
# 🧾 JSON PARSER (ROBUST)
# ----------------------------------------
def extract_json(text):

    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass

    return {"raw_output": text}


# ----------------------------------------
# 🚀 PRIMARY INVOKE (GROQ)
# ----------------------------------------
def invoke_llm(system_prompt: str, user_prompt: str, retries=2):

    llm = get_llm()

    for attempt in range(retries):
        try:
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])

            return response.content

        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                return f"LLM Error: {str(e)}"


# ----------------------------------------
# 🤖 FALLBACK → HUGGING FACE
# ----------------------------------------
def fallback_hf(prompt):

    if not HF_API_TOKEN:
        return "HF token missing"

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}"
    }

    payload = {"inputs": prompt}

    try:
        response = requests.post(
            HF_MODEL_URL,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            return f"HF Error: {response.text}"

        result = response.json()

        if isinstance(result, list):
            return result[0].get("generated_text", str(result))

        return str(result)

    except Exception as e:
        return f"HF Exception: {str(e)}"


# ----------------------------------------
# 🧠 SAFE INVOKE (WITH FALLBACK)
# ----------------------------------------
def safe_invoke(system_prompt, user_prompt):

    response = invoke_llm(system_prompt, user_prompt)

    if "Error" in str(response):
        response = fallback_hf(user_prompt)

    return response


# ----------------------------------------
# 🧠 MEMORY-AWARE INVOKE
# ----------------------------------------
def invoke_with_memory(memory, system_prompt, task_prompt):

    context = memory.get_context()

    full_prompt = f"""
    Context:
    {context}

    Task:
    {task_prompt}
    """

    return safe_invoke(system_prompt, full_prompt)


# ----------------------------------------
# 🧾 STRUCTURED ANALYSIS (MASTER)
# ----------------------------------------
def structured_analysis(context: str):

    system_prompt = "You are an expert PCB design engineer. Return JSON only."

    user_prompt = f"""
    Analyze PCB:

    {context}

    Output JSON:
    {{
        "summary": "...",
        "issues": [
            {{
                "category": "Power/Signal/Thermal/Layout",
                "issue": "...",
                "severity": "High/Medium/Low",
                "fix": "..."
            }}
        ],
        "score": 0-100
    }}
    """

    raw = safe_invoke(system_prompt, user_prompt)

    return extract_json(raw)


# ----------------------------------------
# ⚡ POWER AGENT
# ----------------------------------------
def power_analysis(memory):

    return invoke_with_memory(
        memory,
        "You are a PCB Power Integrity Expert.",
        "Analyze power issues and suggest fixes."
    )


# ----------------------------------------
# 🔌 SIGNAL AGENT
# ----------------------------------------
def signal_analysis(memory):

    return invoke_with_memory(
        memory,
        "You are a Signal Integrity Engineer.",
        "Analyze signal issues like crosstalk, reflection."
    )


# ----------------------------------------
# 🌡️ THERMAL AGENT
# ----------------------------------------
def thermal_analysis(memory):

    return invoke_with_memory(
        memory,
        "You are a Thermal Engineer.",
        "Detect hotspots and cooling issues."
    )


# ----------------------------------------
# 🧩 LAYOUT AGENT
# ----------------------------------------
def layout_analysis(memory):

    return invoke_with_memory(
        memory,
        "You are a PCB Layout Expert.",
        "Check spacing, placement, routing."
    )


# ----------------------------------------
# 🔧 TOOL / FIX AGENT
# ----------------------------------------
def tool_analysis(memory):

    return invoke_with_memory(
        memory,
        "You are a PCB Fix Engineer.",
        "Suggest actionable fixes."
    )


# ----------------------------------------
# 🧠 MASTER MULTI-AGENT
# ----------------------------------------
def run_multi_agent_analysis(memory):

    power = power_analysis(memory)
    memory.update("power", power)

    signal = signal_analysis(memory)
    memory.update("signal", signal)

    thermal = thermal_analysis(memory)
    memory.update("thermal", thermal)

    layout = layout_analysis(memory)
    memory.update("layout", layout)

    tools = tool_analysis(memory)
    memory.update("tools", tools)

    final = structured_analysis(memory.get_context())

    return {
        "power": power,
        "signal": signal,
        "thermal": thermal,
        "layout": layout,
        "tools": tools,
        "final": final
    }


# ----------------------------------------
# 💬 CHAT MODE
# ----------------------------------------
def chat_with_pcb(memory, user_query):

    return invoke_with_memory(
        memory,
        "You are a PCB AI assistant.",
        f"User question: {user_query}"
    )


# ----------------------------------------
# ⚡ STREAMLIT CACHE
# ----------------------------------------
@st.cache_data(show_spinner=False)
def cached_llm(system_prompt, user_prompt):

    return safe_invoke(system_prompt, user_prompt)
    
