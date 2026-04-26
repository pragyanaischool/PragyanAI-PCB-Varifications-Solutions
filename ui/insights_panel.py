# ui/insights_panel.py

"""
PCB Insights Panel

Displays:
✔ YOLO component detection insights
✔ Segmentation (routing density)
✔ OCR extracted labels
✔ Issue / defect breakdown
✔ Interactive filters
"""

import streamlit as st


# ----------------------------------------
# 📦 COMPONENT ANALYSIS (YOLO)
# ----------------------------------------
def component_insights(components):

    if not components:
        st.info("No components detected")
        return

    st.subheader("📦 Component Insights")

    summary = {}
    confidences = []

    for c in components:
        name = c.get("component", "unknown")
        conf = c.get("confidence", 0)

        summary[name] = summary.get(name, 0) + 1
        confidences.append(conf)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Components", len(components))

    with col2:
        avg_conf = round(sum(confidences) / len(confidences), 2) if confidences else 0
        st.metric("Avg Confidence", avg_conf)

    st.json(summary)

    # 🔍 Filter by component
    selected = st.selectbox("Filter Component", ["All"] + list(summary.keys()))

    if selected != "All":
        filtered = [c for c in components if c.get("component") == selected]
        st.json(filtered)


# ----------------------------------------
# 🌡️ SEGMENTATION INSIGHTS
# ----------------------------------------
def segmentation_insights(segmentation):

    if not segmentation:
        st.info("No segmentation data available")
        return

    st.subheader("🌡️ Routing / Segmentation Insights")

    density = segmentation.get("trace_density", "unknown")
    regions = segmentation.get("regions", [])

    st.metric("Trace Density", str(density))

    if regions:
        st.write(f"Detected Regions: {len(regions)}")

        high_density = [
            r for r in regions if r.get("density", 0) > 0.7
        ]

        st.metric("High Density Zones", len(high_density))

        if high_density:
            st.warning("⚠️ Congestion detected in routing")

    else:
        st.info("No segmentation regions found")


# ----------------------------------------
# 🔤 OCR INSIGHTS
# ----------------------------------------
def ocr_insights(ocr):

    if not ocr:
        st.info("No OCR data available")
        return

    st.subheader("🔤 OCR Insights")

    text = ocr.get("text", "")
    components = ocr.get("components", [])
    lines = ocr.get("lines", [])

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Text Length", len(text))

    with col2:
        st.metric("Detected Labels", len(components))

    if components:
        st.write("Detected Component Labels:")
        st.write(components)

    if st.checkbox("Show OCR Text"):
        st.text(text[:1000])  # limit


# ----------------------------------------
# 🔥 ISSUE / DEFECT INSIGHTS
# ----------------------------------------
def issue_insights(issues):

    if not issues:
        st.success("✅ No issues detected")
        return

    st.subheader("🔥 Defect / Issue Insights")

    severity_count = {"high": 0, "medium": 0, "low": 0}

    for i in issues:
        sev = i.get("severity", "medium").lower()
        if sev in severity_count:
            severity_count[sev] += 1

    col1, col2, col3 = st.columns(3)

    col1.metric("High", severity_count["high"])
    col2.metric("Medium", severity_count["medium"])
    col3.metric("Low", severity_count["low"])

    # 🔍 Filter issues
    selected = st.selectbox(
        "Filter by Severity",
        ["All", "high", "medium", "low"]
    )

    filtered = issues

    if selected != "All":
        filtered = [i for i in issues if i.get("severity") == selected]

    st.json(filtered[:20])  # limit


# ----------------------------------------
# 🧠 MASTER PANEL
# ----------------------------------------
def show_insights_panel(results):

    st.header("🔍 AI Insights Panel")

    vision = results.get("vision", {})
    structured = vision.get("structured", {})

    components = structured.get("components", [])
    segmentation = structured.get("segmentation", {})
    ocr = structured.get("ocr", {})

    issues = results.get("final", {}).get("issues", [])

    tab1, tab2, tab3, tab4 = st.tabs([
        "📦 Components",
        "🌡️ Segmentation",
        "🔤 OCR",
        "🔥 Issues"
    ])

    with tab1:
        component_insights(components)

    with tab2:
        segmentation_insights(segmentation)

    with tab3:
        ocr_insights(ocr)

    with tab4:
        issue_insights(issues)
