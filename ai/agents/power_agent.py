import json
import re
import streamlit as st

from ai.llm import invoke_llm


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

    return {
        "issues": [],
        "summary": text,
        "confidence": 0.5,
        "raw_output": text
    }


# ----------------------------------------
# ⚡ MAIN POWER AGENT (MEMORY-BASED)
# ----------------------------------------
def run_power_agent(memory, structured=True):

    context = memory.get_all()

    prompt = f"""
    You are a senior PCB Power Integrity Engineer.

    Analyze the PCB for power-related issues using this context:

    {context}

    Focus on:
    - Power distribution quality
    - Ground plane continuity
    - Voltage stability
    - Decoupling capacitor placement
    - Power trace width adequacy
    - Return current paths

    Provide output in JSON:

    {{
        "issues": [
            {{
                "issue": "...",
                "severity": "High/Medium/Low",
                "explanation": "...",
                "fix": "...",
                "location": "optional",
                "confidence": 0.0-1.0
            }}
        ],
        "summary": "...",
        "confidence": 0.0-1.0
    }}
    """

    response = invoke_llm("PCB Power Expert", prompt)

    if structured:
        return extract_json(response)

    return response


# ----------------------------------------
# 🔍 ADVANCED POWER ANALYSIS
# ----------------------------------------
def advanced_power_analysis(memory):

    context = memory.get_all()

    prompt = f"""
    Perform deep power integrity analysis.

    Context:
    {context}

    Evaluate:
    - Current distribution efficiency
    - Power network impedance
    - Decoupling strategy effectiveness
    - Noise risks
    - IR drop potential

    Return JSON with:
    {{
        "power_network": "...",
        "grounding": "...",
        "decoupling": "...",
        "issues": [...],
        "recommendations": [...],
        "confidence": 0.0-1.0
    }}
    """

    response = invoke_llm("Advanced PCB Power Expert", prompt)

    return extract_json(response)


# ----------------------------------------
# 📊 POWER SCORE
# ----------------------------------------
def power_score(memory):

    context = memory.get_all()

    prompt = f"""
    Evaluate power integrity score (0-100):

    {context}

    Return JSON:
    {{
        "score": 0-100,
        "explanation": "...",
        "confidence": 0.0-1.0
    }}
    """

    response = invoke_llm("PCB Power Evaluator", prompt)

    return extract_json(response)


# ----------------------------------------
# ⚡ QUICK CHECK
# ----------------------------------------
def quick_power_check(memory):

    context = memory.get_all()

    prompt = f"""
    Quickly list major power issues:

    {context}

    Keep it short.
    """

    return invoke_llm("PCB Power Quick Check", prompt)


# ----------------------------------------
# 🔄 STREAMLIT CACHE
# ----------------------------------------
@st.cache_data(show_spinner=False)
def cached_power_agent(memory_dict):
    """
    Cache-friendly wrapper (memory must be dict)
    """
    class TempMemory:
        def __init__(self, data):
            self.data = data

        def get_all(self):
            return self.data

    temp_memory = TempMemory(memory_dict)
    return run_power_agent(temp_memory)


# ----------------------------------------
# 🧠 PRIORITIZATION
# ----------------------------------------
def prioritize_power_issues(power_output):

    prompt = f"""
    Prioritize these power issues:

    {power_output}

    Sort by severity and impact.
    """

    return invoke_llm("PCB Issue Prioritizer", prompt)


# ----------------------------------------
# 🔧 FIX SUGGESTION ENGINE
# ----------------------------------------
def suggest_power_fixes(memory):

    context = memory.get_all()

    prompt = f"""
    Suggest concrete fixes for power issues:

    {context}

    Include:
    - Layout changes
    - Component additions
    - Routing improvements
    """

    return invoke_llm("PCB Power Fix Expert", prompt)
    
