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

# LLM
from ai.llm import invoke_llm, invoke_with_memory, extract_json


# ----------------------------------------
# 🧠 SAFE EXECUTION WRAPPER
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
# 🧠 META AGENT (FINAL BRAIN)
# ----------------------------------------
def meta_agent(memory):

    return extract_json(
        invoke_with_memory(
            memory,
            "You are a Chief PCB Design Engineer.",
            """
            Combine all analysis and provide:

            - Final summary
            - Critical risks
            - Top 5 issues
            - Recommended fixes
            - Overall score (0-100)

            Return structured JSON.
            """
        )
    )


# ----------------------------------------
# 🚀 FULL MULTI-AGENT PIPELINE
# ----------------------------------------
def run_full_analysis(image_path, graph_summary=None, gnn_output=None, ocr_text=None):

    memory = PCBMemory()
    debug_log = {}

    # ----------------------------------------
    # 👁️ VISION AGENT
    # ----------------------------------------
    vision_res = safe_run("vision", run_vision_agent, image_path)
    memory.update("vision", vision_res["data"])
    debug_log["vision"] = vision_res

    # ----------------------------------------
    # 🔤 OCR AGENT
    # ----------------------------------------
    if ocr_text:
        ocr_res = safe_run("ocr", run_ocr_agent, ocr_text)
        memory.update("ocr", ocr_res["data"])
        debug_log["ocr"] = ocr_res

    # ----------------------------------------
    # 🔗 GRAPH DATA
    # ----------------------------------------
    if graph_summary:
        memory.update("graph", graph_summary)

    # ----------------------------------------
    # 🤖 GNN AGENT
    # ----------------------------------------
    if graph_summary:
        gnn_res = safe_run("gnn", run_gnn_agent, graph_summary, gnn_output)
        memory.update("gnn", gnn_res["data"])
        debug_log["gnn"] = gnn_res

    # ----------------------------------------
    # ⚡ POWER AGENT
    # ----------------------------------------
    power_res = safe_run("power", run_power_agent, memory)
    memory.update("power", power_res["data"])
    debug_log["power"] = power_res

    # ----------------------------------------
    # 🔌 SIGNAL AGENT
    # ----------------------------------------
    signal_res = safe_run("signal", run_signal_agent, memory)
    memory.update("signal", signal_res["data"])
    debug_log["signal"] = signal_res

    # ----------------------------------------
    # 🌡️ THERMAL AGENT
    # ----------------------------------------
    thermal_res = safe_run("thermal", run_thermal_agent, memory)
    memory.update("thermal", thermal_res["data"])
    debug_log["thermal"] = thermal_res

    # ----------------------------------------
    # 🧩 LAYOUT AGENT
    # ----------------------------------------
    layout_res = safe_run("layout", run_layout_agent, memory)
    memory.update("layout", layout_res["data"])
    debug_log["layout"] = layout_res

    # ----------------------------------------
    # 🔧 TOOL AGENT
    # ----------------------------------------
    tools_res = safe_run("tools", run_tool_agent, memory)
    memory.update("tools", tools_res["data"])
    debug_log["tools"] = tools_res

    # ----------------------------------------
    # 🧠 META AGENT
    # ----------------------------------------
    final_res = safe_run("meta", meta_agent, memory)
    debug_log["meta"] = final_res

    # ----------------------------------------
    # 📦 FINAL OUTPUT
    # ----------------------------------------
    return {
        "results": {
            "vision": memory.get("vision"),
            "ocr": memory.get("ocr"),
            "gnn": memory.get("gnn"),
            "power": memory.get("power"),
            "signal": memory.get("signal"),
            "thermal": memory.get("thermal"),
            "layout": memory.get("layout"),
            "tools": memory.get("tools"),
            "final": final_res["data"]
        },
        "debug": debug_log,
        "memory_summary": memory.summary()
    }


# ----------------------------------------
# ⚡ STREAMLIT CACHE
# ----------------------------------------
@st.cache_data(show_spinner=True)
def cached_full_analysis(image_path, graph_summary, gnn_output, ocr_text):

    return run_full_analysis(
        image_path=image_path,
        graph_summary=graph_summary,
        gnn_output=gnn_output,
        ocr_text=ocr_text
    )


# ----------------------------------------
# ⚡ QUICK MODE
# ----------------------------------------
def quick_analysis(image_path, graph_summary=None):

    memory = PCBMemory()

    vision = run_vision_agent(image_path)
    memory.update("vision", vision)

    if graph_summary:
        memory.update("graph", graph_summary)

    quick_result = invoke_with_memory(
        memory,
        "Quick PCB Analyzer",
        "Provide short actionable insights."
    )

    return {
        "vision": vision,
        "quick_insight": quick_result
    }


# ----------------------------------------
# 💬 CHAT MODE
# ----------------------------------------
def chat_with_system(memory, user_query):

    return invoke_with_memory(
        memory,
        "PCB AI Assistant",
        f"User query: {user_query}"
    )
    
