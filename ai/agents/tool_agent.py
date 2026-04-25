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
        "actions": [],
        "summary": text,
        "confidence": 0.5,
        "raw_output": text
    }


# ----------------------------------------
# 🔧 TOOL DEFINITIONS (CAN EXPAND)
# ----------------------------------------
AVAILABLE_TOOLS = [
    "Fix trace width",
    "Suggest rerouting",
    "Add decoupling capacitor",
    "Improve grounding",
    "Add thermal vias",
    "Optimize component placement",
    "Reduce EMI",
    "Improve signal routing"
]


# ----------------------------------------
# 🤖 MAIN TOOL AGENT
# ----------------------------------------
def run_tool_agent(memory, structured=True):

    context = memory.get_all()

    # Collect all issues from agents
    power = memory.get("power")
    signal = memory.get("signal")
    thermal = memory.get("thermal")
    layout = memory.get("layout")

    prompt = f"""
    You are an expert PCB Design Fix Assistant.

    Based on the complete PCB analysis:

    {context}

    Available tools:
    {AVAILABLE_TOOLS}

    Your job:
    - Identify critical issues
    - Map each issue to a specific tool/action
    - Suggest step-by-step fixes

    Output STRICT JSON:

    {{
        "actions": [
            {{
                "tool": "...",
                "issue": "...",
                "action": "...",
                "priority": "High/Medium/Low",
                "expected_impact": "...",
                "confidence": 0.0-1.0
            }}
        ],
        "summary": "...",
        "confidence": 0.0-1.0
    }}
    """

    response = invoke_llm("PCB Fix Engineer", prompt)

    if structured:
        return extract_json(response)

    return response


# ----------------------------------------
# ⚡ QUICK FIX MODE
# ----------------------------------------
def quick_fixes(memory):

    context = memory.get_all()

    prompt = f"""
    Quickly suggest top 5 PCB fixes:

    {context}

    Keep it short and actionable.
    """

    return invoke_llm("Quick PCB Fix Assistant", prompt)


# ----------------------------------------
# 📊 PRIORITIZED ACTION PLAN
# ----------------------------------------
def prioritized_action_plan(memory):

    context = memory.get_all()

    prompt = f"""
    Create a prioritized PCB improvement plan:

    {context}

    Order by:
    - Risk
    - Impact
    - Ease of implementation
    """

    return invoke_llm("PCB Optimization Planner", prompt)


# ----------------------------------------
# 🔄 STREAMLIT CACHE
# ----------------------------------------
@st.cache_data(show_spinner=False)
def cached_tool_agent(memory_dict):

    class TempMemory:
        def __init__(self, data):
            self.data = data

        def get_all(self):
            return self.data

        def get(self, key, default=None):
            return self.data.get(key, default)

    temp_memory = TempMemory(memory_dict)

    return run_tool_agent(temp_memory)


# ----------------------------------------
# 🧠 AUTO-FIX SIMULATION (OPTIONAL)
# ----------------------------------------
def simulate_fix(memory):

    context = memory.get_all()

    prompt = f"""
    Simulate improvements after applying fixes:

    {context}

    Predict:
    - Improvement in signal integrity
    - Reduction in thermal issues
    - Overall score improvement
    """

    return invoke_llm("PCB Simulation Expert", prompt)
