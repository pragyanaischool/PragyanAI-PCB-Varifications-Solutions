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
# 🎨 PAGE CONFIG
# ----------------------------------------
st.set_page_config(
    page_title="PragyanAI PCB Copilot",
    layout="wide",
    page_icon="⚡"
)

# ----------------------------------------
# 🧠 HEADER
# ----------------------------------------
st.title("⚡ PragyanAI PCB Copilot")
st.caption("Multi-Agent AI for PCB Analysis (Vision + Graph + GNN + LLM)")


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

    st.markdown("### ℹ️ Features")
    st.markdown("""
    - Vision (YOLO + OCR + Segmentation)
    - Graph + GNN
    - Multi-Agent AI
    - Fix Recommendation Engine
    """)


# ----------------------------------------
# 📤 FILE UPLOAD
# ----------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    pcb_file = st.file_uploader(
        "Upload PCB Image",
        type=["png", "jpg", "jpeg"]
    )

with col2:
    st.markdown("### 🧩 Supported")
    st.markdown("""
    - PCB Images  
    - (Netlist support coming)  
    """)


# ----------------------------------------
# 🖼️ IMAGE PREVIEW
# ----------------------------------------
if pcb_file:
    image = Image.open(pcb_file)
    st.image(image, caption="PCB Preview", use_container_width=True)


# ----------------------------------------
# 🚀 RUN ANALYSIS
# ----------------------------------------
if pcb_file:

    if st.button("🚀 Run AI Analysis"):

        try:
            with st.spinner("Running AI pipeline..."):

                # ----------------------------------------
                # 💾 SAVE FILE
                # ----------------------------------------
                file_path = save_uploaded_file(pcb_file)

                # ----------------------------------------
                # 🧠 PARSE
                # ----------------------------------------
                pcb_data = parse_pcb(file_path)

                # ----------------------------------------
                # 🔗 GRAPH
                # ----------------------------------------
                graph = build_graph(pcb_data)
                g_summary = graph_summary(graph)

                # ----------------------------------------
                # ⚠️ RULE ENGINE
                # ----------------------------------------
                rule_issues = run_rules(graph)

                # ----------------------------------------
                # 🤖 AI ORCHESTRATOR
                # ----------------------------------------
                result = run_full_analysis(
                    image_path=file_path,
                    graph_summary=g_summary,
                    gnn_output=None,
                    ocr_text=None
                )

                results = result["results"]

                # ----------------------------------------
                # 📊 REPORT
                # ----------------------------------------
                report = build_full_system_report(results)

            st.success("✅ Analysis Completed")

            # ----------------------------------------
            # 📊 TABS
            # ----------------------------------------
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🧠 Final Report",
                "🖼️ Visual Debugger",
                "⚡ Domain Insights",
                "📊 Graph & Rules",
                "🔍 Debug"
            ])

            # ----------------------------------------
            # 🧠 FINAL REPORT
            # ----------------------------------------
            with tab1:

                st.metric("PCB Score", report.get("score", 0))

                st.subheader("📋 Summary")
                st.write(report.get("summary", ""))

                st.subheader("⚠️ Issues")
                st.json(report.get("issues", []))

                st.subheader("🔧 Recommended Actions")
                st.json(report.get("recommended_actions", []))

                st.download_button(
                    "📄 Download Report",
                    report_to_markdown(report),
                    file_name="pcb_report.md"
                )

            # ----------------------------------------
            # 🖼️ VISUAL DEBUGGER
            # ----------------------------------------
            with tab2:

                show_visualization(file_path, results)

            # ----------------------------------------
            # ⚡ DOMAIN AGENTS
            # ----------------------------------------
            with tab3:

                colA, colB = st.columns(2)

                with colA:
                    st.subheader("⚡ Power")
                    st.json(results.get("power"))

                    st.subheader("🔌 Signal")
                    st.json(results.get("signal"))

                with colB:
                    st.subheader("🌡️ Thermal")
                    st.json(results.get("thermal"))

                    st.subheader("🧩 Layout")
                    st.json(results.get("layout"))

            # ----------------------------------------
            # 📊 GRAPH + RULES
            # ----------------------------------------
            with tab4:

                st.subheader("Graph Summary")
                st.json(g_summary)

                st.subheader("Rule Issues")
                st.json(rule_issues)

            # ----------------------------------------
            # 🔍 DEBUG
            # ----------------------------------------
            if show_debug:
                with tab5:
                    st.subheader("Full System Output")
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
# 🧭 FOOTER
# ----------------------------------------
st.markdown("---")
st.markdown("⚡ PragyanAI | PCB Copilot | Multi-Agent AI System")

