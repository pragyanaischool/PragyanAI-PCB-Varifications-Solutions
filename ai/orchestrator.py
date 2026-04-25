import streamlit as st

from ai.memory import PCBMemory

# Agents
from ai.agents.vision_agent import run_vision_agent
from ai.agents.power_agent import run_power_agent
from ai.agents.signal_agent import run_signal_agent
from ai.agents.thermal_agent import run_thermal_agent
from ai.agents.layout_agent import run_layout_agent
from ai.agents.gnn_agent import run_gnn_agent
from ai.agents.ocr_agent import run_ocr_agent

from ai.llm import invoke_llm


# ----------------------------------------
# 🚀 MULTI-AGENT PIPELINE
# ----------------------------------------
def run_full_analysis(image_path, graph_summary, gnn_output, ocr_text):

    memory = PCBMemory()

    # ----------------------------------------
    # 👁️ Vision Agent
    # ----------------------------------------
    vision = run_vision_agent(image_path)
    memory.update("vision", vision)

    # ----------------------------------------
    # 🔤 OCR Agent
    # ----------------------------------------
    ocr = run_ocr_agent(ocr_text)
    memory.update("ocr", ocr)

    # ----------------------------------------
    # 🔗 Graph
    # ----------------------------------------
    memory.update("graph", graph_summary)

    # ----------------------------------------
    # 🤖 GNN Agent
    # ----------------------------------------
    gnn = run_gnn_agent(graph_summary, gnn_output)
    memory.update("gnn", gnn)

    # ----------------------------------------
    # ⚡ Power Agent
    # ----------------------------------------
    power = run_power_agent(memory)
    memory.update("power", power)

    # ----------------------------------------
    # 🔌 Signal Agent (uses power)
    # ----------------------------------------
    signal = run_signal_agent(memory)
    memory.update("signal", signal)

    # ----------------------------------------
    # 🌡️ Thermal Agent (uses power + layout)
    # ----------------------------------------
    thermal = run_thermal_agent(memory)
    memory.update("thermal", thermal)

    # ----------------------------------------
    # 🧩 Layout Agent
    # ----------------------------------------
    layout = run_layout_agent(memory)
    memory.update("layout", layout)

    # ----------------------------------------
    # 🧠 FINAL META AGENT
    # ----------------------------------------
    final = meta_agent(memory)

    return {
        "vision": vision,
        "ocr": ocr,
        "gnn": gnn,
        "power": power,
        "signal": signal,
        "thermal": thermal,
        "layout": layout,
        "final": final
    }


# ----------------------------------------
# 🧠 META AGENT (FINAL BRAIN)
# ----------------------------------------
def meta_agent(memory):

    context = memory.get_all()

    prompt = f"""
    You are a senior PCB design expert.

    Combine all analysis:

    {context}

    Provide:
    - Final summary
    - Critical risks
    - Top 5 issues
    - Actionable fixes
    - Overall score (0-100)
    """

    return invoke_llm("You are expert PCB engineer", prompt)
    
