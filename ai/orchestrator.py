# ai/orchestrator.py

import streamlit as st
import time

from ai.memory import PCBMemory

# Agents
from ai.agents.vision_agent import run_vision_agent
from ai.agents.ocr_agent import run_ocr_agent
from ai.agents.gnn_agent import run_gnn_agent

from ai.agents.power_agent import run_power_agent
from ai.agents.signal_agent import run_signal_agent
from ai.agents.thermal_agent import run_thermal_agent
from ai.agents.layout_agent import run_layout_agent
from ai.agents.tool_agent import run_tool_agent

# Services
from services.graph import build_graph

# LLM
from ai.llm import invoke_with_memory, extract_json


# ----------------------------------------
# 🧠 SAFE EXECUTION
# ----------------------------------------
def safe_run(step_name, func, *args):
    try:
        start = time.time()
        result = func(*args)
        duration = round(time.time() - start, 2)

        return {
            "data": result,
            "time": duration,
            "error": None
        }

    except Exception as e:
        return {
            "data": None,
            "time": 0,
            "error": f"{step_name} failed: {str(e)}"
        }


# ----------------------------------------
# 🧠 META AGENT
# ----------------------------------------
def meta_agent(memory):

    return extract_json(
        invoke_with_memory(
            memory,
            "You are a Chief PCB Design Engineer.",
            """
            Combine all analysis and provide:
            - Summary
            - Top issues
            - Fixes
            - Score (0-100)

            Return JSON
            """
        )
    )


# ----------------------------------------
# 🚀 MAIN PIPELINE (FIXED)
# ----------------------------------------
def run_full_analysis(
    image_path,
    graph_summary=None,
    graph_summary_input=None,
    gnn_output=None,
    ocr_text=None
):

    # ✅ Normalize input (CRITICAL FIX)
    if graph_summary_input is None:
        graph_summary_input = graph_summary

    memory = PCBMemory()

    debug = {}
    timings = {}

    # ----------------------------------------
    # 👁️ VISION
    # ----------------------------------------
    vision = safe_run("vision", run_vision_agent, image_path)
    memory.update("vision", vision["data"])
    debug["vision"] = vision
    timings["vision"] = vision["time"]

    # ----------------------------------------
    # 🔤 OCR
    # ----------------------------------------
    ocr = safe_run("ocr", run_ocr_agent, ocr_text, image_path)
    memory.update("ocr", ocr["data"])
    debug["ocr"] = ocr
    timings["ocr"] = ocr["time"]

    # ----------------------------------------
    # 🔗 GRAPH
    # ----------------------------------------
    if graph_summary_input:
        memory.update("graph", graph_summary_input)
    else:
        graph = safe_run("graph", build_graph,
                         memory.get("vision"),
                         memory.get("ocr"))
        memory.update("graph", graph["data"])
        debug["graph"] = graph
        timings["graph"] = graph["time"]

    # ----------------------------------------
    # 🤖 GNN
    # ----------------------------------------
    gnn = safe_run("gnn", run_gnn_agent,
                   memory.get("graph"),
                   gnn_output)
    memory.update("gnn", gnn["data"])
    debug["gnn"] = gnn
    timings["gnn"] = gnn["time"]

    # ----------------------------------------
    # ⚡ DOMAIN AGENTS
    # ----------------------------------------
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

    # ----------------------------------------
    # 🔧 TOOL
    # ----------------------------------------
    tools = safe_run("tools", run_tool_agent, memory)
    memory.update("tools", tools["data"])
    debug["tools"] = tools
    timings["tools"] = tools["time"]

    # ----------------------------------------
    # 🧠 FINAL
    # ----------------------------------------
    final = safe_run("meta", meta_agent, memory)

    return {
        "vision": memory.get("vision"),
        "ocr": memory.get("ocr"),
        "graph": memory.get("graph"),
        "gnn": memory.get("gnn"),
        "power": memory.get("power"),
        "signal": memory.get("signal"),
        "thermal": memory.get("thermal"),
        "layout": memory.get("layout"),
        "tools": memory.get("tools"),
        "final": final["data"],
        "debug": debug,
        "timings": timings
    }


# ----------------------------------------
# ⚡ CACHE
# ----------------------------------------
@st.cache_data
def cached_full_analysis(image_path, graph_summary, gnn_output, ocr_text):
    return run_full_analysis(
        image_path=image_path,
        graph_summary=graph_summary,
        gnn_output=gnn_output,
        ocr_text=ocr_text
    )
