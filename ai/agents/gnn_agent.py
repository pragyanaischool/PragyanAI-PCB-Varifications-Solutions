import json
import re
import streamlit as st

from ai.llm import invoke_llm, invoke_with_memory


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
        "issues": [],
        "summary": str(text),
        "confidence": 0.5,
        "raw_output": text
    }


# ----------------------------------------
# 🔍 GRAPH VALIDATION
# ----------------------------------------
def validate_graph(graph_data):

    if not isinstance(graph_data, dict):
        return False, "Invalid graph format"

    if "nodes" not in graph_data or "edges" not in graph_data:
        return False, "Missing nodes/edges"

    return True, "Valid graph"


# ----------------------------------------
# 📊 GRAPH FEATURES (LIGHT GNN)
# ----------------------------------------
def compute_graph_features(graph_data):

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    node_degree = {n: 0 for n in nodes}

    for e in edges:
        if len(e) >= 2:
            node_degree[e[0]] = node_degree.get(e[0], 0) + 1
            node_degree[e[1]] = node_degree.get(e[1], 0) + 1

    isolated_nodes = [n for n, d in node_degree.items() if d == 0]
    high_degree_nodes = [n for n, d in node_degree.items() if d > 5]

    return {
        "num_nodes": len(nodes),
        "num_edges": len(edges),
        "isolated_nodes": isolated_nodes,
        "high_degree_nodes": high_degree_nodes,
        "avg_degree": sum(node_degree.values()) / (len(nodes) + 1)
    }


# ----------------------------------------
# 🤖 MAIN GNN AGENT
# ----------------------------------------
def run_gnn_agent(graph_data, gnn_output=None, memory=None, structured=True):

    valid, msg = validate_graph(graph_data)

    if not valid:
        return {"error": msg}

    # ----------------------------------------
    # 🧠 GRAPH FEATURES
    # ----------------------------------------
    features = compute_graph_features(graph_data)

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    # ----------------------------------------
    # 🧠 PROMPT
    # ----------------------------------------
    prompt = f"""
    You are a PCB Graph + GNN Expert.

    Graph:
    Nodes: {nodes}
    Edges: {edges}

    Computed Features:
    {features}

    External GNN Output:
    {gnn_output}

    Detect:
    - Broken connections
    - Missing nets
    - Isolated components
    - Over-connected nodes
    - Signal flow issues

    Return STRICT JSON:
    {{
        "issues": [
            {{
                "issue": "...",
                "severity": "High/Medium/Low",
                "affected_nodes": [...],
                "explanation": "...",
                "fix": "...",
                "confidence": 0.0-1.0
            }}
        ],
        "summary": "...",
        "confidence": 0.0-1.0
    }}
    """

    # ----------------------------------------
    # 🧠 LLM CALL
    # ----------------------------------------
    if memory:
        response = invoke_with_memory(memory, "PCB Graph Expert", prompt)
    else:
        response = invoke_llm("PCB Graph Expert", prompt)
        response = response.get("content", response)

    result = extract_json(response)

    # ----------------------------------------
    # 🧠 FALLBACK (NO LLM)
    # ----------------------------------------
    if not result.get("issues"):
        if features["isolated_nodes"]:
            result["issues"] = [{
                "issue": "Isolated components detected",
                "severity": "High",
                "affected_nodes": features["isolated_nodes"],
                "explanation": "Components not connected",
                "fix": "Check routing",
                "confidence": 0.8
            }]

    return result


# ----------------------------------------
# 🔍 ADVANCED ANALYSIS
# ----------------------------------------
def advanced_gnn_analysis(graph_data, memory=None):

    features = compute_graph_features(graph_data)

    prompt = f"""
    Perform deep PCB graph analysis:

    {graph_data}

    Features:
    {features}

    Evaluate:
    - Connectivity quality
    - Bottlenecks
    - Signal paths

    Return JSON.
    """

    if memory:
        response = invoke_with_memory(memory, "Advanced Graph Analyst", prompt)
    else:
        response = invoke_llm("Advanced Graph Analyst", prompt)
        response = response.get("content", response)

    return extract_json(response)


# ----------------------------------------
# 📊 GRAPH SCORE
# ----------------------------------------
def graph_score(graph_data, memory=None):

    features = compute_graph_features(graph_data)

    prompt = f"""
    Score PCB graph (0-100):

    {graph_data}

    Features:
    {features}
    """

    if memory:
        response = invoke_with_memory(memory, "Graph Evaluator", prompt)
    else:
        response = invoke_llm("Graph Evaluator", prompt)
        response = response.get("content", response)

    return extract_json(response)


# ----------------------------------------
# ⚡ QUICK CHECK
# ----------------------------------------
def quick_graph_check(graph_data):

    response = invoke_llm(
        "Quick Graph Checker",
        f"List major issues:\n{graph_data}"
    )

    return response.get("content", response)


# ----------------------------------------
# 🔄 CACHE
# ----------------------------------------
@st.cache_data(show_spinner=False)
def cached_gnn_agent(graph_data):
    return run_gnn_agent(graph_data)


# ----------------------------------------
# 🧠 PRIORITIZATION
# ----------------------------------------
def prioritize_graph_issues(graph_output):

    response = invoke_llm(
        "Graph Issue Prioritizer",
        f"Prioritize issues:\n{graph_output}"
    )

    return response.get("content", response)


# ----------------------------------------
# 🔧 FIX ENGINE
# ----------------------------------------
def suggest_graph_fixes(graph_data, memory=None):

    prompt = f"""
    Suggest fixes:

    {graph_data}

    Improve:
    - Connectivity
    - Signal flow
    """

    if memory:
        return invoke_with_memory(memory, "Graph Fix Expert", prompt)

    response = invoke_llm("Graph Fix Expert", prompt)
    return response.get("content", response)


# ----------------------------------------
# 🔬 SIMULATION
# ----------------------------------------
def simulate_graph_improvement(graph_data, memory=None):

    prompt = f"""
    Simulate improvements:

    {graph_data}

    Predict:
    - Better connectivity
    - Reduced failure
    """

    if memory:
        return invoke_with_memory(memory, "Graph Simulation Expert", prompt)

    response = invoke_llm("Graph Simulation Expert", prompt)
    return response.get("content", response)
    
