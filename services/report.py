"""Report Service for PragyanAI PCB Copilot.

Normalizes multimodal defect detections, maps IPC severity levels,
and generates structured executive summaries and markdown reports.
"""

from typing import Any, Dict, List


# ----------------------------------------
#  NORMALIZE ISSUES
# ----------------------------------------
def normalize_issues(agent_name: str, result: Any) -> List[Dict]:
    issues = []
    if not result:
        return issues

    raw_list = []
    if isinstance(result, list):
        raw_list = result
    elif isinstance(result, dict):
        if "issues" in result and isinstance(result["issues"], list):
            raw_list = result["issues"]
        elif "defects" in result and isinstance(result["defects"], list):
            raw_list = result["defects"]
        elif "reasoning" in result and isinstance(result["reasoning"], dict):
            raw_list = result["reasoning"].get(
                "defects", result["reasoning"].get("issues", [])
            )

    for item in raw_list:
        if not isinstance(item, dict):
            continue

        # Flexible key extraction
        name = (
            item.get("issue")
            or item.get("type")
            or item.get("category")
            or "PCB Anomaly"
        )
        explanation = (
            item.get("explanation")
            or item.get("description")
            or item.get("details")
            or ""
        )
        fix = (
            item.get("fix")
            or item.get("recommended_fix")
            or item.get("action")
            or "Inspect and rework per IPC-A-610 standards."
        )
        location = (
            item.get("location")
            or item.get("component_or_net_reference")
            or "Board Wide"
        )
        raw_sev = str(item.get("severity", "medium")).lower()

        # Map severities
        if raw_sev in ["critical", "crit", "severe"]:
            sev = "Critical"
        elif raw_sev in ["high", "major"]:
            sev = "High"
        elif raw_sev in ["low", "minor"]:
            sev = "Low"
        else:
            sev = "Medium"

        issues.append({
            "category": agent_name.capitalize(),
            "issue": f"{name} ({location})" if location != "Board Wide" else name,
            "severity": sev,
            "location": location,
            "explanation": explanation,
            "fix": fix,
            "confidence": float(item.get("confidence", item.get("confidence_score", 0.85))),
        })

    return issues


# ----------------------------------------
#  MERGE ALL ISSUES
# ----------------------------------------
def merge_all_issues(rule_issues: List[Dict], agent_outputs: Dict) -> List[Dict]:
    all_issues = []

    # Process Rule-Engine issues
    if rule_issues:
        for r in rule_issues:
            if isinstance(r, dict):
                all_issues.append({
                    "category": r.get("category", "Rule Engine"),
                    "issue": r.get("issue") or r.get("description") or "Design Rule Violation",
                    "severity": str(r.get("severity", "Medium")).capitalize(),
                    "location": r.get("location", "N/A"),
                    "explanation": r.get("explanation", ""),
                    "fix": r.get("fix", "Review schematic netlist"),
                    "confidence": 1.0,
                })

    # Process Agent issues
    for agent_name, output in agent_outputs.items():
        all_issues.extend(normalize_issues(agent_name, output))

    return all_issues


# ----------------------------------------
#  SEVERITY COUNT
# ----------------------------------------
def severity_breakdown(issues: List[Dict]) -> Dict[str, int]:
    stats = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    for i in issues:
        s = str(i.get("severity", "")).lower()
        if s in stats:
            stats[s] += 1
        else:
            stats["medium"] += 1

    return stats


# ----------------------------------------
#  SCORE CALCULATION
# ----------------------------------------
def calculate_score(issues: List[Dict]) -> int:
    score = 100

    for i in issues:
        s = str(i.get("severity", "")).lower()
        if s == "critical":
            score -= 20
        elif s == "high":
            score -= 12
        elif s == "medium":
            score -= 6
        elif s == "low":
            score -= 2

    return max(score, 0)


# ----------------------------------------
#  EXECUTIVE SUMMARY
# ----------------------------------------
def generate_summary(issues: List[Dict], stats: Dict) -> str:
    total = len(issues)

    if total == 0:
        return "✅ PCB design and assembly verified. No critical defects or violations identified."

    summary = (
        f"PCB Inspection Summary:\n\n"
        f"- Total Issues Detected: {total}\n"
        f"- Critical (Hard Shorts/Bridges): {stats['critical']}\n"
        f"- High Severity (Cold Joints/Corrosion): {stats['high']}\n"
        f"- Medium Severity (Layout/Thermals): {stats['medium']}\n"
        f"- Low Severity (Cosmetic/Slight Misalignment): {stats['low']}\n"
    )

    if stats["critical"] > 0 or stats["high"] > 0:
        summary += "\n⚠️ Action Required: Severe physical assembly or topological defects found. Immediate board rework needed."
    elif stats["medium"] > 0:
        summary += "\n⚡ Warning: Moderate layout or thermal bottlenecks detected. Review before fabrication."
    else:
        summary += "\n✅ Notice: Minor anomalies present. Assembly remains functional."

    return summary.strip()


# ----------------------------------------
#  PRIORITIZATION & CATEGORIES
# ----------------------------------------
def prioritize_issues(issues: List[Dict]) -> List[Dict]:
    priority_map = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return sorted(
        issues,
        key=lambda x: priority_map.get(str(x.get("severity", "medium")).lower(), 2),
    )


def category_breakdown(issues: List[Dict]) -> Dict[str, List[Dict]]:
    categories = {}
    for issue in issues:
        cat = issue.get("category", "General")
        categories.setdefault(cat, []).append(issue)
    return categories


# ----------------------------------------
#  COMPLETE SYSTEM REPORT
# ----------------------------------------
def build_full_system_report(results: Dict) -> Dict:
    """Consolidates orchestrator outputs into a unified inspection report."""
    if not results:
        return {
            "score": 0,
            "summary": "No analysis data available.",
            "issue_count": 0,
            "severity": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "issues": [],
            "recommended_actions": [],
        }

    agent_outputs = {
        "vision": results.get("vision"),
        "power": results.get("power"),
        "signal": results.get("signal"),
        "thermal": results.get("thermal"),
        "layout": results.get("layout"),
        "gnn": results.get("gnn"),
    }

    # If the orchestrator already synthesized final issues, include them
    direct_issues = results.get("issues", [])
    if direct_issues:
        agent_outputs["orchestrator"] = direct_issues

    all_issues = merge_all_issues([], agent_outputs)
    stats = severity_breakdown(all_issues)
    score = calculate_score(all_issues)

    final_meta = results.get("final") or {}
    summary = final_meta.get("summary") or generate_summary(all_issues, stats)

    # Use meta-score if valid, else use calculated score
    if isinstance(final_meta.get("score"), (int, float)):
        score = final_meta["score"]

    prioritized = prioritize_issues(all_issues)
    categories = category_breakdown(all_issues)

    # Extract actions
    actions = []
    tool_output = results.get("tools", {})
    if isinstance(tool_output, dict):
        actions = tool_output.get("actions", [])
    if not actions and all_issues:
        actions = [{"action": f"Rework {i['issue']}: {i['fix']}"} for i in prioritized[:5]]

    return {
        "score": int(score),
        "status": final_meta.get("status", "REWORK_REQUIRED" if score < 70 else "PASS"),
        "summary": summary,
        "issue_count": len(all_issues),
        "severity": stats,
        "issues": all_issues,
        "prioritized_issues": prioritized[:10],
        "categories": categories,
        "recommended_actions": actions,
    }


# ----------------------------------------
#  MARKDOWN EXPORT
# ----------------------------------------
def report_to_markdown(report: Dict) -> str:
    md = "# ⚡ PragyanAI PCB Copilot - Quality Inspection Report\n\n"
    md += f"**Health Score:** {report.get('score', 0)} / 100\n"
    md += f"**Inspection Verdict:** {report.get('status', 'N/A')}\n\n"

    md += "## 📋 Executive Summary\n"
    md += f"{report.get('summary', 'No summary available.')}\n\n"

    md += "## ⚠️ Detected Issues\n"
    issues = report.get("issues", [])
    if issues:
        for idx, i in enumerate(issues, start=1):
            md += f"### {idx}. [{i.get('severity', 'Medium')}] {i.get('issue', 'Unnamed Defect')}\n"
            md += f"- **Category:** {i.get('category', 'General')}\n"
            md += f"- **Location:** {i.get('location', 'N/A')}\n"
            if i.get("explanation"):
                md += f"- **Description:** {i.get('explanation')}\n"
            if i.get("fix"):
                md += f"- **Recommended Fix:** {i.get('fix')}\n"
            md += "\n"
    else:
        md += "_No defects identified during inspection._\n\n"

    md += "## 🔧 Recommended Action Plan\n"
    actions = report.get("recommended_actions", [])
    if actions:
        for a in actions:
            action_text = a.get("action") if isinstance(a, dict) else str(a)
            md += f"- {action_text}\n"
    else:
        md += "- No rework required.\n"

    return md
    
