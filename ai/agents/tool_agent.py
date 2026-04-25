# ai/agents/tool_agent.py

import json
import re
import streamlit as st

from ai.llm import invoke_with_memory, invoke_llm


# ----------------------------------------
# 🧾 JSON PARSER (ROBUST)
# ----------------------------------------
def extract_json(text):

    if isinstance(text, dict):
        text = text.get("content", str(text))

    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", str(text), re.DOTALL)
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
# 🧠 NORMALIZE ACTIONS
# ----------------------------------------
def normalize_actions(actions):

    normalized = []
    seen = set()

    for a in actions:

        tool = a.get("tool", "Unknown")

        # enforce valid tools
        if tool not in AVAILABLE_TOOLS:
            tool = "General PCB Fix"

        key = (tool, a.get("issue"))

        if key in seen:
            continue

        seen.add(key)

        normalized.append({
            "tool": tool,
            "issue": a.get("issue", ""),
            "action": a.get("action", ""),
            "priority": a.get("priority", "Medium"),
            "expected_impact": a.get("expected_impact", ""),
            "confidence": a.get("confidence", 0.7)
        })

    return normalized


# ----------------------------------------
# 🤖 MAIN TOOL AGENT
# ----------------------------------------
def run_tool_agent(memory, structured=True):

    context = memory.get_all()

    power = memory.get("power")
    signal = memory.get("signal")
    thermal = memory.get("thermal")
    layout = memory.get("layout")
    vision = memory.get("vision")
    gnn = memory.get("gnn")

    prompt = f"""
    You are an expert PCB Fix Engineer.

    Analyze all issues:

    Power:
    {power}

    Signal:
    {signal}

    Thermal:
    {thermal}

    Layout:
    {layout}

    Vision:
    {vision}

    Graph/GNN:
    {gnn}

    Available Tools:
    {AVAILABLE_TOOLS}

    TASK:
    - Map issues → tools
    - Suggest fixes
    - Prioritize

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

    response = invoke_with_memory(memory, "PCB Fix Engineer", prompt)
    result = extract_json(response)

    # ----------------------------------------
    # 🔁 NORMALIZE + CLEAN
    # ----------------------------------------
    actions = normalize_actions(result.get("actions", []))

    # ----------------------------------------
    # ⚠️ FALLBACK LOGIC
    # ----------------------------------------
    if not actions:
        actions = [{
            "tool": "General PCB Fix",
            "issue": "No structured issues detected",
            "action": "Review PCB layout manually",
            "priority": "Medium",
            "expected_impact": "General improvement",
            "confidence": 0.5
        }]

    return {
        "actions": actions,
        "summary": result.get("summary", ""),
        "confidence": result.get("confidence", 0.7)
    } if structured else result


# ----------------------------------------
# ⚡ QUICK FIX MODE
# ----------------------------------------
def quick_fixes(memory):

    return invoke_with_memory(
        memory,
        "Quick PCB Fix Assistant",
        "Give top 5 actionable fixes."
    )


# ----------------------------------------
# 📊 PRIORITIZED ACTION PLAN
# ----------------------------------------
def prioritized_action_plan(memory):

    prompt = """
    Create prioritized PCB fix roadmap.

    Order by:
    - Risk
    - Impact
    - Effort
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

    return run_tool_agent(TempMemory(memory_dict))


# ----------------------------------------
# 🧠 PRIORITIZATION ENGINE
# ----------------------------------------
def prioritize_actions(tool_output):

    response = invoke_llm(
        "Fix Prioritizer",
        f"Prioritize actions:\n{tool_output}"
    )

    return response.get("content", response)


# ----------------------------------------
# 🔬 SIMULATION
# ----------------------------------------
def simulate_fix_impact(memory):

    prompt = """
    Simulate improvements after fixes.

    Predict:
    - Signal improvement
    - Power stability
    - Thermal reduction
    """

    return invoke_with_memory(
        memory,
        "PCB Simulation Expert",
        prompt
    )


# ----------------------------------------
# 🔧 EXECUTION PLAN
# ----------------------------------------
def generate_execution_steps(memory):

    prompt = """
    Generate step-by-step PCB fix plan.

    Include:
    - Order
    - Dependencies
    - Effort
    """

    return invoke_with_memory(
        memory,
        "PCB Execution Planner",
        prompt
    )
    
