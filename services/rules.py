# services/rules.py

"""
Enhanced PCB Rule Engine (Production Version)

✔ Accepts dict OR networkx graph
✔ Safe execution (no crashes)
✔ PCB-aware checks
✔ Connectivity + reliability + congestion
"""

from typing import List, Dict
import networkx as nx


# ----------------------------------------
# 🔁 GRAPH NORMALIZER (CRITICAL FIX)
# ----------------------------------------
def ensure_graph(graph):

    if isinstance(graph, nx.Graph):
        return graph

    if isinstance(graph, dict):

        G = nx.Graph()

        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        try:
            G.add_nodes_from(nodes)
            G.add_edges_from(edges)
        except:
            return None

        return G

    return None


# ----------------------------------------
# 🚀 MAIN RULE ENGINE
# ----------------------------------------
def run_rules(graph_input) -> List[Dict]:

    graph = ensure_graph(graph_input)

    if graph is None or graph.number_of_nodes() == 0:
        return [{
            "category": "Input",
            "issue": "Empty or Invalid Graph",
            "severity": "High",
            "explanation": "Graph data missing or invalid",
            "fix": "Check pipeline / parser"
        }]

    issues = []

    issues += check_floating_components(graph)
    issues += check_high_degree_nodes(graph)
    issues += check_isolated_clusters(graph)
    issues += check_critical_nodes(graph)
    issues += check_sparse_connectivity(graph)
    issues += check_bridge_edges(graph)
    issues += check_cycle_loops(graph)
    issues += check_dense_regions(graph)

    return issues


# ----------------------------------------
# ⚠️ FLOATING COMPONENTS
# ----------------------------------------
def check_floating_components(graph: nx.Graph):

    issues = []

    for node in graph.nodes:
        if graph.degree[node] == 0:
            issues.append({
                "category": "Connectivity",
                "issue": "Floating Component",
                "node": node,
                "severity": "High",
                "explanation": "Component is not connected",
                "fix": "Ensure proper net connection"
            })

    return issues


# ----------------------------------------
# 🔥 HIGH DEGREE NODES
# ----------------------------------------
def check_high_degree_nodes(graph: nx.Graph, threshold: int = 6):

    issues = []

    for node, degree in graph.degree():
        if degree > threshold:
            issues.append({
                "category": "Connectivity",
                "issue": "Overconnected Node",
                "node": node,
                "severity": "Medium",
                "explanation": f"{degree} connections exceed threshold",
                "fix": "Check for unintended shorts"
            })

    return issues


# ----------------------------------------
# 🔗 ISOLATED CLUSTERS
# ----------------------------------------
def check_isolated_clusters(graph: nx.Graph):

    try:
        clusters = list(nx.connected_components(graph))
    except:
        return []

    if len(clusters) > 1:
        return [{
            "category": "Connectivity",
            "issue": "Disconnected Clusters",
            "severity": "High",
            "explanation": f"{len(clusters)} isolated networks",
            "fix": "Ensure all nets are connected"
        }]

    return []


# ----------------------------------------
# ⚡ CRITICAL NODES
# ----------------------------------------
def check_critical_nodes(graph: nx.Graph):

    issues = []

    try:
        critical = list(nx.articulation_points(graph))

        for node in critical:
            issues.append({
                "category": "Reliability",
                "issue": "Critical Node",
                "node": node,
                "severity": "Medium",
                "explanation": "Single point of failure",
                "fix": "Add redundancy"
            })
    except:
        pass

    return issues


# ----------------------------------------
# 📉 SPARSE CONNECTIVITY
# ----------------------------------------
def check_sparse_connectivity(graph: nx.Graph):

    if graph.number_of_nodes() == 0:
        return []

    avg_degree = sum(dict(graph.degree()).values()) / graph.number_of_nodes()

    if avg_degree < 1.5:
        return [{
            "category": "Design",
            "issue": "Sparse Connectivity",
            "severity": "Medium",
            "explanation": f"Low avg degree ({avg_degree:.2f})",
            "fix": "Check missing routes"
        }]

    return []


# ----------------------------------------
# 🔗 BRIDGE EDGES
# ----------------------------------------
def check_bridge_edges(graph: nx.Graph):

    issues = []

    try:
        bridges = list(nx.bridges(graph))

        for edge in bridges:
            issues.append({
                "category": "Reliability",
                "issue": "Critical Connection",
                "edge": edge,
                "severity": "Medium",
                "explanation": "Removing this edge breaks connectivity",
                "fix": "Add alternate path"
            })
    except:
        pass

    return issues


# ----------------------------------------
# 🔁 CYCLE DETECTION
# ----------------------------------------
def check_cycle_loops(graph: nx.Graph):

    issues = []

    try:
        cycles = list(nx.cycle_basis(graph))

        if len(cycles) > 10:
            issues.append({
                "category": "Design",
                "issue": "Excessive Loops",
                "severity": "Low",
                "explanation": f"{len(cycles)} loops detected",
                "fix": "Optimize routing"
            })
    except:
        pass

    return issues


# ----------------------------------------
# 🔥 DENSITY CHECK
# ----------------------------------------
def check_dense_regions(graph: nx.Graph):

    issues = []

    try:
        density = nx.density(graph)

        if density > 0.3:
            issues.append({
                "category": "Layout",
                "issue": "High Density Region",
                "severity": "Medium",
                "explanation": f"Density {density:.2f}",
                "fix": "Reduce congestion"
            })
    except:
        pass

    return issues


# ----------------------------------------
# 📊 SUMMARY
# ----------------------------------------
def summarize_rules(issues: List[Dict]):

    summary = {"total": len(issues), "high": 0, "medium": 0, "low": 0}

    for i in issues:
        sev = str(i.get("severity", "")).lower()

        if sev in summary:
            summary[sev] += 1

    return summary


# ----------------------------------------
# 📊 SCORE
# ----------------------------------------
def rule_score(issues: List[Dict]):

    score = 100

    for i in issues:
        sev = str(i.get("severity", "")).lower()

        if sev == "high":
            score -= 12
        elif sev == "medium":
            score -= 6
        elif sev == "low":
            score -= 3

    return max(score, 0)
    
