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
# 🔌 MAIN SIGNAL AGENT (ENHANCED)
# ----------------------------------------
def run_signal_agent(memory, structured=True):

    context = memory.get_all()

    # Cross-agent awareness
    power = memory.get("power")
    layout = memory.get("layout")
    vision = memory.get("vision")

    prompt = f"""
    You are a senior Signal Integrity Engineer.

    Analyze PCB signal behavior using FULL context:

    Full Context:
    {context}

    Power Analysis:
    {power}

    Layout Analysis:
    {layout}

    Vision Data:
    {vision}

    Focus on:
    - Crosstalk between traces
    - Impedance mismatch
    - Signal reflections
    - Trace length matching
    - Differential pair routing
    - Signal-to-power interference
    - EMI/EMC risks
    - High-speed signal integrity issues

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
        "PCB Signal Integrity Expert",
        prompt
    )

    if structured:
        return extract_json(response)

    return response


# ----------------------------------------
# 🔍 ADVANCED SIGNAL ANALYSIS
# ----------------------------------------
def advanced_signal_analysis(memory):

    prompt = """
    Perform deep signal integrity analysis.

    Evaluate:
    - Transmission line effects
    - Impedance control
    - Differential pair balance
    - EMI/EMC risk
    - Signal delay mismatch

    Return structured JSON:
    {
        "signal_quality": "...",
        "impedance_control": "...",
        "issues": [...],
        "recommendations": [...],
        "confidence": 0.0-1.0
    }
    """

    response = invoke_with_memory(
        memory,
        "Advanced Signal Integrity Engineer",
        prompt
    )

    return extract_json(response)


# ----------------------------------------
# 📊 SIGNAL SCORE
# ----------------------------------------
def signal_score(memory):

    prompt = """
    Evaluate signal integrity score (0-100).

    Consider:
    - Crosstalk
    - Reflection
    - Impedance
    - Routing quality

    Return JSON.
    """

    response = invoke_with_memory(
        memory,
        "Signal Evaluator",
        prompt
    )

    return extract_json(response)


# ----------------------------------------
# ⚡ QUICK CHECK
# ----------------------------------------
def quick_signal_check(memory):

    return invoke_with_memory(
        memory,
        "Quick Signal Checker",
        "List top 3 signal issues."
    )


# ----------------------------------------
# 🔄 CACHE WRAPPER
# ----------------------------------------
@st.cache_data(show_spinner=False)
def cached_signal_agent(memory_dict):

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
    Prioritize signal issues:

    {signal_output}

    Rank based on:
    - Severity
    - Impact on performance
    - EMI risk
    """

    from ai.llm import invoke_llm
    return invoke_llm("Signal Issue Prioritizer", prompt)


# ----------------------------------------
# 🔧 FIX SUGGESTION ENGINE
# ----------------------------------------
def suggest_signal_fixes(memory):

    prompt = """
    Suggest signal integrity improvements:

    Include:
    - Trace rerouting
    - Impedance control fixes
    - Differential pair correction
    - EMI reduction techniques
    """

    return invoke_with_memory(
        memory,
        "Signal Fix Expert",
        prompt
    )


# ----------------------------------------
# 🔬 SIGNAL SIMULATION (AI-BASED)
# ----------------------------------------
def simulate_signal_improvement(memory):

    prompt = """
    Simulate improvements after signal fixes:

    Predict:
    - Reduced crosstalk
    - Improved timing
    - Reduced EMI
    """

    return invoke_with_memory(
        memory,
        "Signal Simulation Expert",
        prompt
    )
    
