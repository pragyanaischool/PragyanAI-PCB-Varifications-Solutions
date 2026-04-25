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

MAX_RETRIES = 3
TIMEOUT = 60


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

    if not text:
        return {"error": "Empty response"}

    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass

    return {
        "raw_output": text,
        "confidence": 0.5
    }


# ----------------------------------------
# 🧠 VALIDATE RESPONSE
# ----------------------------------------
def validate_response(response):

    if not response:
        return False

    if isinstance(response, str) and len(response.strip()) < 5:
        return False

    return True


# ----------------------------------------
# 🚀 PRIMARY INVOKE (GROQ)
# ----------------------------------------
def invoke_llm(system_prompt: str, user_prompt: str):

    llm = get_llm()

    for attempt in range(MAX_RETRIES):
        try:
            start = time.time()

            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])

            latency = round(time.time() - start, 2)

            if not validate_response(response.content):
                raise ValueError("Invalid LLM response")

            return {
                "content": response.content,
                "latency": latency,
                "source": "groq"
            }

        except Exception as e:

            # Handle rate limit / retry
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 * (attempt + 1))
            else:
                return {
                    "content": f"LLM Error: {str(e)}",
                    "latency": 0,
                    "source": "error"
                }


# ----------------------------------------
# 🤖 FALLBACK → HUGGING FACE
# ----------------------------------------
def fallback_hf(prompt):

    if not HF_API_TOKEN:
        return {
            "content": "HF token missing",
            "source": "hf_error"
        }

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}"
    }

    payload = {"inputs": prompt}

    try:
        response = requests.post(
            HF_MODEL_URL,
            headers=headers,
            json=payload,
            timeout=TIMEOUT
        )

        if response.status_code != 200:
            return {
                "content": f"HF Error: {response.text}",
                "source": "hf_error"
            }

        result = response.json()

        if isinstance(result, list):
            return {
                "content": result[0].get("generated_text", str(result)),
                "source": "hf"
            }

        return {
            "content": str(result),
            "source": "hf"
        }

    except Exception as e:
        return {
            "content": f"HF Exception: {str(e)}",
            "source": "hf_exception"
        }


# ----------------------------------------
# 🧠 SAFE INVOKE (WITH FALLBACK)
# ----------------------------------------
def safe_invoke(system_prompt, user_prompt):

    response = invoke_llm(system_prompt, user_prompt)

    if response["source"] == "error":
        fallback = fallback_hf(user_prompt)
        return fallback["content"]

    return response["content"]


# ----------------------------------------
# 🧠 MEMORY-AWARE INVOKE
# ----------------------------------------
def invoke_with_memory(memory, system_prompt, task_prompt):

    context = ""

    if memory:
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
# 🤖 MULTI-AGENT WRAPPER
# ----------------------------------------
def run_multi_agent_analysis(memory):

    agents = {}

    for name, prompt in [
        ("power", "Analyze power issues"),
        ("signal", "Analyze signal integrity"),
        ("thermal", "Analyze thermal risks"),
        ("layout", "Analyze layout design")
    ]:

        result = invoke_with_memory(
            memory,
            f"You are a PCB {name} expert.",
            prompt
        )

        memory.update(name, result)
        agents[name] = result

    tools = invoke_with_memory(
        memory,
        "You are a PCB fix expert.",
        "Suggest fixes"
    )

    memory.update("tools", tools)

    final = structured_analysis(memory.get_context())

    return {
        **agents,
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
# ⚡ CACHE
# ----------------------------------------
@st.cache_data(show_spinner=False)
def cached_llm(system_prompt, user_prompt):

    return safe_invoke(system_prompt, user_prompt)
    
