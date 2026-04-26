# app.py
import os
os.environ["ULTRALYTICS_NO_AUTO_INSTALL"] = "1"  

import streamlit as st
from PIL import Image
import traceback
import sys
# ----------------------------------------
# HARD BLOCK CV2 (CRITICAL FIX)
# ----------------------------------------
#sys.modules['cv2'] = None
# ----------------------------------------
# Services
# ----------------------------------------
from services.parser import parse_pcb
from services.graph import build_graph, graph_summary
from services.rules import run_rules
from services.report import build_full_system_report, report_to_markdown

# RAG
from services.pdf_parser import parse_pdf
from ai.vector_store import build_vector_store

# AI
from ai.orchestrator import run_full_analysis

# UI
from ui.visualization import show_visualization
from ui.insights_panel import show_insights_panel
from ui.chat_panel import show_chat_panel, chat_controls

# Utils
from utils.file import save_uploaded_file, safe_delete

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}
h1, h2, h3 {
    font-weight: 600;
}
.stTabs [data-baseweb="tab"] {
    font-size: 16px;
    padding: 10px 20px;
}
.stButton>button {
    border-radius: 10px;
    height: 45px;
}
</style>
""", unsafe_allow_html=True)
# ----------------------------------------
# CONFIG
# ----------------------------------------
st.set_page_config(
    page_title="PragyanAI PCB Copilot",
    layout="wide",
    page_icon="⚡"
)
st.image("PragyanAI_Transperent.png")
st.title(" PragyanAI PCB Copilot")
st.caption(" Vision + YOLO + Segmentation + Multi-Agent AI + RAG")

# ----------------------------------------
#  SIDEBAR
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

    st.markdown("### PCB Varification - AI Stack")
    st.markdown("""
    - YOLO Detection  
    - OCR Extraction  
    - Segmentation  
    - Multi-Agent AI  
    - RAG (Docs + Chat)  
    """)
    chat_controls()  

# ----------------------------------------
#  PCB IMAGE UPLOAD
# ----------------------------------------
pcb_file = st.file_uploader(
    "Upload PCB Image",
    type=["png", "jpg", "jpeg"]
)

# ----------------------------------------
#  PDF (RAG INPUT)
# ----------------------------------------
doc_file = st.file_uploader(
    "Upload Datasheet / PDF (Optional)",
    type=["pdf", "csv", "xls"], 
    accept_multiple_files=True
)

if doc_file:

    try:
        doc_path = save_uploaded_file(doc_file)

        pdf_data = parse_pdf(doc_path)

        if "text" in pdf_data and pdf_data["text"]:
            build_vector_store(pdf_data["text"])
            st.success("📚 Knowledge base updated")
        else:
            st.warning("⚠️ No text extracted")

    except Exception as e:
        st.error(f"PDF error: {e}")


# ----------------------------------------
#  PREVIEW (FIXED)
# ----------------------------------------
if pcb_file:
    try:
        image = Image.open(pcb_file)
        st.image(image, caption="PCB Preview", use_container_width=True)
    except Exception as e:
        st.warning(f"Preview not available: {e}")

# ----------------------------------------
#  RUN ANALYSIS
# ----------------------------------------
if pcb_file and st.button(" Run PCB - AI Analysis"):

    try:
        with st.spinner("Running AI pipeline..."):

            file_path = save_uploaded_file(pcb_file)

            if not file_path or not os.path.exists(file_path):
                st.error("❌ File saving failed")
                st.stop()

            # ----------------------------------------
            # PARSER + GRAPH
            # ----------------------------------------
            pcb_data = parse_pcb(file_path)
            graph = build_graph(pcb_data)
            g_summary = graph_summary(graph)

            # ----------------------------------------
            # RULE ENGINE
            # ----------------------------------------
            rule_issues = run_rules(graph)

            # ----------------------------------------
            # AI PIPELINE
            # ----------------------------------------
            results = run_full_analysis(
                image_path=file_path,
                graph_summary=g_summary,
                gnn_output=None,
                ocr_text=None
            )

            # ----------------------------------------
            # REPORT
            # ----------------------------------------
            #report = build_full_system_report(results)
            if results:
                report = build_full_system_report(results)
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("PCB Score", report.get("score", 0))
                col2.metric("Issues", report.get("issue_count", 0))
                col3.metric("High Severity", report.get("severity", {}).get("high", 0))
                col4.metric("Components", len(results.get("vision", {}).get("structured", {}).get("components", [])))
            else:
                st.warning("⚠️ Run analysis first")
                st.stop()
                st.success("✅ Analysis Completed")
            
        # ----------------------------------------
        #  TABS
        # ----------------------------------------
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "  Final Report",
            "  Visualization",
            "  Vision AI",
            "  Insights",
            "  Domain",
            "  Graph & Rules",
            "  Debug",
            "  Chat AI"
        ])

        # ----------------------------------------
        # REPORT
        # ----------------------------------------
        with tab1:
            st.metric("PCB Score", report.get("score", 0))
            st.write(report.get("summary"))
            st.json(report.get("issues", []))

            st.download_button(
                "Download Report",
                report_to_markdown(report),
                file_name="pcb_report.md"
            )

        # ----------------------------------------
        # VISUALIZATION
        # ----------------------------------------
        with tab2:
            show_visualization(file_path, results)

        # ----------------------------------------
        # VISION
        # ----------------------------------------
        with tab3:
            vision = results.get("vision", {})
            st.json(vision)

        # ----------------------------------------
        # INSIGHTS
        # ----------------------------------------
        with tab4:
            show_insights_panel(results)

        # ----------------------------------------
        # DOMAIN
        # ----------------------------------------
        with tab5:
            st.json(results.get("power"))
            st.json(results.get("signal"))
            st.json(results.get("thermal"))
            st.json(results.get("layout"))

        # ----------------------------------------
        # GRAPH
        # ----------------------------------------
        with tab6:
            st.json(g_summary)
            st.json(rule_issues)

        # ----------------------------------------
        # DEBUG
        # ----------------------------------------
        with tab7:
            if show_debug:
                st.json(results)

        # ----------------------------------------
        #  CHAT (FINAL FIX)
        # ----------------------------------------
        with tab8:
            show_chat_panel(results)

        # ----------------------------------------
        # CLEANUP
        # ----------------------------------------
        if cleanup_files_flag:
            safe_delete(file_path)

    except Exception as e:

        st.error("❌ Error")
        st.text(str(e))
        st.text(traceback.format_exc())

# ----------------------------------------
# FOOTER
# ----------------------------------------
st.markdown("---")
st.markdown("⚡ PragyanAI | PCB Copilot | AI Debugging System")
