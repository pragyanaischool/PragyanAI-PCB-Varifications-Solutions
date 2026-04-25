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
        "summary": str(text),
        "issues": [],
        "confidence": 0.5,
        "raw_output": text
    }


# ----------------------------------------
# 📍 NORMALIZE LOCATION (FOR UI)
# ----------------------------------------
def normalize_locations(issues):

    for issue in issues:
        loc = issue.get("location")

        # Ensure bbox format [x1, y1, x2, y2]
        if isinstance(loc, str):
            issue["location"] = None

    return issues


# ----------------------------------------
# 👁️ MAIN VISION AGENT
# ----------------------------------------
def run_vision_agent(image_path, memory=None, structured=True):

    pipeline = get_pipeline()

    # ----------------------------------------
    # 🔍 PERCEPTION (SAFE)
    # ----------------------------------------
    try:
        perception = pipeline.safe_run(image_path)
    except Exception as e:
        return {
            "structured": {},
            "reasoning": {"error": str(e)}
        }

    components = perception.get("components", [])
    ocr = perception.get("ocr", {})
    segmentation = perception.get("segmentation", {})
    metadata = perception.get("metadata", {})

    # ----------------------------------------
    # 🧠 LLM REASONING
    # ----------------------------------------
    prompt = f"""
    You are a PCB Vision Analysis Expert.

    Analyze the PCB:

    Components:
    {components}

    OCR:
    {ocr}

    Segmentation:
    {segmentation}

    Identify:
    - Component distribution
    - Routing density
    - Missing components
    - Label inconsistencies
    - Visual defects

    Return STRICT JSON:
    {{
        "component_analysis": "...",
        "routing_analysis": "...",
        "issues": [
            {{
                "issue": "...",
                "severity": "High/Medium/Low",
                "location": [x1,y1,x2,y2],
                "explanation": "...",
                "confidence": 0.0-1.0
            }}
        ],
        "summary": "...",
        "confidence": 0.0-1.0
    }}
    """

    # ----------------------------------------
    # 🧠 MEMORY-AWARE CALL
    # ----------------------------------------
    if memory:
        response = invoke_with_memory(memory, "PCB Vision Expert", prompt)
    else:
        response = invoke_llm("PCB Vision Expert", prompt)
        response = response.get("content", response)

    reasoning = extract_json(response)

    # Normalize locations
    if "issues" in reasoning:
        reasoning["issues"] = normalize_locations(reasoning["issues"])

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
    Compare PCB front and back:

    FRONT:
    {front}

    BACK:
    {back}

    Detect:
    - Missing vias
    - Misalignment
    - Connectivity gaps

    Return JSON.
    """

    response = invoke_llm("PCB Dual Side Analyst", prompt)
    return extract_json(response.get("content", response))


# ----------------------------------------
# ⚡ QUICK VISION CHECK
# ----------------------------------------
def quick_vision_check(image_path):

    pipeline = get_pipeline()

    try:
        perception = pipeline.quick_run(image_path)
    except:
        return "Quick vision failed"

    prompt = f"""
    Provide quick PCB insights:

    {perception}

    Keep it concise.
    """

    response = invoke_llm("Quick PCB Vision Checker", prompt)
    return response.get("content", response)


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
# 🧠 ISSUE PRIORITIZATION
# ----------------------------------------
def prioritize_visual_issues(vision_output):

    prompt = f"""
    Prioritize PCB issues:

    {vision_output}

    Rank by severity and impact.
    """

    response = invoke_llm("Vision Issue Prioritizer", prompt)
    return response.get("content", response)


# ----------------------------------------
# 🔧 FIX SUGGESTIONS
# ----------------------------------------
def suggest_visual_fixes(vision_output):

    prompt = f"""
    Suggest PCB fixes:

    {vision_output}

    Include:
    - Placement fixes
    - Routing improvements
    """

    response = invoke_llm("PCB Vision Fix Expert", prompt)
    return response.get("content", response)
    
