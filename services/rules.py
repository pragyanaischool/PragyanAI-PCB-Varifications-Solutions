# services/rules.py

"""
Enhanced Rule Engine (PCB DRC + Graph Intelligence)

Checks:
✔ Connectivity
✔ Reliability
✔ Congestion
✔ Redundancy
✔ Structural issues
"""

from typing import List, Dict
import networkx as nx


# ----------------------------------------
# 🚀 MAIN RULE ENGINE
# ----------------------------------------
def run_rules(graph: nx.Graph) -> List[Dict]:

    if graph is None or graph.number_of_nodes() == 0:
        return [{
            "category": "Input",
            "issue": "Empty Graph",
            "severity": "High",
            "explanation": "No PCB data available",
            "fix": "Check input pipeline"
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
                "explanation": "Component not connected",
                "fix": "Check net connections"
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
                "fix": "Check for short circuits"
            })

    return issues


# ----------------------------------------
# 🔗 ISOLATED CLUSTERS
# ----------------------------------------
def check_isolated_clusters(graph: nx.Graph):

    clusters = list(nx.connected_components(graph))

    if len(clusters) > 1:
        return [{
            "category": "Connectivity",
            "issue": "Disconnected Clusters",
            "severity": "High",
            "explanation": f"{len(clusters)} isolated networks",
            "fix": "Ensure complete routing"
        }]

    return []


# ----------------------------------------
# ⚡ CRITICAL NODES
# ----------------------------------------
def check_critical_nodes(graph: nx.Graph):

    issues = []

    try:
        for node in nx.articulation_points(graph):
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
            "explanation": f"Low avg degree: {avg_degree:.2f}",
            "fix": "Check missing routes"
        }]

    return []


# ----------------------------------------
# 🔗 BRIDGE EDGES (CRITICAL LINKS)
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
                "explanation": "Edge removal disconnects graph",
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
# 🔥 DENSE REGION CHECK
# ----------------------------------------
def check_dense_regions(graph: nx.Graph):

    issues = []

    density = nx.density(graph)

    if density > 0.3:
        issues.append({
            "category": "Layout",
            "issue": "High Density Region",
            "severity": "Medium",
            "explanation": f"Graph density {density:.2f}",
            "fix": "Reduce congestion"
        })

    return issues


# ----------------------------------------
# 📊 RULE SUMMARY
# ----------------------------------------
def summarize_rules(issues: List[Dict]):

    summary = {"total": len(issues), "high": 0, "medium": 0, "low": 0}

    for i in issues:
        sev = i.get("severity", "").lower()
        if sev in summary:
            summary[sev] += 1

    return summary


# ----------------------------------------
# 📊 RULE SCORE
# ----------------------------------------
def rule_score(issues: List[Dict]):

    score = 100

    for i in issues:
        sev = i.get("severity", "").lower()

        if sev == "high":
            score -= 12
        elif sev == "medium":
            score -= 6
        elif sev == "low":
            score -= 3

    return max(score, 0)
