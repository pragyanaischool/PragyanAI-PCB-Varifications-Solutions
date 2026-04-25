# ui/visualization.py

"""
PCB Visualization Module

Features:
- Draw component bounding boxes
- Highlight issues (severity-based)
- Heatmap overlay
- Streamlit display
"""

from PIL import Image, ImageDraw, ImageFont
import streamlit as st


# ----------------------------------------
# 🎨 COLOR MAP (SEVERITY)
# ----------------------------------------
COLOR_MAP = {
    "high": "red",
    "medium": "orange",
    "low": "yellow"
}


# ----------------------------------------
# 🧠 LOAD IMAGE SAFELY
# ----------------------------------------
def load_image(image_path):

    try:
        return Image.open(image_path).convert("RGB")
    except Exception as e:
        st.error(f"Image load failed: {e}")
        return None


# ----------------------------------------
# 📦 DRAW COMPONENT BOUNDING BOXES
# ----------------------------------------
def draw_components(image, components):

    draw = ImageDraw.Draw(image)

    for comp in components:
        bbox = comp.get("bbox", [])
        label = comp.get("component", "unknown")

        if len(bbox) == 4:
            draw.rectangle(bbox, outline="blue", width=2)
            draw.text((bbox[0], bbox[1] - 10), label, fill="blue")

    return image


# ----------------------------------------
# 🔥 DRAW ISSUES OVERLAY
# ----------------------------------------
def draw_issues(image, issues):

    draw = ImageDraw.Draw(image)

    for issue in issues:
        severity = issue.get("severity", "medium").lower()
        color = COLOR_MAP.get(severity, "white")

        location = issue.get("location")

        # If bounding box available
        if isinstance(location, list) and len(location) == 4:
            draw.rectangle(location, outline=color, width=3)
            draw.text((location[0], location[1] - 10), severity.upper(), fill=color)

    return image


# ----------------------------------------
# 🌡️ HEATMAP EFFECT (SIMPLIFIED)
# ----------------------------------------
def draw_heatmap(image, issues):

    draw = ImageDraw.Draw(image, "RGBA")

    for issue in issues:
        severity = issue.get("severity", "medium").lower()

        opacity = 80
        if severity == "high":
            opacity = 150
        elif severity == "medium":
            opacity = 100

        location = issue.get("location")

        if isinstance(location, list) and len(location) == 4:
            overlay_color = (255, 0, 0, opacity)
            draw.rectangle(location, fill=overlay_color)

    return image


# ----------------------------------------
# 📊 COMPONENT SUMMARY
# ----------------------------------------
def component_summary(components):

    summary = {}

    for comp in components:
        name = comp.get("component", "unknown")
        summary[name] = summary.get(name, 0) + 1

    return summary


# ----------------------------------------
# 🖼️ MAIN VISUALIZATION PIPELINE
# ----------------------------------------
def visualize_pcb(
    image_path,
    vision_output=None,
    issues=None,
    show_boxes=True,
    show_heatmap=True
):

    image = load_image(image_path)

    if image is None:
        return

    components = []
    if vision_output:
        components = vision_output.get("structured", {}).get("components", [])

    # Draw components
    if show_boxes:
        image = draw_components(image, components)

    # Draw issues
    if issues:
        image = draw_issues(image, issues)

    # Draw heatmap
    if show_heatmap and issues:
        image = draw_heatmap(image, issues)

    return image


# ----------------------------------------
# 📺 STREAMLIT DISPLAY
# ----------------------------------------
def show_visualization(image_path, results):

    st.subheader("🖼️ PCB Visualization")

    vision_output = results.get("vision", {})
    issues = results.get("final", {}).get("issues", [])

    image = visualize_pcb(
        image_path,
        vision_output=vision_output,
        issues=issues
    )

    if image:
        st.image(image, use_container_width=True)

    # ----------------------------------------
    # 📊 COMPONENT STATS
    # ----------------------------------------
    components = vision_output.get("structured", {}).get("components", [])
    summary = component_summary(components)

    if summary:
        st.subheader("📊 Component Breakdown")
        st.json(summary)


# ----------------------------------------
# 🔍 DEBUG VIEW
# ----------------------------------------
def debug_visualization(image_path, vision_output):

    st.subheader("🔍 Debug Visualization")

    components = vision_output.get("structured", {}).get("components", [])

    image = visualize_pcb(
        image_path,
        vision_output=vision_output,
        issues=[]
    )

    if image:
        st.image(image)

    st.json(components)
