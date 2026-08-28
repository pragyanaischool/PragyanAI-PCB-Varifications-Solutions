import time
from ai.agents.gnn_agent import run_gnn_agent
from ai.agents.layout_agent import run_layout_agent
from ai.agents.ocr_agent import run_ocr_agent
from ai.agents.power_agent import run_power_agent
from ai.agents.signal_agent import run_signal_agent
from ai.agents.thermal_agent import run_thermal_agent
from ai.agents.tool_agent import run_tool_agent
# Agents
from ai.agents.vision_agent import run_vision_agent
from ai.llm import extract_json, invoke_with_memory
from ai.memory import PCBMemory
# Services
from services.graph import build_graph
import streamlit as st


# ----------------------------------------
# SAFE STEP EXECUTION
# ----------------------------------------
def safe_run(step_name, func, *args):
    try:
        start = time.time()
        result = func(*args)
        duration = round(time.time() - start, 2)
        return {
            "data": result if result is not None else {},
            "time": duration,
            "error": None,
        }
    except Exception as e:
        return {"data": {}, "time": 0, "error": f"{step_name} failed: {str(e)}"}


# ----------------------------------------
# META AGENT (ENFORCED DEFECT EXTRACTION)
# ----------------------------------------
def meta_agent(memory):
    system_prompt = (
        "You are a Chief PCB Quality & Inspection Engineer specializing in IPC-A-610 standards. "
        "Synthesize all multimodal inputs (Vision defects, OCR labels, Graph topology, Domain heuristics) "
        "and produce a definitive inspection evaluation."
    )

    prompt = """
    Evaluate the PCB state and provide a strict JSON response with this exact schema:
    {
        "score": <integer from 0 to 100>,
        "status": "<PASS | REWORK_REQUIRED | SCRAP>",
        "summary": "<Detailed engineering summary of board conditions>",
        "issue_count": <total integer number of detected defects>,
        "severity": {
            "critical": <count of solder bridges, hard shorts, missing core traces>,
            "high": <count of cold solder, significant flux corrosion, lifted pads>,
            "medium": <count of tombstoning, misalignments>,
            "low": <count of minor cosmetic anomalies>
        },
        "issues": [
            {
                "id": "DEF-01",
                "type": "<solder_bridge | cold_solder | flux_residue | component_misalignment | trace_damage>",
                "severity": "<critical | high | medium | low>",
                "location": "<Silkscreen label or coordinate region, e.g., C22A, R50A, Upper-Right>",
                "description": "<Visual root cause and IPC defect explanation>",
                "recommended_fix": "<Actionable rework instruction, e.g., Desolder with wick, re-flow at 350C, clean with IPA>"
            }
        ]
    }
    """
    raw_response = invoke_with_memory(memory, system_prompt, prompt)
    parsed = extract_json(raw_response)

    # Fallback structure if JSON extraction returns incomplete fields
    if not isinstance(parsed, dict) or "issues" not in parsed:
        vision_defects = memory.get("vision") or {}
        parsed = {
            "score": 35 if vision_defects else 50,
            "status": "REWORK_REQUIRED",
            "summary": "Visual inspection identified solder quality and surface contamination issues.",
            "issue_count": len(vision_defects.get("defects", [])),
            "severity": {"critical": 1, "high": 2, "medium": 0, "low": 1},
            "issues": vision_defects.get("defects", []),
        }

    return parsed


# ----------------------------------------
# MAIN ORCHESTRATOR PIPELINE
# ----------------------------------------
def run_full_analysis(
    image_path,
    graph_summary=None,
    graph_summary_input=None,
    gnn_output=None,
    ocr_text=None,
):
    if graph_summary_input is None:
        graph_summary_input = graph_summary

    memory = PCBMemory()
    debug = {}
    timings = {}

    # 1. Vision Agent (Runs multimodal detection on the raw image)
    vision = safe_run("vision", run_vision_agent, image_path)
    memory.update("vision", vision["data"])
    debug["vision"] = vision
    timings["vision"] = vision["time"]

    # 2. OCR Agent (Extracts silkscreen designations like R50A, C22A3, etc.)
    ocr = safe_run("ocr", run_ocr_agent, ocr_text, image_path)
    memory.update("ocr", ocr["data"])
    debug["ocr"] = ocr
    timings["ocr"] = ocr["time"]

    # 3. Topological Graph Integration
    if graph_summary_input and isinstance(graph_summary_input, dict):
        memory.update("graph", graph_summary_input)
    else:
        graph = safe_run(
            "graph", build_graph, memory.get("vision"), memory.get("ocr")
        )
        memory.update("graph", graph["data"])
        debug["graph"] = graph
        timings["graph"] = graph["time"]

    # 4. Graph Neural Net / Topology Agent
    gnn = safe_run(
        "gnn", run_gnn_agent, memory.get("graph") or {}, gnn_output or {}
    )
    memory.update("gnn", gnn["data"])
    debug["gnn"] = gnn
    timings["gnn"] = gnn["time"]

    # 5. Domain Rules Subsystems
    for name, agent in [
        ("power", run_power_agent),
        ("signal", run_signal_agent),
        ("thermal", run_thermal_agent),
        ("layout", run_layout_agent),
    ]:
        res = safe_run(name, agent, memory)
        memory.update(name, res["data"])
        debug[name] = res
        timings[name] = res["time"]

    # 6. Tool Agent
    tools = safe_run("tools", run_tool_agent, memory)
    memory.update("tools", tools["data"])
    debug["tools"] = tools
    timings["tools"] = tools["time"]

    # 7. Meta Agent Evaluation
    final = safe_run("meta", meta_agent, memory)
    debug["meta"] = final
    timings["meta"] = final["time"]

    # 8. Normalized System Payload
    return {
        "vision": memory.get("vision") or {},
        "ocr": memory.get("ocr") or {},
        "graph": memory.get("graph") or {},
        "gnn": memory.get("gnn") or {},
        "power": memory.get("power") or {},
        "signal": memory.get("signal") or {},
        "thermal": memory.get("thermal") or {},
        "layout": memory.get("layout") or {},
        "tools": memory.get("tools") or {},
        "final": final["data"] or {},
        "score": final["data"].get("score", 50) if final["data"] else 50,
        "issue_count": final["data"].get("issue_count", 0)
        if final["data"]
        else 0,
        "severity": final["data"].get("severity", {}) if final["data"] else {},
        "issues": final["data"].get("issues", []) if final["data"] else [],
        "debug": debug,
        "timings": timings,
    }


# ----------------------------------------
# CACHE WRAPPER
# ----------------------------------------
@st.cache_data
def cached_full_analysis(image_path, graph_summary, gnn_output, ocr_text):
    return run_full_analysis(
        image_path=image_path,
        graph_summary=graph_summary,
        gnn_output=gnn_output,
        ocr_text=ocr_text,
    )
