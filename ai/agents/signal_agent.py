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
# 🔌 MAIN SIGNAL AGENT (MEMORY-BASED)
# ----------------------------------------
def run_signal_agent(memory, structured=True):

    context = memory.get_all()

    # Cross-agent inputs
    power_data = memory.get("power")
    vision_data = memory.get("vision")
    graph_data = memory.get("graph")

    prompt = f"""
    You are a senior PCB Signal Integrity Engineer.

    Analyze signal integrity issues using the full PCB context.

    Context:
    {context}

    Power Analysis (important for SI):
    {power_data}

    Vision Observations:
    {vision_data}

    Graph Structure:
    {graph_data}

    Focus on:
    - Crosstalk between traces
    - Impedance mismatch
    - Signal reflections
    - Trace length mismatch
    - High-speed routing issues
    - Differential pair imbalance
    - EMI/EMC risks

    Output STRICT JSON:

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

    response = invoke_llm("PCB Signal Expert", prompt)

    if structured:
        return extract_json(response)

    return response


# ----------------------------------------
# 🔍 ADVANCED SIGNAL ANALYSIS
# ----------------------------------------
def advanced_signal_analysis(memory):

    context = memory.get_all()

    prompt = f"""
    Perform deep signal integrity analysis.

    Context:
    {context}

    Evaluate:
    - Transmission line effects
    - Differential pair balance
    - Clock signal integrity
    - Noise coupling
    - EMI/EMC vulnerabilities

    Return JSON:
    {{
        "crosstalk": "...",
        "impedance": "...",
        "reflections": "...",
        "timing": "...",
        "issues": [...],
        "recommendations": [...],
        "confidence": 0.0-1.0
    }}
    """

    response = invoke_llm("Advanced Signal Integrity Expert", prompt)

    return extract_json(response)


# ----------------------------------------
# 📊 SIGNAL SCORE
# ----------------------------------------
def signal_score(memory):

    context = memory.get_all()

    prompt = f"""
    Evaluate signal integrity score (0-100):

    {context}

    Return JSON:
    {{
        "score": 0-100,
        "explanation": "...",
        "confidence": 0.0-1.0
    }}
    """

    response = invoke_llm("Signal Quality Evaluator", prompt)

    return extract_json(response)


# ----------------------------------------
# ⚡ QUICK SIGNAL CHECK
# ----------------------------------------
def quick_signal_check(memory):

    context = memory.get_all()

    prompt = f"""
    Quickly identify major signal issues:

    {context}

    Return short bullet points.
    """

    return invoke_llm("Signal Quick Checker", prompt)


# ----------------------------------------
# 🔄 STREAMLIT CACHE
# ----------------------------------------
@st.cache_data(show_spinner=False)
def cached_signal_agent(memory_dict):
    """
    Cache-friendly wrapper
    """

    class TempMemory:
        def __init__(self, data):
            self.data = data

        def get_all(self):
            return self.data

        def get(self, key, default=None):
            return self.data.get(key, default)

    temp_memory = TempMemory(memory_dict)

    return run_signal_agent(temp_memory)


# ----------------------------------------
# 🧠 PRIORITIZATION
# ----------------------------------------
def prioritize_signal_issues(signal_output):

    prompt = f"""
    Prioritize these signal issues:

    {signal_output}

    Rank by severity, timing impact, and EMI risk.
    """

    return invoke_llm("Signal Issue Prioritizer", prompt)


# ----------------------------------------
# 🔧 FIX SUGGESTION ENGINE
# ----------------------------------------
def suggest_signal_fixes(memory):

    context = memory.get_all()

    prompt = f"""
    Suggest fixes for signal integrity issues:

    {context}

    Include:
    - Trace routing improvements
    - Shielding techniques
    - Impedance control suggestions
    - Differential pair corrections
    """

    return invoke_llm("Signal Fix Expert", prompt)
    
