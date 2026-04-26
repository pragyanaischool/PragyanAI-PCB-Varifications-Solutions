import streamlit as st
from PIL import Image
import traceback
import os

# Services
from services.parser import parse_pcb
from services.graph import build_graph, graph_summary
from services.rules import run_rules
from services.report import build_full_system_report, report_to_markdown

# NEW: PDF + RAG
from services.pdf_parser import parse_pdf
from ai.vector_store import build_vector_store

# AI
from ai.orchestrator import run_full_analysis

# UI
from ui.visualization import show_visualization
from ui.insights_panel import show_insights_panel
from ui.chat_panel import show_chat_panel   # ✅ NEW
import sys
sys.modules['cv2'] = None
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
st.caption("Vision + YOLO + Segmentation + Multi-Agent AI + RAG")


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
    - Segmentation  
    - Multi-Agent AI  
    - RAG (Docs + Chat)  
    """)


# ----------------------------------------
# 📤 PCB IMAGE UPLOAD
# ----------------------------------------
pcb_file = st.file_uploader(
    "Upload PCB Image",
    type=["png", "jpg", "jpeg"]
)


# ----------------------------------------
# 📄 PDF DATASHEET UPLOAD (NEW)
# ----------------------------------------
doc_file = st.file_uploader(
    "Upload Datasheet / PDF (Optional)",
    type=["pdf"]
)

if doc_file:

    try:
        doc_path = save_uploaded_file(doc_file)

        pdf_data = parse_pdf(doc_path)

        if "text" in pdf_data and pdf_data["text"]:

            build_vector_store(pdf_data["text"])
            st.success("📚 Knowledge base updated (RAG ready)")

        else:
            st.warning("⚠️ No text extracted from PDF")

    except Exception as e:
        st.error(f"PDF processing error: {e}")


# ----------------------------------------
# 🖼️ PREVIEW (FIXED SAFE)
# ----------------------------------------
if pcb_file:
    try:
        image = Image.open(pcb_file.getvalue())  # ✅ FIXED
        st.image(image, caption="PCB Preview", use_container_width=True)
    except Exception as e:
        st.warning(f"Preview not available: {e}")


# ----------------------------------------
# 🚀 RUN ANALYSIS
# ----------------------------------------
if pcb_file and st.button("🚀 Run AI Analysis"):

    try:
        with st.spinner("Running AI pipeline..."):

            # ----------------------------------------
            # 💾 SAVE FILE
            # ----------------------------------------
            file_path = save_uploaded_file(pcb_file)

            if not file_path or not os.path.exists(file_path):
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
            # 🤖 AI PIPELINE
            # ----------------------------------------
            result = run_full_analysis(image_path=file_path)
            results = result.get("results", {})

            # ----------------------------------------
            # 📊 REPORT
            # ----------------------------------------
            report = build_full_system_report(results)

        st.success("✅ Analysis Completed")

        # ----------------------------------------
        # 📊 TABS (ENHANCED)
        # ----------------------------------------
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "🧠 Final Report",
            "🖼️ Visual Debugger",
            "🔍 Vision AI",
            "📊 Insights Panel",
            "⚡ Domain Insights",
            "📊 Graph & Rules",
            "🐞 Debug",
            "💬 Chat AI"   # ✅ NEW
        ])

        # ----------------------------------------
        # 🧠 FINAL REPORT
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
        # 🖼️ VISUAL DEBUGGER
        # ----------------------------------------
        with tab2:
            show_visualization(file_path, results)

        # ----------------------------------------
        # 🔍 VISION AI
        # ----------------------------------------
        with tab3:

            vision = results.get("vision", {})
            structured = vision.get("structured", {})

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📦 YOLO Detection")
                st.json(structured.get("components", []))

            with col2:
                st.subheader("🌡️ Segmentation")
                st.json(structured.get("segmentation", {}))

            st.subheader("🔤 OCR")
            st.json(structured.get("ocr", {}))

        # ----------------------------------------
        # 🧠 INSIGHTS
        # ----------------------------------------
        with tab4:
            show_insights_panel(results)

        # ----------------------------------------
        # ⚡ DOMAIN AGENTS
        # ----------------------------------------
        with tab5:

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("⚡ Power")
                st.json(results.get("power"))

                st.subheader("🔌 Signal")
                st.json(results.get("signal"))

            with col2:
                st.subheader("🌡️ Thermal")
                st.json(results.get("thermal"))

                st.subheader("🧩 Layout")
                st.json(results.get("layout"))

        # ----------------------------------------
        # 📊 GRAPH + RULES
        # ----------------------------------------
        with tab6:
            st.subheader("Graph Summary")
            st.json(g_summary)

            st.subheader("Rule Issues")
            st.json(rule_issues)

        # ----------------------------------------
        # 🐞 DEBUG
        # ----------------------------------------
        with tab7:
            if show_debug:
                st.json(result)

        # ----------------------------------------
        # 💬 CHAT AI (NEW)
        # ----------------------------------------
        with tab8:
            show_chat_panel(results)

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
