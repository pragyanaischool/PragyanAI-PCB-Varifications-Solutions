import streamlit as st
from PIL import Image
import traceback

# Services
from services.parser import parse_pcb
from services.graph import build_graph, graph_summary
from services.rules import run_rules
from services.report import build_full_system_report, report_to_markdown

# AI
from ai.orchestrator import run_full_analysis

# UI
from ui.visualization import show_visualization

# Utils
from utils.file import save_uploaded_file, safe_delete


# ----------------------------------------
# 🎨 CONFIG
# ----------------------------------------
st.set_page_config(
    page_title="PragyanAI PCB Copilot",
    layout="wide",
    page_icon="⚡"
)

st.title("⚡ PragyanAI PCB Copilot")
st.caption("Vision + YOLO + Segmentation + Multi-Agent AI")

# ----------------------------------------
# ⚙️ SIDEBAR
# ----------------------------------------
with st.sidebar:

    st.header("⚙️ Settings")

    run_mode = st.selectbox(
        "Analysis Mode",
        ["Full (Accurate)", "Quick (Fast)"]
    )

    show_debug = st.checkbox("Show Debug Info", value=False)
    cleanup_files_flag = st.checkbox("Cleanup temp files", value=True)

    st.markdown("---")
    st.markdown("### 🔍 AI Stack")
    st.markdown("""
    - YOLO Detection  
    - OCR Extraction  
    - Segmentation (Routing Heatmap)  
    - Multi-Agent AI  
    """)

# ----------------------------------------
# 📤 FILE UPLOAD
# ----------------------------------------
pcb_file = st.file_uploader(
    "Upload PCB Image",
    type=["png", "jpg", "jpeg"]
)

# ----------------------------------------
# 🖼️ PREVIEW
# ----------------------------------------
if pcb_file:
    try:
        image = Image.open(pcb_file)
        st.image(image, caption="PCB Preview", use_container_width=True)
    except:
        st.warning("Preview not available")

# ----------------------------------------
# 🚀 RUN ANALYSIS
# ----------------------------------------
if pcb_file and st.button("🚀 Run AI Analysis"):

    try:
        with st.spinner("Running AI pipeline..."):

            # ----------------------------------------
            # 💾 SAVE FILE (FIXED)
            # ----------------------------------------
            file_path = save_uploaded_file(pcb_file)

            if not file_path:
                st.error("❌ File saving failed")
                st.stop()

            # ----------------------------------------
            # 🧠 PARSE + GRAPH
            # ----------------------------------------
            pcb_data = parse_pcb(file_path)
            graph = build_graph(pcb_data)
            g_summary = graph_summary(graph)

            # ----------------------------------------
            # ⚠️ RULE ENGINE
            # ----------------------------------------
            rule_issues = run_rules(graph)

            # ----------------------------------------
            # 🤖 AI PIPELINE (UPDATED)
            # ----------------------------------------
            result = run_full_analysis(image_path=file_path)
            results = result.get("results", {})

            # ----------------------------------------
            # 📊 REPORT
            # ----------------------------------------
            report = build_full_system_report(results)

        st.success("✅ Analysis Completed")

        # ----------------------------------------
        # 📊 TABS
        # ----------------------------------------
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🧠 Final Report",
            "🖼️ Visual Debugger",
            "🔍 Vision AI (YOLO + Segmentation)",
            "⚡ Domain Insights",
            "📊 Graph & Rules",
            "🐞 Debug"
        ])

        # ----------------------------------------
        # 🧠 REPORT
        # ----------------------------------------
        with tab1:

            st.metric("PCB Score", report.get("score", 0))

            st.subheader("Summary")
            st.write(report.get("summary"))

            st.subheader("Issues")
            st.json(report.get("issues", []))

            st.subheader("Recommended Fixes")
            st.json(report.get("recommended_actions", []))

            st.download_button(
                "Download Report",
                report_to_markdown(report),
                file_name="pcb_report.md"
            )

        # ----------------------------------------
        # 🖼️ VISUALIZATION
        # ----------------------------------------
        with tab2:
            show_visualization(file_path, results)

        # ----------------------------------------
        # 🔍 VISION AI PANEL (NEW)
        # ----------------------------------------
        with tab3:

            vision = results.get("vision", {})
            structured = vision.get("structured", {})

            components = structured.get("components", [])
            segmentation = structured.get("segmentation", {})
            ocr = structured.get("ocr", {})

            st.subheader("📦 YOLO Detection")
            st.json(components)

            st.subheader("🌡️ Segmentation (Routing Heatmap)")
            st.json(segmentation)

            st.subheader("🔤 OCR Extraction")
            st.json(ocr)

        # ----------------------------------------
        # ⚡ DOMAIN AGENTS
        # ----------------------------------------
        with tab4:

            col1, col2 = st.columns(2)

            with col1:
                st.json(results.get("power"))
                st.json(results.get("signal"))

            with col2:
                st.json(results.get("thermal"))
                st.json(results.get("layout"))

        # ----------------------------------------
        # 📊 GRAPH + RULES
        # ----------------------------------------
        with tab5:
            st.json(g_summary)
            st.json(rule_issues)

        # ----------------------------------------
        # 🐞 DEBUG
        # ----------------------------------------
        with tab6:
            if show_debug:
                st.json(result)

        # ----------------------------------------
        # 🧹 CLEANUP
        # ----------------------------------------
        if cleanup_files_flag:
            safe_delete(file_path)

    except Exception as e:

        st.error("❌ Error during processing")

        st.text(str(e))
        st.text(traceback.format_exc())

# ----------------------------------------
# FOOTER
# ----------------------------------------
st.markdown("---")
st.markdown("⚡ PragyanAI | PCB Copilot | AI Debugging System")
