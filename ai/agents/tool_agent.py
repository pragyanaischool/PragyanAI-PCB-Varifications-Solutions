import json
import re
import streamlit as st

from ai.llm import invoke_with_memory, invoke_llm


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
        "summary": str(text),
        "confidence": 0.5,
        "raw_output": text
    }


# ----------------------------------------
# 🔧 AVAILABLE TOOL SET
# ----------------------------------------
AVAILABLE_TOOLS = [
    "Fix trace width",
    "Reroute signal traces",
    "Add decoupling capacitor",
    "Improve grounding",
    "Add thermal vias",
    "Optimize component placement",
    "Reduce EMI",
    "Improve differential pair routing",
    "Increase copper area",
    "Add shielding"
]


# ----------------------------------------
# 🤖 MAIN TOOL AGENT
# ----------------------------------------
def run_tool_agent(memory, structured=True):

    context = memory.get_all()

    # Cross-agent outputs
    power = memory.get("power")
    signal = memory.get("signal")
    thermal = memory.get("thermal")
    layout = memory.get("layout")
    vision = memory.get("vision")

    prompt = f"""
    You are an expert PCB Design Fix Engineer.

    Based on full PCB analysis:

    Full Context:
    {context}

    Power Issues:
    {power}

    Signal Issues:
    {signal}

    Thermal Issues:
    {thermal}

    Layout Issues:
    {layout}

    Vision Insights:
    {vision}

    Available Tools:
    {AVAILABLE_TOOLS}

    Your task:
    - Identify critical issues
    - Map each issue to a specific tool/action
    - Suggest step-by-step fixes
    - Prioritize actions

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

    response = invoke_with_memory(
        memory,
        "PCB Fix Engineer",
        prompt
    )

    if structured:
        return extract_json(response)

    return response


# ----------------------------------------
# ⚡ QUICK FIX MODE
# ----------------------------------------
def quick_fixes(memory):

    return invoke_with_memory(
        memory,
        "Quick PCB Fix Assistant",
        "Suggest top 5 quick fixes."
    )


# ----------------------------------------
# 📊 PRIORITIZED ACTION PLAN
# ----------------------------------------
def prioritized_action_plan(memory):

    prompt = """
    Create prioritized PCB improvement plan.

    Order by:
    - Risk
    - Impact
    - Ease of implementation
    """

    return invoke_with_memory(
        memory,
        "PCB Optimization Planner",
        prompt
    )


# ----------------------------------------
# 🔄 CACHE WRAPPER
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
# 🧠 PRIORITIZATION ENGINE
# ----------------------------------------
def prioritize_actions(tool_output):

    prompt = f"""
    Prioritize these PCB fixes:

    {tool_output}

    Rank based on:
    - Severity
    - System impact
    - Ease of fix
    """

    return invoke_llm("Fix Prioritizer", prompt)


# ----------------------------------------
# 🔬 SIMULATION (IMPACT PREDICTION)
# ----------------------------------------
def simulate_fix_impact(memory):

    prompt = """
    Simulate improvements after applying fixes.

    Predict:
    - Signal improvement
    - Power stability improvement
    - Thermal reduction
    - Overall system score increase
    """

    return invoke_with_memory(
        memory,
        "PCB Simulation Expert",
        prompt
    )


# ----------------------------------------
# 🔧 EXECUTION PLAN (STEP-BY-STEP)
# ----------------------------------------
def generate_execution_steps(memory):

    prompt = """
    Generate step-by-step execution plan to fix PCB issues.

    Include:
    - Order of operations
    - Dependencies between fixes
    - Estimated effort
    """

    return invoke_with_memory(
        memory,
        "PCB Execution Planner",
        prompt
    )
    
