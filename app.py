import os
import sys
import traceback
from PIL import Image
import streamlit as st

os.environ["ULTRALYTICS_NO_AUTO_INSTALL"] = "1"

# ----------------------------------------
# Services
# ----------------------------------------
from services.graph import build_graph, graph_summary
from services.parser import parse_pcb
from services.report import build_full_system_report, report_to_markdown
from services.rules import run_rules

# RAG
from ai.vector_store import build_vector_store
from services.pdf_parser import parse_pdf

# AI Orchestrator
from ai.orchestrator import run_full_analysis

# UI
from ui.chat_panel import chat_controls, show_chat_panel
from ui.insights_panel import show_insights_panel
from ui.visualization import show_visualization

# Utils
from utils.file import safe_delete, save_uploaded_file
import os
import sys
from pathlib import Path

# Ensure repository root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Suppress Ultralytics permission warnings & auto-installs
os.environ["YOLO_CONFIG_DIR"] = "/tmp/Ultralytics"
os.environ["ULTRALYTICS_NO_AUTO_INSTALL"] = "1"
# ----------------------------------------
# CONFIG & STYLES
# ----------------------------------------
st.set_page_config(
    page_title="PragyanAI PCB Copilot", layout="wide", page_icon="⚡"
)

st.markdown(
    """
<style>
.block-container { padding-top: 2rem; }
h1, h2, h3 { font-weight: 600; }
.stTabs [data-baseweb="tab"] { font-size: 16px; padding: 10px 20px; }
.stButton>button { border-radius: 10px; height: 45px; }
</style>
""",
    unsafe_allow_html=True,
)

if os.path.exists("PragyanAI_Transperent.png"):
    st.image("PragyanAI_Transperent.png", width=220)
st.title("PragyanAI PCB Copilot")
st.caption("Vision + YOLO + Segmentation + Multi-Agent AI + RAG")

# ----------------------------------------
# SIDEBAR
# ----------------------------------------
with st.sidebar:
    st.header(" Settings")
    run_mode = st.selectbox(
        "Analysis Mode", ["Full (Accurate)", "Quick (Fast)"]
    )
    show_debug = st.checkbox("Show Debug Info", value=False)

    st.markdown("---")
    st.markdown("### PCB Verification Stack")
    st.markdown("""
    - Vision Defect Localization
    - IPC-A-610 Rule Checking
    - Topological Graph Engine
    - Multi-Agent Orchestration
    """)
    chat_controls()

# ----------------------------------------
# FILE UPLOADS
# ----------------------------------------
pcb_file = st.file_uploader(
    "Upload PCB Image", type=["png", "jpg", "jpeg", "webp"]
)
doc_file = st.file_uploader(
    "Upload Datasheet / Spec PDF (Optional)", type=["pdf"]
)

if doc_file:
    try:
        doc_path = save_uploaded_file(doc_file)
        pdf_data = parse_pdf(doc_path)
        if pdf_data.get("text"):
            build_vector_store(pdf_data["text"])
            st.success(" Knowledge base updated")
        else:
            st.warning("⚠️ No text extracted from PDF")
    except Exception as e:
        st.error(f"PDF error: {e}")

if pcb_file:
    try:
        image = Image.open(pcb_file)
        st.image(image, caption="PCB Preview", use_container_width=True)
    except Exception as e:
        st.warning(f"Preview not available: {e}")

# ----------------------------------------
# RUN ANALYSIS PIPELINE
# ----------------------------------------
if pcb_file and st.button("Run PCB - AI Analysis", type="primary"):
    try:
        with st.spinner("Executing PCB Vision & Multi-Agent Inspection..."):
            file_path = save_uploaded_file(pcb_file)
            if not file_path or not os.path.exists(file_path):
                st.error("❌ File saving failed")
                st.stop()

            # 1. Image Parsing & Graph Generation
            try:
                pcb_data = parse_pcb(file_path)
                graph = build_graph(pcb_data)
                g_summary = graph_summary(graph)
                rule_issues = run_rules(graph)
            except Exception as graph_err:
                g_summary = {"status": "fallback", "error": str(graph_err)}
                rule_issues = []

            # 2. Multi-Agent Vision & Domain Orchestration
            results = run_full_analysis(
                image_path=file_path,
                graph_summary=g_summary,
                gnn_output=None,
                ocr_text=None,
            )

            if not results:
                st.error("❌ Analysis returned empty results.")
                st.stop()

            # 3. Report Generation
            report = build_full_system_report(results)

            st.success("✅ Analysis Completed")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("PCB Score", report.get("score", 0))
            col2.metric("Issues Found", report.get("issue_count", 0))
            col3.metric(
                "High Severity", report.get("severity", {}).get("high", 0)
            )

            comp_count = len(
                results.get("vision", {})
                .get("structured", {})
                .get("components", [])
            )
            col4.metric("Components Identified", comp_count)

        # ----------------------------------------
        # UI TABS
        # ----------------------------------------
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "1. Final Report",
            "2. Visualization",
            "3. Vision AI",
            "4. Insights",
            "5. Domain Rules",
            "6. Graph Summary",
            "7. Debug",
            "8. Chat AI",
        ])

        with tab1:
            st.metric("PCB Health Score", report.get("score", 0))
            st.write(
                report.get("summary", "Inspection completed successfully.")
            )

            issues = report.get("issues", [])
            if issues:
                st.subheader("Detected Defect Items")
                st.json(issues)
            else:
                st.info("No critical defects flagged by standard rules.")

            st.download_button(
                " Download Inspection Report",
                report_to_markdown(report),
                file_name="pcb_inspection_report.md",
            )

        with tab2:
            show_visualization(file_path, results)

        with tab3:
            st.json(results.get("vision", {}))

        with tab4:
            show_insights_panel(results)

        with tab5:
            st.markdown("### Domain Subsystem Checks")
            st.write("**Power Analysis**")
            st.json(results.get("power", {}))
            st.write("**Signal Integrity**")
            st.json(results.get("signal", {}))
            st.write("**Thermal Distribution**")
            st.json(results.get("thermal", {}))
            st.write("**Physical Layout**")
            st.json(results.get("layout", {}))

        with tab6:
            st.markdown("### Graph Topology & Rule Violations")
            st.json(g_summary)
            st.json(rule_issues)

        with tab7:
            if show_debug:
                st.json(results)
            else:
                st.write("Enable 'Show Debug Info' in the sidebar.")

        with tab8:
            show_chat_panel(results)

    except Exception as e:
        st.error(f"❌ Error during execution: {str(e)}")
        st.code(traceback.format_exc())

# ----------------------------------------
# FOOTER
# ----------------------------------------
st.markdown("---")
st.markdown(" PragyanAI | PCB Copilot | AI Debugging System")
