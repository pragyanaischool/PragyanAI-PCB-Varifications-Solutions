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
# 🧩 MAIN LAYOUT AGENT (MEMORY-BASED)
# ----------------------------------------
def run_layout_agent(memory, structured=True):

    context = memory.get_all()

    # Cross-agent inputs
    vision_data = memory.get("vision")
    signal_data = memory.get("signal")
    power_data = memory.get("power")
    thermal_data = memory.get("thermal")

    prompt = f"""
    You are a senior PCB Layout Engineer.

    Analyze PCB layout using the complete system context.

    Context:
    {context}

    Vision Insights:
    {vision_data}

    Signal Analysis:
    {signal_data}

    Power Analysis:
    {power_data}

    Thermal Analysis:
    {thermal_data}

    Focus on:
    - Component placement optimization
    - Routing efficiency
    - Trace spacing and clearance
    - Power vs signal separation
    - EMI/EMC risk zones
    - Layer utilization
    - Design Rule Check (DRC)
    - Manufacturability (DFM)

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
        "drc_violations": [
            {{
                "type": "...",
                "severity": "...",
                "fix": "...",
                "confidence": 0.0-1.0
            }}
        ],
        "summary": "...",
        "confidence": 0.0-1.0
    }}
    """

    response = invoke_llm("PCB Layout Expert", prompt)

    if structured:
        return extract_json(response)

    return response


# ----------------------------------------
# 🔍 ADVANCED LAYOUT ANALYSIS
# ----------------------------------------
def advanced_layout_analysis(memory):

    context = memory.get_all()

    prompt = f"""
    Perform deep layout analysis.

    Context:
    {context}

    Evaluate:
    - Placement density
    - Routing congestion
    - Signal vs power isolation
    - EMI hotspots
    - Manufacturability risks

    Return JSON:
    {{
        "placement_quality": "...",
        "routing_efficiency": "...",
        "layer_usage": "...",
        "issues": [...],
        "recommendations": [...],
        "confidence": 0.0-1.0
    }}
    """

    response = invoke_llm("Advanced Layout Engineer", prompt)

    return extract_json(response)


# ----------------------------------------
# ⚠️ DESIGN RULE CHECK (DRC)
# ----------------------------------------
def drc_analysis(memory):

    context = memory.get_all()

    prompt = f"""
    Perform PCB Design Rule Check (DRC):

    {context}

    Check:
    - Clearance violations
    - Trace spacing
    - Via placement
    - Component overlap

    Return JSON:
    {{
        "violations": [
            {{
                "type": "...",
                "severity": "...",
                "fix": "...",
                "confidence": 0.0-1.0
            }}
        ]
    }}
    """

    response = invoke_llm("DRC Expert", prompt)

    return extract_json(response)


# ----------------------------------------
# 🏭 MANUFACTURABILITY (DFM)
# ----------------------------------------
def manufacturability_analysis(memory):

    context = memory.get_all()

    prompt = f"""
    Evaluate PCB manufacturability (DFM):

    {context}

    Check:
    - Minimum trace width
    - Drill feasibility
    - Solder mask issues
    - Assembly complexity

    Return JSON:
    {{
        "dfm_score": "...",
        "issues": [...],
        "recommendations": [...],
        "confidence": 0.0-1.0
    }}
    """

    response = invoke_llm("DFM Expert", prompt)

    return extract_json(response)


# ----------------------------------------
# 📊 LAYOUT SCORE
# ----------------------------------------
def layout_score(memory):

    context = memory.get_all()

    prompt = f"""
    Evaluate PCB layout score (0-100):

    {context}

    Return JSON:
    {{
        "score": 0-100,
        "explanation": "...",
        "confidence": 0.0-1.0
    }}
    """

    response = invoke_llm("Layout Evaluator", prompt)

    return extract_json(response)


# ----------------------------------------
# ⚡ QUICK LAYOUT CHECK
# ----------------------------------------
def quick_layout_check(memory):

    context = memory.get_all()

    prompt = f"""
    Quickly identify layout issues:

    {context}

    Return short bullet points.
    """

    return invoke_llm("Layout Quick Checker", prompt)


# ----------------------------------------
# 🔄 STREAMLIT CACHE
# ----------------------------------------
@st.cache_data(show_spinner=False)
def cached_layout_agent(memory_dict):
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

    return run_layout_agent(temp_memory)


# ----------------------------------------
# 🧠 PRIORITIZE LAYOUT ISSUES
# ----------------------------------------
def prioritize_layout_issues(layout_output):

    prompt = f"""
    Prioritize layout issues:

    {layout_output}

    Rank based on severity, EMI risk, and manufacturability.
    """

    return invoke_llm("Layout Issue Prioritizer", prompt)


# ----------------------------------------
# 🔧 OPTIMIZATION ENGINE
# ----------------------------------------
def suggest_layout_optimizations(memory):

    context = memory.get_all()

    prompt = f"""
    Suggest layout optimizations:

    {context}

    Include:
    - Component repositioning
    - Routing improvements
    - EMI reduction
    - Layer restructuring
    """

    return invoke_llm("Layout Optimization Expert", prompt)
    
