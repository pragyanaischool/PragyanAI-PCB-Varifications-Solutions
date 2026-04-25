import json
import re
import streamlit as st

from models.pipeline import PCBPipeline
from ai.llm import invoke_llm, invoke_with_memory


# ----------------------------------------
# 🧠 INIT PIPELINE (CACHED)
# ----------------------------------------
@st.cache_resource
def get_pipeline():
    return PCBPipeline()


# ----------------------------------------
# 🧾 JSON PARSER
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
        "summary": str(text),
        "confidence": 0.5,
        "raw_output": text
    }


# ----------------------------------------
# 👁️ MAIN VISION AGENT
# ----------------------------------------
def run_vision_agent(image_path, structured=True):

    pipeline = get_pipeline()

    # ----------------------------------------
    # 🔍 PERCEPTION LAYER (REAL MODELS)
    # ----------------------------------------
    perception = pipeline.safe_run(image_path)

    components = perception.get("components", [])
    ocr = perception.get("ocr", {})
    segmentation = perception.get("segmentation", {})
    metadata = perception.get("metadata", {})

    # ----------------------------------------
    # 🧠 LLM REASONING
    # ----------------------------------------
    prompt = f"""
    You are a PCB Vision Analysis Expert.

    Analyze the PCB using extracted data:

    Components:
    {components}

    OCR Data:
    {ocr}

    Segmentation:
    {segmentation}

    Metadata:
    {metadata}

    Identify:
    - Component distribution
    - Congestion regions
    - Routing density
    - Missing components
    - Label inconsistencies
    - Visual defects

    Output STRICT JSON:

    {{
        "component_analysis": "...",
        "routing_analysis": "...",
        "issues": [
            {{
                "issue": "...",
                "severity": "High/Medium/Low",
                "location": "...",
                "explanation": "...",
                "confidence": 0.0-1.0
            }}
        ],
        "summary": "...",
        "confidence": 0.0-1.0
    }}
    """

    response = invoke_llm("PCB Vision Expert", prompt)

    if structured:
        reasoning = extract_json(response)
    else:
        reasoning = response

    # ----------------------------------------
    # 📦 FINAL OUTPUT
    # ----------------------------------------
    return {
        "structured": perception,
        "reasoning": reasoning
    }


# ----------------------------------------
# 🔁 FRONT + BACK ANALYSIS
# ----------------------------------------
def analyze_front_back(front_image, back_image):

    front = run_vision_agent(front_image)
    back = run_vision_agent(back_image)

    prompt = f"""
    Compare front and back PCB:

    FRONT:
    {front}

    BACK:
    {back}

    Identify:
    - Missing vias
    - Alignment issues
    - Connectivity problems

    Return JSON.
    """

    response = invoke_llm("PCB Dual Side Analyst", prompt)

    return extract_json(response)


# ----------------------------------------
# ⚡ QUICK VISION CHECK
# ----------------------------------------
def quick_vision_check(image_path):

    pipeline = get_pipeline()

    perception = pipeline.quick_run(image_path)

    prompt = f"""
    Provide quick insights:

    {perception}

    Keep it short.
    """

    return invoke_llm("Quick PCB Vision Checker", prompt)


# ----------------------------------------
# 📊 COMPONENT SUMMARY
# ----------------------------------------
def component_summary(perception):

    components = perception.get("components", [])

    summary = {}

    for comp in components:
        name = comp.get("component", "unknown")
        summary[name] = summary.get(name, 0) + 1

    return summary


# ----------------------------------------
# 🔄 CACHE WRAPPER
# ----------------------------------------
@st.cache_data(show_spinner=False)
def cached_vision_agent(image_path):
    return run_vision_agent(image_path)


# ----------------------------------------
# 🧠 VISUAL ISSUE PRIORITIZATION
# ----------------------------------------
def prioritize_visual_issues(vision_output):

    prompt = f"""
    Prioritize visual PCB issues:

    {vision_output}

    Rank based on severity and risk.
    """

    return invoke_llm("Vision Issue Prioritizer", prompt)


# ----------------------------------------
# 🔧 SUGGEST VISUAL FIXES
# ----------------------------------------
def suggest_visual_fixes(vision_output):

    prompt = f"""
    Suggest fixes based on visual PCB issues:

    {vision_output}

    Include:
    - Placement fixes
    - Routing improvements
    """

    return invoke_llm("PCB Vision Fix Expert", prompt)
    
