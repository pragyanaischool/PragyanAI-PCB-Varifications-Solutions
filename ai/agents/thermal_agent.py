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
# 🌡️ MAIN THERMAL AGENT (MEMORY-BASED)
# ----------------------------------------
def run_thermal_agent(memory, structured=True):

    context = memory.get_all()

    # Cross-agent dependencies
    power_data = memory.get("power")
    layout_data = memory.get("layout")
    vision_data = memory.get("vision")

    prompt = f"""
    You are a senior PCB Thermal Engineer.

    Analyze thermal performance using the full PCB context.

    Context:
    {context}

    Power Analysis (heat sources):
    {power_data}

    Layout Analysis (placement impact):
    {layout_data}

    Vision Observations:
    {vision_data}

    Focus on:
    - Heat concentration zones
    - Power component clustering
    - Cooling inefficiencies
    - Copper area for heat dissipation
    - Thermal vias presence
    - Airflow constraints

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
        "hotspots": [
            {{
                "region": "...",
                "reason": "...",
                "severity": "...",
                "confidence": 0.0-1.0
            }}
        ],
        "summary": "...",
        "confidence": 0.0-1.0
    }}
    """

    response = invoke_llm("PCB Thermal Expert", prompt)

    if structured:
        return extract_json(response)

    return response


# ----------------------------------------
# 🔥 ADVANCED THERMAL ANALYSIS
# ----------------------------------------
def advanced_thermal_analysis(memory):

    context = memory.get_all()

    prompt = f"""
    Perform deep thermal analysis.

    Context:
    {context}

    Evaluate:
    - Heat distribution uniformity
    - Thermal resistance paths
    - Heat dissipation efficiency
    - Component overheating risk

    Return JSON:
    {{
        "heat_distribution": "...",
        "cooling_efficiency": "...",
        "risk_zones": "...",
        "issues": [...],
        "recommendations": [...],
        "confidence": 0.0-1.0
    }}
    """

    response = invoke_llm("Advanced Thermal Engineer", prompt)

    return extract_json(response)


# ----------------------------------------
# 📊 THERMAL SCORE
# ----------------------------------------
def thermal_score(memory):

    context = memory.get_all()

    prompt = f"""
    Evaluate thermal performance score (0-100):

    {context}

    Return JSON:
    {{
        "score": 0-100,
        "explanation": "...",
        "confidence": 0.0-1.0
    }}
    """

    response = invoke_llm("Thermal Evaluator", prompt)

    return extract_json(response)


# ----------------------------------------
# ⚡ QUICK THERMAL CHECK
# ----------------------------------------
def quick_thermal_check(memory):

    context = memory.get_all()

    prompt = f"""
    Quickly identify thermal risks:

    {context}

    Return short bullet points.
    """

    return invoke_llm("Thermal Quick Checker", prompt)


# ----------------------------------------
# 🔄 STREAMLIT CACHE
# ----------------------------------------
@st.cache_data(show_spinner=False)
def cached_thermal_agent(memory_dict):
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

    return run_thermal_agent(temp_memory)


# ----------------------------------------
# 🧠 PRIORITIZE THERMAL ISSUES
# ----------------------------------------
def prioritize_thermal_issues(thermal_output):

    prompt = f"""
    Prioritize thermal issues:

    {thermal_output}

    Rank by overheating risk and failure probability.
    """

    return invoke_llm("Thermal Issue Prioritizer", prompt)


# ----------------------------------------
# 🔧 COOLING STRATEGY ENGINE
# ----------------------------------------
def suggest_cooling_strategies(memory):

    context = memory.get_all()

    prompt = f"""
    Suggest cooling improvements:

    {context}

    Include:
    - Heat sinks
    - Thermal vias
    - Copper pours
    - Component relocation
    - Airflow optimization
    """

    return invoke_llm("Thermal Optimization Expert", prompt)
    
