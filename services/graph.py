# services/graph.py

"""
PCB Graph Builder

Creates graph from:
- Vision (YOLO components)
- OCR (labels)
- Segmentation (optional)

Graph Format:
{
    "nodes": [...],
    "edges": [...],
    "metadata": {...}
}
"""

from typing import Dict, List
import math


# ----------------------------------------
# 🧠 MAIN GRAPH BUILDER
# ----------------------------------------
def build_graph(vision_data: Dict, ocr_data: Dict = None) -> Dict:

    structured = vision_data.get("structured", {})
    components = structured.get("components", [])

    nodes = []
    edges = []

    # ----------------------------------------
    # 🔹 CREATE NODES
    # ----------------------------------------
    for idx, comp in enumerate(components):

        node = {
            "id": idx,
            "type": comp.get("component", "unknown"),
            "bbox": comp.get("bbox", []),
            "center": _get_center(comp.get("bbox", [])),
        }

        nodes.append(node)

    # ----------------------------------------
    # 🔹 CONNECT NODES (PROXIMITY-BASED)
    # ----------------------------------------
    edges = _build_edges(nodes)

    # ----------------------------------------
    # 🔹 OCR ENRICHMENT
    # ----------------------------------------
    if ocr_data:
        _attach_ocr_labels(nodes, ocr_data)

    # ----------------------------------------
    # 📊 METADATA
    # ----------------------------------------
    metadata = {
        "num_nodes": len(nodes),
        "num_edges": len(edges),
        "node_types": list(set(n["type"] for n in nodes))
    }

    return {
        "nodes": nodes,
        "edges": edges,
        "metadata": metadata
    }


# ----------------------------------------
# 📐 COMPUTE CENTER
# ----------------------------------------
def _get_center(bbox):

    if not bbox or len(bbox) != 4:
        return (0, 0)

    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)


# ----------------------------------------
# 🔗 BUILD EDGES (DISTANCE BASED)
# ----------------------------------------
def _build_edges(nodes: List[Dict], threshold=150):

    edges = []

    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):

            dist = _distance(nodes[i]["center"], nodes[j]["center"])

            if dist < threshold:
                edges.append({
                    "source": nodes[i]["id"],
                    "target": nodes[j]["id"],
                    "distance": round(dist, 2)
                })

    return edges


# ----------------------------------------
# 📏 DISTANCE FUNCTION
# ----------------------------------------
def _distance(p1, p2):

    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


# ----------------------------------------
# 🔤 ATTACH OCR LABELS
# ----------------------------------------
def _attach_ocr_labels(nodes, ocr_data):

    labels = ocr_data.get("components", [])

    for i, node in enumerate(nodes):
        if i < len(labels):
            node["label"] = labels[i]
        else:
            node["label"] = None


# ----------------------------------------
# 📊 GRAPH SUMMARY
# ----------------------------------------
def graph_summary(graph):

    return {
        "nodes": len(graph.get("nodes", [])),
        "edges": len(graph.get("edges", [])),
        "types": graph.get("metadata", {}).get("node_types", [])
    }


# ----------------------------------------
# 🔍 FIND ISOLATED NODES
# ----------------------------------------
def find_isolated_nodes(graph):

    connected = set()

    for e in graph.get("edges", []):
        connected.add(e["source"])
        connected.add(e["target"])

    all_nodes = set(n["id"] for n in graph.get("nodes", []))

    isolated = list(all_nodes - connected)

    return isolated


# ----------------------------------------
# 🔧 GRAPH VALIDATION
# ----------------------------------------
def validate_graph(graph):

    issues = []

    if not graph.get("nodes"):
        issues.append("No nodes detected")

    if not graph.get("edges"):
        issues.append("No connections found")

    isolated = find_isolated_nodes(graph)

    if isolated:
        issues.append(f"Isolated nodes detected: {isolated}")

    return {
        "valid": len(issues) == 0,
        "issues": issues
    }


# ----------------------------------------
# ⚡ QUICK GRAPH BUILDER (SHORTCUT)
# ----------------------------------------
def build_graph_from_vision_only(vision_data):

    return build_graph(vision_data)
    
