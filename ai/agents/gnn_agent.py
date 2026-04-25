import json
import re
import streamlit as st

from ai.llm import invoke_llm, invoke_with_memory


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
        "summary": str(text),
        "confidence": 0.5,
        "raw_output": text
    }


# ----------------------------------------
# 🤖 MAIN GNN AGENT
# ----------------------------------------
def run_gnn_agent(graph_data, gnn_output=None, memory=None, structured=True):

    # Optional memory context
    context = memory.get_all() if memory else {}

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    prompt = f"""
    You are a PCB Graph Analysis Expert.

    Analyze PCB connectivity graph:

    Nodes:
    {nodes}

    Edges:
    {edges}

    Additional Context:
    {context}

    Detect:
    - Broken connections
    - Missing nets
    - Abnormal topology
    - Over-connected nodes
    - Isolated components
    - Signal flow issues

    Output STRICT JSON:

    {{
        "graph_issues": [
            {{
                "issue": "...",
                "severity": "High/Medium/Low",
                "explanation": "...",
                "affected_nodes": [...],
                "fix": "...",
                "confidence": 0.0-1.0
            }}
        ],
        "summary": "...",
        "confidence": 0.0-1.0
    }}
    """

    if memory:
        response = invoke_with_memory(
            memory,
            "PCB Graph Expert",
            prompt
        )
    else:
        response = invoke_llm("PCB Graph Expert", prompt)

    if structured:
        return extract_json(response)

    return response


# ----------------------------------------
# 🔍 ADVANCED GRAPH ANALYSIS
# ----------------------------------------
def advanced_gnn_analysis(graph_data, memory=None):

    prompt = f"""
    Perform deep graph-based PCB analysis:

    {graph_data}

    Evaluate:
    - Graph connectivity quality
    - Node centrality
    - Signal paths
    - Bottlenecks
    - Redundant connections

    Return JSON:
    {{
        "connectivity_score": "...",
        "critical_nodes": [...],
        "bottlenecks": [...],
        "issues": [...],
        "recommendations": [...],
        "confidence": 0.0-1.0
    }}
    """

    if memory:
        response = invoke_with_memory(
            memory,
            "Advanced Graph Analyst",
            prompt
        )
    else:
        response = invoke_llm("Advanced Graph Analyst", prompt)

    return extract_json(response)


# ----------------------------------------
# 📊 GRAPH SCORE
# ----------------------------------------
def graph_score(graph_data, memory=None):

    prompt = f"""
    Evaluate PCB graph quality score (0-100):

    {graph_data}

    Consider:
    - Connectivity
    - Redundancy
    - Signal flow
    - Structural integrity

    Return JSON.
    """

    if memory:
        response = invoke_with_memory(
            memory,
            "Graph Evaluator",
            prompt
        )
    else:
        response = invoke_llm("Graph Evaluator", prompt)

    return extract_json(response)


# ----------------------------------------
# ⚡ QUICK GRAPH CHECK
# ----------------------------------------
def quick_graph_check(graph_data):

    return invoke_llm(
        "Quick Graph Checker",
        f"List major graph issues:\n{graph_data}"
    )


# ----------------------------------------
# 🔄 CACHE WRAPPER
# ----------------------------------------
@st.cache_data(show_spinner=False)
def cached_gnn_agent(graph_data):

    return run_gnn_agent(graph_data)


# ----------------------------------------
# 🧠 PRIORITIZATION
# ----------------------------------------
def prioritize_graph_issues(graph_output):

    prompt = f"""
    Prioritize graph issues:

    {graph_output}

    Rank based on:
    - Connectivity risk
    - Impact on signal flow
    """

    return invoke_llm("Graph Issue Prioritizer", prompt)


# ----------------------------------------
# 🔧 FIX SUGGESTION ENGINE
# ----------------------------------------
def suggest_graph_fixes(graph_data, memory=None):

    prompt = f"""
    Suggest fixes for PCB connectivity issues:

    {graph_data}

    Include:
    - Reconnecting nets
    - Removing redundant paths
    - Improving topology
    """

    if memory:
        return invoke_with_memory(
            memory,
            "Graph Fix Expert",
            prompt
        )

    return invoke_llm("Graph Fix Expert", prompt)


# ----------------------------------------
# 🔬 SIMULATION (AI-BASED)
# ----------------------------------------
def simulate_graph_improvement(graph_data, memory=None):

    prompt = f"""
    Simulate improvements after fixing graph issues:

    {graph_data}

    Predict:
    - Better connectivity
    - Improved signal flow
    - Reduced failure risk
    """

    if memory:
        return invoke_with_memory(
            memory,
            "Graph Simulation Expert",
            prompt
        )

    return invoke_llm("Graph Simulation Expert", prompt)
    
