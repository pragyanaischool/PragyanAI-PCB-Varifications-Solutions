# services/kicad_parser.py

"""
KiCad / Netlist Parser for PCB AI System

✔ Parse KiCad netlist (.net)
✔ Parse .kicad_pcb (basic)
✔ Extract components
✔ Extract nets (connections)
✔ Build graph-ready structure
✔ Safe + production ready
"""

import re
import os
from typing import Dict, List


# ----------------------------------------
# 🔍 PARSE KICAD NETLIST (.net)
# ----------------------------------------
def parse_netlist(file_path: str) -> Dict:

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # ----------------------------------------
        # 📦 COMPONENTS
        # ----------------------------------------
        components = re.findall(
            r'\(comp\s+\(ref\s+([A-Za-z0-9]+)\)',
            content
        )

        # ----------------------------------------
        # 🔗 NETS
        # ----------------------------------------
        nets = re.findall(
            r'\(net\s+\d+\s+"([^"]+)"',
            content
        )

        # ----------------------------------------
        # 🔗 CONNECTIONS (simple extraction)
        # ----------------------------------------
        connections = re.findall(
            r'\(node\s+\(ref\s+([A-Za-z0-9]+)\)\s+\(pin\s+([A-Za-z0-9]+)\)\)',
            content
        )

        # Convert to edges (simple pair grouping)
        edges = []

        for i in range(0, len(connections) - 1, 2):
            n1 = connections[i][0]
            n2 = connections[i + 1][0]
            edges.append((n1, n2))

        return {
            "components": list(set(components)),
            "nets": list(set(nets)),
            "edges": edges,
            "num_components": len(components),
            "num_nets": len(nets)
        }

    except Exception as e:
        return {"error": str(e)}


# ----------------------------------------
# 🧩 PARSE .KICAD_PCB FILE (BASIC)
# ----------------------------------------
def parse_kicad_pcb(file_path: str) -> Dict:

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # ----------------------------------------
        # 📦 COMPONENTS (modules)
        # ----------------------------------------
        components = re.findall(
            r'\(module\s+([^\s]+)',
            content
        )

        # ----------------------------------------
        # 📍 POSITIONS (approx)
        # ----------------------------------------
        positions = re.findall(
            r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)',
            content
        )

        # ----------------------------------------
        # 🔗 NETS
        # ----------------------------------------
        nets = re.findall(
            r'\(net\s+\d+\s+"([^"]+)"',
            content
        )

        return {
            "components": components,
            "positions": positions,
            "nets": nets,
            "num_components": len(components),
            "num_nets": len(nets)
        }

    except Exception as e:
        return {"error": str(e)}


# ----------------------------------------
# 🧠 BUILD GRAPH (FOR RULES / GNN)
# ----------------------------------------
def build_graph_from_netlist(parsed_data: Dict) -> Dict:

    components = parsed_data.get("components", [])
    edges = parsed_data.get("edges", [])

    return {
        "nodes": components,
        "edges": edges
    }


# ----------------------------------------
# 📊 SUMMARY
# ----------------------------------------
def summarize_kicad(parsed_data: Dict) -> Dict:

    if "error" in parsed_data:
        return {"valid": False}

    return {
        "valid": True,
        "components": parsed_data.get("num_components", 0),
        "nets": parsed_data.get("num_nets", 0),
        "edges": len(parsed_data.get("edges", []))
    }


# ----------------------------------------
# ⚡ QUICK PARSE
# ----------------------------------------
def quick_parse_kicad(file_path: str) -> Dict:

    try:
        if file_path.endswith(".net"):
            data = parse_netlist(file_path)
        else:
            data = parse_kicad_pcb(file_path)

        return {
            "components_preview": data.get("components", [])[:10],
            "nets_preview": data.get("nets", [])[:10]
        }

    except Exception as e:
        return {"error": str(e)}


# ----------------------------------------
# 🧠 UNIVERSAL PARSER
# ----------------------------------------
def parse_kicad(file_path: str) -> Dict:

    if file_path.endswith(".net"):
        return parse_netlist(file_path)

    if file_path.endswith(".kicad_pcb"):
        return parse_kicad_pcb(file_path)

    return {"error": "Unsupported file format"}
