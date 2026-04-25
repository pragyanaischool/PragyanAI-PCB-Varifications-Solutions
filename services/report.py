"""
Report Service

Combines:
- Rule Engine output
- Multi-agent AI outputs
- Tool Agent (fixes)
- Meta Agent summary

Generates:
- Unified issue list
- Score
- Summary
- Category-wise breakdown
- Prioritized issues
- Action plan
"""

from typing import Dict, List


# ----------------------------------------
# 🧠 NORMALIZE ISSUES
# ----------------------------------------
def normalize_issues(agent_name: str, result) -> List[Dict]:

    issues = []

    if isinstance(result, dict) and "issues" in result:
        for issue in result["issues"]:
            issues.append({
                "category": agent_name,
                "issue": issue.get("issue", ""),
                "severity": issue.get("severity", "Medium"),
                "explanation": issue.get("explanation", ""),
                "fix": issue.get("fix", ""),
                "confidence": issue.get("confidence", 0.7)
            })

    return issues


# ----------------------------------------
# 🔗 MERGE ALL ISSUES
# ----------------------------------------
def merge_all_issues(rule_issues: List[Dict], agent_outputs: Dict):

    all_issues = []

    # Rule issues
    for r in rule_issues:
        all_issues.append({
            "category": r.get("category", "Rule"),
            "issue": r.get("issue", ""),
            "severity": r.get("severity", "Medium"),
            "explanation": r.get("explanation", ""),
            "fix": r.get("fix", "")
        })

    # Agent issues
    for agent_name, output in agent_outputs.items():
        all_issues.extend(normalize_issues(agent_name, output))

    return all_issues


# ----------------------------------------
# 📊 SEVERITY COUNT
# ----------------------------------------
def severity_breakdown(issues: List[Dict]):

    stats = {"high": 0, "medium": 0, "low": 0}

    for i in issues:
        s = i.get("severity", "").lower()

        if s == "high":
            stats["high"] += 1
        elif s == "medium":
            stats["medium"] += 1
        elif s == "low":
            stats["low"] += 1

    return stats


# ----------------------------------------
# 🎯 SCORE CALCULATION (IMPROVED)
# ----------------------------------------
def calculate_score(issues: List[Dict]):

    score = 100

    for i in issues:
        s = i.get("severity", "").lower()

        if s == "high":
            score -= 12
        elif s == "medium":
            score -= 6
        elif s == "low":
            score -= 3

    return max(score, 0)


# ----------------------------------------
# 🧾 EXECUTIVE SUMMARY
# ----------------------------------------
def generate_summary(issues: List[Dict], stats: Dict):

    total = len(issues)

    if total == 0:
        return "✅ PCB design looks clean with no major issues."

    summary = f"""
PCB Analysis Summary:

- Total Issues: {total}
- High Severity: {stats['high']}
- Medium Severity: {stats['medium']}
- Low Severity: {stats['low']}
"""

    if stats["high"] > 0:
        summary += "\n⚠️ Critical issues detected. Immediate attention required."
    elif stats["medium"] > 0:
        summary += "\n⚡ Moderate issues present. Optimization recommended."
    else:
        summary += "\n✅ Minor issues only. Design is stable."

    return summary.strip()


# ----------------------------------------
# 🧠 FINAL REPORT GENERATOR
# ----------------------------------------
def generate_report(rule_issues: List[Dict], agent_outputs: Dict):

    all_issues = merge_all_issues(rule_issues, agent_outputs)
    stats = severity_breakdown(all_issues)
    score = calculate_score(all_issues)
    summary = generate_summary(all_issues, stats)

    return {
        "score": score,
        "summary": summary,
        "issue_count": len(all_issues),
        "severity": stats,
        "issues": all_issues
    }


# ----------------------------------------
# 📊 CATEGORY BREAKDOWN
# ----------------------------------------
def category_breakdown(issues: List[Dict]):

    categories = {}

    for issue in issues:
        cat = issue.get("category", "Other")

        if cat not in categories:
            categories[cat] = []

        categories[cat].append(issue)

    return categories


# ----------------------------------------
# 📈 PRIORITIZATION
# ----------------------------------------
def prioritize_issues(issues: List[Dict]):

    priority_map = {"high": 0, "medium": 1, "low": 2}

    return sorted(
        issues,
        key=lambda x: priority_map.get(x.get("severity", "medium").lower(), 1)
    )


# ----------------------------------------
# 🔧 EXTRACT TOOL ACTIONS
# ----------------------------------------
def extract_actions(tool_output):

    if not isinstance(tool_output, dict):
        return []

    return tool_output.get("actions", [])


# ----------------------------------------
# 📦 FULL ENTERPRISE REPORT
# ----------------------------------------
def build_enterprise_report(rule_issues: List[Dict], agent_outputs: Dict):

    base = generate_report(rule_issues, agent_outputs)

    prioritized = prioritize_issues(base["issues"])
    category_view = category_breakdown(base["issues"])

    return {
        **base,
        "prioritized_issues": prioritized[:10],
        "categories": category_view
    }


# ----------------------------------------
# 🚀 COMPLETE SYSTEM REPORT (AI INTEGRATED)
# ----------------------------------------
def build_full_system_report(results: Dict):

    """
    Input: orchestrator results
    """

    agent_outputs = {
        "power": results.get("power"),
        "signal": results.get("signal"),
        "thermal": results.get("thermal"),
        "layout": results.get("layout"),
        "vision": results.get("vision", {}).get("reasoning")
    }

    tool_output = results.get("tools", {})
    final_output = results.get("final", {})

    report = build_enterprise_report([], agent_outputs)

    # Add tool actions
    report["recommended_actions"] = extract_actions(tool_output)

    # Add meta-agent summary
    report["final_summary"] = final_output.get("summary")
    report["final_score"] = final_output.get("score")

    return report


# ----------------------------------------
# 📝 MARKDOWN EXPORT
# ----------------------------------------
def report_to_markdown(report: Dict) -> str:

    md = "# 🔧 PCB Analysis Report\n\n"

    md += f"## 🧠 Summary\n{report.get('summary','')}\n\n"
    md += f"## 📊 Score: {report.get('score','N/A')}\n\n"

    md += "## ⚠️ Issues\n"
    for i in report.get("issues", []):
        md += f"- [{i['severity']}] {i['issue']}\n"

    md += "\n## 🔧 Recommended Actions\n"
    for a in report.get("recommended_actions", []):
        md += f"- {a.get('action')}\n"

    return md
    
