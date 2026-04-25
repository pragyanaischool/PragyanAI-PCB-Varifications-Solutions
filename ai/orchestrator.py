import streamlit as st

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

from ai.llm import invoke_llm


# ----------------------------------------
# 🧠 META AGENT (FINAL BRAIN)
# ----------------------------------------
def meta_agent(memory):

    context = memory.get_all()

    prompt = f"""
    You are a Chief PCB Design Engineer.

    Combine all analysis:

    {context}

    Provide:
    - Final summary
    - Critical risks
    - Top 5 issues
    - Recommended fixes
    - Overall score (0-100)

    Return structured JSON.
    """

    return invoke_llm("PCB Chief Engineer", prompt)


# ----------------------------------------
# 🚀 FULL MULTI-AGENT PIPELINE
# ----------------------------------------
def run_full_analysis(image_path, graph_summary, gnn_output, ocr_text):

    memory = PCBMemory()

    # ----------------------------------------
    # 👁️ VISION AGENT
    # ----------------------------------------
    vision = run_vision_agent(image_path)
    memory.update("vision", vision)

    # ----------------------------------------
    # 🔤 OCR AGENT
    # ----------------------------------------
    ocr = run_ocr_agent(ocr_text)
    memory.update("ocr", ocr)

    # ----------------------------------------
    # 🔗 GRAPH DATA
    # ----------------------------------------
    memory.update("graph", graph_summary)

    # ----------------------------------------
    # 🤖 GNN AGENT
    # ----------------------------------------
    gnn = run_gnn_agent(graph_summary, gnn_output)
    memory.update("gnn", gnn)

    # ----------------------------------------
    # ⚡ POWER AGENT
    # ----------------------------------------
    power = run_power_agent(memory)
    memory.update("power", power)

    # ----------------------------------------
    # 🔌 SIGNAL AGENT (uses power)
    # ----------------------------------------
    signal = run_signal_agent(memory)
    memory.update("signal", signal)

    # ----------------------------------------
    # 🌡️ THERMAL AGENT (uses power + layout)
    # ----------------------------------------
    thermal = run_thermal_agent(memory)
    memory.update("thermal", thermal)

    # ----------------------------------------
    # 🧩 LAYOUT AGENT
    # ----------------------------------------
    layout = run_layout_agent(memory)
    memory.update("layout", layout)

    # ----------------------------------------
    # 🔧 TOOL AGENT (FIX ENGINE)
    # ----------------------------------------
    tools = run_tool_agent(memory)
    memory.update("tools", tools)

    # ----------------------------------------
    # 🧠 META AGENT (FINAL SYNTHESIS)
    # ----------------------------------------
    final = meta_agent(memory)

    # ----------------------------------------
    # 📦 FINAL OUTPUT
    # ----------------------------------------
    return {
        "vision": vision,
        "ocr": ocr,
        "gnn": gnn,
        "power": power,
        "signal": signal,
        "thermal": thermal,
        "layout": layout,
        "tools": tools,
        "final": final
    }


# ----------------------------------------
# ⚡ STREAMLIT CACHE (IMPORTANT)
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
# ⚡ QUICK MODE (FAST ANALYSIS)
# ----------------------------------------
def quick_analysis(image_path, graph_summary):

    memory = PCBMemory()

    vision = run_vision_agent(image_path)
    memory.update("vision", vision)

    memory.update("graph", graph_summary)

    quick_prompt = f"""
    Provide quick PCB insights:

    {memory.get_all()}

    Keep it short.
    """

    quick_result = invoke_llm("Quick PCB Analyzer", quick_prompt)

    return {
        "vision": vision,
        "quick_insight": quick_result
    }
    
