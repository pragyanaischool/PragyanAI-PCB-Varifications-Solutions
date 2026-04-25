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
# ⚡ MAIN POWER AGENT (ENHANCED)
# ----------------------------------------
def run_power_agent(memory, structured=True):

    context = memory.get_all()

    # Cross-agent awareness
    vision = memory.get("vision")
    layout = memory.get("layout")
    signal = memory.get("signal")

    prompt = f"""
    You are a senior PCB Power Integrity Engineer.

    Analyze the PCB system using ALL context:

    Full Context:
    {context}

    Vision Data:
    {vision}

    Layout Insights:
    {layout}

    Signal Analysis:
    {signal}

    Focus on:
    - Power distribution network (PDN)
    - Ground plane continuity
    - Decoupling capacitor placement
    - Voltage stability
    - Power trace width adequacy
    - Return current paths
    - IR drop risk
    - Noise coupling with signal lines

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
        "PCB Power Integrity Expert",
        prompt
    )

    if structured:
        return extract_json(response)

    return response


# ----------------------------------------
# 🔍 ADVANCED POWER ANALYSIS
# ----------------------------------------
def advanced_power_analysis(memory):

    prompt = """
    Perform deep power integrity analysis.

    Evaluate:
    - PDN impedance
    - Current distribution
    - Decoupling effectiveness
    - Noise risks
    - IR drop

    Return structured JSON.
    """

    response = invoke_with_memory(
        memory,
        "Advanced PCB Power Engineer",
        prompt
    )

    return extract_json(response)


# ----------------------------------------
# 📊 POWER SCORE
# ----------------------------------------
def power_score(memory):

    prompt = """
    Evaluate power integrity score (0-100).

    Consider:
    - Stability
    - Noise
    - Layout quality
    - Decoupling

    Return JSON.
    """

    response = invoke_with_memory(
        memory,
        "PCB Power Evaluator",
        prompt
    )

    return extract_json(response)


# ----------------------------------------
# ⚡ QUICK CHECK
# ----------------------------------------
def quick_power_check(memory):

    return invoke_with_memory(
        memory,
        "Quick PCB Power Checker",
        "List top 3 power issues in bullet points."
    )


# ----------------------------------------
# 🔄 STREAMLIT CACHE
# ----------------------------------------
@st.cache_data(show_spinner=False)
def cached_power_agent(memory_dict):

    class TempMemory:
        def __init__(self, data):
            self.data = data

        def get_all(self):
            return self.data

        def get(self, key, default=None):
            return self.data.get(key, default)

    temp_memory = TempMemory(memory_dict)

    return run_power_agent(temp_memory)


# ----------------------------------------
# 🧠 PRIORITIZATION ENGINE
# ----------------------------------------
def prioritize_power_issues(power_output):

    prompt = f"""
    Prioritize these power issues:

    {power_output}

    Rank based on:
    - Severity
    - Impact on system stability
    - Risk of failure
    """

    from ai.llm import invoke_llm
    return invoke_llm("PCB Issue Prioritizer", prompt)


# ----------------------------------------
# 🔧 FIX SUGGESTION ENGINE
# ----------------------------------------
def suggest_power_fixes(memory):

    prompt = """
    Suggest concrete fixes for power issues.

    Include:
    - Capacitor placement
    - Ground improvements
    - Trace redesign
    - Layer optimization
    """

    return invoke_with_memory(
        memory,
        "PCB Power Fix Expert",
        prompt
    )


# ----------------------------------------
# 🔬 SIMULATION (OPTIONAL AI-BASED)
# ----------------------------------------
def simulate_power_improvement(memory):

    prompt = """
    Simulate improvements after fixes:

    Predict:
    - Noise reduction
    - Voltage stability improvement
    - Overall power score improvement
    """

    return invoke_with_memory(
        memory,
        "Power Simulation Expert",
        prompt
    )
    
