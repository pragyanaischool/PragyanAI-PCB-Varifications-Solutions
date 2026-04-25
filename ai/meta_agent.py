# ai/meta_agent.py

import json
import re
import streamlit as st

from ai.llm import invoke_with_memory, invoke_llm


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
        "summary": str(text),
        "issues": [],
        "score": 50,
        "confidence": 0.5,
        "raw_output": text
    }


# ----------------------------------------
# 📊 ISSUE AGGREGATION
# ----------------------------------------
def collect_all_issues(memory):

    issues = []

    for key in ["vision", "power", "signal", "thermal", "layout", "gnn"]:
        data = memory.get(key)

        if isinstance(data, dict) and "issues" in data:
            issues.extend(data["issues"])

    return issues


# ----------------------------------------
# 🎯 RULE-BASED SCORE (FALLBACK)
# ----------------------------------------
def fallback_score(issues):

    score = 100

    for i in issues:
        sev = str(i.get("severity", "medium")).lower()

        if sev == "high":
            score -= 12
        elif sev == "medium":
            score -= 6
        elif sev == "low":
            score -= 3

    return max(score, 0)


# ----------------------------------------
# 🧠 META AGENT (MAIN)
# ----------------------------------------
def run_meta_agent(memory, structured=True):

    context = memory.get_context()

    all_issues = collect_all_issues(memory)

    prompt = f"""
    You are a Chief PCB Design Engineer.

    Combine ALL analysis:

    {context}

    Total Issues:
    {all_issues}

    Provide:

    - Final summary
    - Top 5 critical issues
    - Recommended fixes
    - Overall score (0-100)

    Return STRICT JSON:
    {{
        "summary": "...",
        "top_issues": [...],
        "recommendations": [...],
        "score": 0-100,
        "confidence": 0.0-1.0
    }}
    """

    response = invoke_with_memory(memory, "PCB Chief Engineer", prompt)
    result = extract_json(response)

    # ----------------------------------------
    # ⚠️ FALLBACK LOGIC
    # ----------------------------------------
    if not result.get("score") or result["score"] == 0:
        result["score"] = fallback_score(all_issues)

    if not result.get("top_issues"):
        result["top_issues"] = all_issues[:5]

    if not result.get("recommendations"):
        tools = memory.get("tools", {})
        result["recommendations"] = tools.get("actions", [])

    return result if structured else response


# ----------------------------------------
# 📊 CONSISTENCY CHECK
# ----------------------------------------
def validate_consistency(memory):

    power = memory.get("power")
    thermal = memory.get("thermal")

    inconsistencies = []

    if power and thermal:
        if "overheating" in str(thermal).lower() and "stable" in str(power).lower():
            inconsistencies.append("Thermal issues contradict power stability")

    return inconsistencies


# ----------------------------------------
# 🔍 QUICK SUMMARY
# ----------------------------------------
def quick_summary(memory):

    return invoke_with_memory(
        memory,
        "PCB Quick Analyst",
        "Give short summary of PCB condition."
    )


# ----------------------------------------
# 🔄 CACHE
# ----------------------------------------
@st.cache_data(show_spinner=False)
def cached_meta_agent(memory_dict):

    class TempMemory:
        def __init__(self, data):
            self.data = data

        def get(self, key, default=None):
            return self.data.get(key, default)

        def get_context(self):
            return str(self.data)

    return run_meta_agent(TempMemory(memory_dict))


# ----------------------------------------
# 📈 SCORE BREAKDOWN
# ----------------------------------------
def score_breakdown(memory):

    issues = collect_all_issues(memory)

    breakdown = {
        "high": 0,
        "medium": 0,
        "low": 0
    }

    for i in issues:
        sev = str(i.get("severity", "medium")).lower()

        if sev in breakdown:
            breakdown[sev] += 1

    return breakdown


# ----------------------------------------
# 🧠 DECISION EXPLANATION
# ----------------------------------------
def explain_decision(memory):

    return invoke_with_memory(
        memory,
        "PCB Decision Explainer",
        "Explain why this PCB got its score."
    )
