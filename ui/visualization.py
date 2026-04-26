# ui/visualization.py

"""
Advanced PCB Visualization Module

✔ YOLO bounding boxes
✔ Issue overlays (LLM)
✔ Segmentation heatmap
✔ Layer toggles
✔ Safe image handling
✔ Streamlit UI ready
"""

from PIL import Image, ImageDraw
import streamlit as st
import os


# ----------------------------------------
# COLOR MAP
# ----------------------------------------
COLOR_MAP = {
    "high": (255, 0, 0),
    "medium": (255, 165, 0),
    "low": (255, 255, 0)
}


# ----------------------------------------
# SAFE IMAGE LOADER
# ----------------------------------------
def load_image(image_path):

    if not image_path or not os.path.exists(image_path):
        st.error("❌ Invalid image path")
        return None

    try:
        return Image.open(image_path).convert("RGB")
    except Exception as e:
        st.error(f"Image load failed: {e}")
        return None


# ----------------------------------------
# DRAW COMPONENTS (YOLO)
# ----------------------------------------
def draw_components(image, components):

    draw = ImageDraw.Draw(image)

    for comp in components:

        bbox = comp.get("bbox")
        label = comp.get("component", "unknown")
        conf = comp.get("confidence", 0)

        if isinstance(bbox, list) and len(bbox) == 4:

            draw.rectangle(bbox, outline="blue", width=2)

            text = f"{label} ({round(conf,2)})"
            draw.text((bbox[0], bbox[1] - 12), text, fill="blue")

    return image


# ----------------------------------------
# DRAW ISSUES (LLM)
# ----------------------------------------
def draw_issues(image, issues):

    draw = ImageDraw.Draw(image)

    for issue in issues:

        loc = issue.get("location")
        severity = issue.get("severity", "medium").lower()

        color = COLOR_MAP.get(severity, (255, 255, 255))

        if isinstance(loc, list) and len(loc) == 4:

            draw.rectangle(loc, outline=color, width=3)

            label = f"{severity.upper()}"
            draw.text((loc[0], loc[1] - 12), label, fill=color)

    return image


# ----------------------------------------
# SEGMENTATION HEATMAP
# ----------------------------------------
def draw_segmentation(image, segmentation):

    draw = ImageDraw.Draw(image, "RGBA")
    regions = segmentation.get("regions", [])
    for r in regions:
        bbox = r.get("bbox")
        density = r.get("density", 0.5)
        if isinstance(bbox, list) and len(bbox) == 4:
            opacity = int(50 + density * 150)
            draw.rectangle(
                bbox,
                fill=(255, 0, 0, opacity)
            )
    return image
# ----------------------------------------
# COMPONENT SUMMARY
# ----------------------------------------
def component_summary(components):
    summary = {}
    for comp in components:
        name = comp.get("component", "unknown")
        summary[name] = summary.get(name, 0) + 1

    return summary
# ----------------------------------------
# CORE VISUALIZATION
# ----------------------------------------
#def visualize_pcb(
#    image_path,
#    vision_output=None,
#    issues=None,
#    show_components=True,
#    show_issues=True,
#    show_heatmap=True
#):
def visualize_pcb(
    image_path,
    vision_output=None,
    issues=None,
    show_boxes=True,
    show_heatmap=True
):
    image = load_image(image_path)
    if image is None:
        return None

    components = []
    segmentation = {}

    if vision_output:
        structured = vision_output.get("structured", {})
        components = structured.get("components", [])
        segmentation = structured.get("segmentation", {})

    # Layer 1: Segmentation (bottom)
    if show_heatmap:
        image = draw_segmentation(image, segmentation)
    
    show_components = True
    # Layer 2: Components
    if show_components:
        image = draw_components(image, components)

    # Layer 3: Issues
    if show_issues and issues:
        image = draw_issues(image, issues)
    return image
# ----------------------------------------
#  STREAMLIT DISPLAY
# ----------------------------------------
def show_visualization(
    image_path,
    results,
    show_boxes=True,
    show_heatmap=True
):
#def show_visualization(image_path, results):

    st.subheader("PragyanAI PCB Visualization")

    # ----------------------------------------
    # 🎛️ LAYER CONTROLS
    # ----------------------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        show_components = st.checkbox("Show Components", True)

    with col2:
        show_issues = st.checkbox("Show Issues", True)

    with col3:
        show_heatmap = st.checkbox("Show Heatmap", True)

    vision_output = results.get("vision", {})
    issues = results.get("final", {}).get("issues", [])

   # image = visualize_pcb(
   #     image_path,
   #     vision_output=vision_output,
   #     issues=issues,
   #     show_components=show_components,
   #     show_issues=show_issues,
   #     show_heatmap=show_heatmap
   #)
    image = visualize_pcb(
        image_path,
        vision_output=vision_output,
        issues=issues,
        show_boxes=show_boxes,
        show_heatmap=show_heatmap
    )
    if image:
        st.image(image, use_container_width=True)

    # ----------------------------------------
    #  COMPONENT STATS
    # ----------------------------------------
    components = vision_output.get("structured", {}).get("components", [])

    if components:
        st.subheader("📊 Component Breakdown")
        st.json(component_summary(components))


# ----------------------------------------
# 🔍 DEBUG MODE
# ----------------------------------------
def debug_visualization(image_path, vision_output):

    st.subheader("🔍 Debug Visualization")

    image = visualize_pcb(
        image_path,
        vision_output=vision_output,
        issues=[]
    )

    if image:
        st.image(image)

    st.json(vision_output)
