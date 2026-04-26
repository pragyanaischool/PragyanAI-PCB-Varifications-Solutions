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
            Combine all analysis:

            Provide:
            - Final summary
            - Top issues
            - Recommended fixes
            - Overall score (0-100)

            Return JSON.
            """
        )
    )


# ----------------------------------------
# 🚀 FULL PIPELINE (FIXED)
# ----------------------------------------
def run_full_analysis(
    image_path,
    graph_summary_input=None,
    gnn_output=None,
    ocr_text=None
):

    memory = PCBMemory()
    debug_log = {}
    timings = {}

    # ----------------------------------------
    # 👁️ VISION
    # ----------------------------------------
    vision_res = safe_run("vision", run_vision_agent, image_path)
    memory.update("vision", vision_res["data"])
    debug_log["vision"] = vision_res
    timings["vision"] = vision_res["time"]

    # ----------------------------------------
    # 🔤 OCR
    # ----------------------------------------
    if ocr_text:
        ocr_res = safe_run("ocr", run_ocr_agent, ocr_text)
    else:
        ocr_res = safe_run("ocr", run_ocr_agent, None, image_path)

    memory.update("ocr", ocr_res["data"])
    debug_log["ocr"] = ocr_res
    timings["ocr"] = ocr_res["time"]

    # ----------------------------------------
    # 🔗 GRAPH (USE EXTERNAL IF PROVIDED)
    # ----------------------------------------
    if graph_summary_input:
        memory.update("graph", graph_summary_input)

        debug_log["graph"] = {
            "data": graph_summary_input,
            "time": 0,
            "error": None
        }
        timings["graph"] = 0

    else:
        graph_res = safe_run(
            "graph",
            build_graph,
            memory.get("vision"),
            memory.get("ocr")
        )

        memory.update("graph", graph_res["data"])
        debug_log["graph"] = graph_res
        timings["graph"] = graph_res["time"]

    # ----------------------------------------
    # 🤖 GNN
    # ----------------------------------------
    try:
        gnn_res = safe_run(
            "gnn",
            run_gnn_agent,
            memory.get("graph"),
            gnn_output
        )
    except:
        gnn_res = {"data": {}, "time": 0, "error": "GNN skipped"}

    memory.update("gnn", gnn_res["data"])
    debug_log["gnn"] = gnn_res
    timings["gnn"] = gnn_res["time"]

    # ----------------------------------------
    # ⚡ POWER
    # ----------------------------------------
    power_res = safe_run("power", run_power_agent, memory)
    memory.update("power", power_res["data"])
    debug_log["power"] = power_res
    timings["power"] = power_res["time"]

    # ----------------------------------------
    # 🔌 SIGNAL
    # ----------------------------------------
    signal_res = safe_run("signal", run_signal_agent, memory)
    memory.update("signal", signal_res["data"])
    debug_log["signal"] = signal_res
    timings["signal"] = signal_res["time"]

    # ----------------------------------------
    # 🌡️ THERMAL
    # ----------------------------------------
    thermal_res = safe_run("thermal", run_thermal_agent, memory)
    memory.update("thermal", thermal_res["data"])
    debug_log["thermal"] = thermal_res
    timings["thermal"] = thermal_res["time"]

    # ----------------------------------------
    # 🧩 LAYOUT
    # ----------------------------------------
    layout_res = safe_run("layout", run_layout_agent, memory)
    memory.update("layout", layout_res["data"])
    debug_log["layout"] = layout_res
    timings["layout"] = layout_res["time"]

    # ----------------------------------------
    # 🔧 TOOL
    # ----------------------------------------
    tools_res = safe_run("tools", run_tool_agent, memory)
    memory.update("tools", tools_res["data"])
    debug_log["tools"] = tools_res
    timings["tools"] = tools_res["time"]

    # ----------------------------------------
    # 🧠 META
    # ----------------------------------------
    meta_res = safe_run("meta", meta_agent, memory)
    debug_log["meta"] = meta_res
    timings["meta"] = meta_res["time"]

    # ----------------------------------------
    # 📦 FINAL OUTPUT (FLAT STRUCTURE)
    # ----------------------------------------
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
        "final": meta_res["data"],

        # Debug
        "debug": debug_log,
        "timings": timings,
        "memory_summary": memory.summary()
    }


# ----------------------------------------
# ⚡ CACHE (FIXED SIGNATURE)
# ----------------------------------------
@st.cache_data(show_spinner=True)
def cached_full_analysis(image_path, graph_summary_input, gnn_output, ocr_text):

    return run_full_analysis(
        image_path=image_path,
        graph_summary_input=graph_summary_input,
        gnn_output=gnn_output,
        ocr_text=ocr_text
    )
