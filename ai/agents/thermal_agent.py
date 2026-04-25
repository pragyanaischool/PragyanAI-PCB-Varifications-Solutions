import json
import re
import streamlit as st

from ai.llm import invoke_with_memory


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
        "summary": str(text),
        "confidence": 0.5,
        "raw_output": text
    }


# ----------------------------------------
# 🌡️ MAIN THERMAL AGENT (ENHANCED)
# ----------------------------------------
def run_thermal_agent(memory, structured=True):

    context = memory.get_all()

    # Cross-agent awareness
    power = memory.get("power")
    layout = memory.get("layout")
    signal = memory.get("signal")
    vision = memory.get("vision")

    prompt = f"""
    You are a senior PCB Thermal Engineer.

    Analyze thermal behavior using FULL context:

    Full Context:
    {context}

    Power Analysis:
    {power}

    Layout Analysis:
    {layout}

    Signal Analysis:
    {signal}

    Vision Data:
    {vision}

    Focus on:
    - Heat generation (high-power components)
    - Hotspot detection
    - Thermal dissipation efficiency
    - Copper area for heat spreading
    - Thermal vias effectiveness
    - Airflow and cooling paths
    - Component clustering causing heat buildup
    - Risk of overheating or failure

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

    response = invoke_with_memory(
        memory,
        "PCB Thermal Expert",
        prompt
    )

    if structured:
        return extract_json(response)

    return response


# ----------------------------------------
# 🔍 ADVANCED THERMAL ANALYSIS
# ----------------------------------------
def advanced_thermal_analysis(memory):

    prompt = """
    Perform deep thermal analysis.

    Evaluate:
    - Heat flow paths
    - Thermal resistance
    - Hotspot severity
    - Cooling efficiency
    - Risk of thermal runaway

    Return JSON:
    {
        "thermal_profile": "...",
        "cooling_efficiency": "...",
        "issues": [...],
        "recommendations": [...],
        "confidence": 0.0-1.0
    }
    """

    response = invoke_with_memory(
        memory,
        "Advanced Thermal Engineer",
        prompt
    )

    return extract_json(response)


# ----------------------------------------
# 📊 THERMAL SCORE
# ----------------------------------------
def thermal_score(memory):

    prompt = """
    Evaluate thermal performance score (0-100).

    Consider:
    - Heat distribution
    - Cooling
    - Component placement
    - Thermal risks

    Return JSON.
    """

    response = invoke_with_memory(
        memory,
        "Thermal Evaluator",
        prompt
    )

    return extract_json(response)


# ----------------------------------------
# ⚡ QUICK CHECK
# ----------------------------------------
def quick_thermal_check(memory):

    return invoke_with_memory(
        memory,
        "Quick Thermal Checker",
        "List top 3 thermal issues."
    )


# ----------------------------------------
# 🔄 CACHE WRAPPER
# ----------------------------------------
@st.cache_data(show_spinner=False)
def cached_thermal_agent(memory_dict):

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
# 🧠 PRIORITIZATION
# ----------------------------------------
def prioritize_thermal_issues(thermal_output):

    prompt = f"""
    Prioritize thermal issues:

    {thermal_output}

    Rank based on:
    - Overheating risk
    - Failure probability
    - Impact on performance
    """

    from ai.llm import invoke_llm
    return invoke_llm("Thermal Issue Prioritizer", prompt)


# ----------------------------------------
# 🔧 FIX SUGGESTION ENGINE
# ----------------------------------------
def suggest_thermal_fixes(memory):

    prompt = """
    Suggest thermal improvements:

    Include:
    - Heat sink usage
    - Thermal vias addition
    - Copper area increase
    - Component repositioning
    - Cooling strategies
    """

    return invoke_with_memory(
        memory,
        "Thermal Fix Expert",
        prompt
    )


# ----------------------------------------
# 🔬 THERMAL SIMULATION (AI-BASED)
# ----------------------------------------
def simulate_thermal_improvement(memory):

    prompt = """
    Simulate improvements after thermal fixes:

    Predict:
    - Reduced hotspot temperature
    - Better heat distribution
    - Improved reliability
    """

    return invoke_with_memory(
        memory,
        "Thermal Simulation Expert",
        prompt
    )
    
