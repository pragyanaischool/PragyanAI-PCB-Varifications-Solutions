"""
Unified PCB Perception Pipeline

Combines:
- Component Detection (YOLO / fallback)
- OCR (text + component labels)
- Segmentation (trace density / congestion)

Output:
Structured perception data for downstream agents
"""

from typing import Dict, Any

# Local model modules
from models.ocr_model import extract_text
from models.yolo_detector import PCBDetector
from models.segmentation_model import PCBSegmentation


# ----------------------------------------
# 🧠 MAIN PIPELINE CLASS
# ----------------------------------------
class PCBPipeline:

    def __init__(self):

        # Initialize models (safe / lightweight)
        self.detector = PCBDetector()
        self.segmenter = PCBSegmentation()

    # ----------------------------------------
    # 🚀 MAIN ENTRY
    # ----------------------------------------
    def run(self, image_path: str) -> Dict[str, Any]:

        result = {
            "components": [],
            "ocr": {},
            "segmentation": {},
            "metadata": {},
            "errors": []
        }

        # ----------------------------------------
        # 🔍 COMPONENT DETECTION
        # ----------------------------------------
        try:
            detections = self.detector.detect(image_path)
            result["components"] = detections
        except Exception as e:
            result["errors"].append(f"Detection error: {str(e)}")

        # ----------------------------------------
        # 🔤 OCR
        # ----------------------------------------
        try:
            ocr_data = extract_text(image_path)
            result["ocr"] = ocr_data
        except Exception as e:
            result["errors"].append(f"OCR error: {str(e)}")

        # ----------------------------------------
        # 🧩 SEGMENTATION
        # ----------------------------------------
        try:
            segmentation = self.segmenter.segment(image_path)
            result["segmentation"] = segmentation
        except Exception as e:
            result["errors"].append(f"Segmentation error: {str(e)}")

        # ----------------------------------------
        # 🧠 POST-PROCESSING
        # ----------------------------------------
        result["metadata"] = self._build_metadata(result)

        return result

    # ----------------------------------------
    # 🧠 METADATA BUILDER
    # ----------------------------------------
    def _build_metadata(self, data: Dict) -> Dict:

        components = data.get("components", [])
        ocr = data.get("ocr", {})
        segmentation = data.get("segmentation", {})

        component_count = len(components)

        detected_types = list(set([
            c.get("component", "unknown")
            for c in components
        ]))

        ocr_components = ocr.get("components", [])

        trace_density = segmentation.get("trace_density", "unknown")

        return {
            "component_count": component_count,
            "component_types": detected_types,
            "ocr_component_labels": ocr_components,
            "trace_density": trace_density,
            "has_errors": len(data.get("errors", [])) > 0
        }

    # ----------------------------------------
    # ⚡ QUICK MODE (FAST)
    # ----------------------------------------
    def quick_run(self, image_path: str) -> Dict:

        try:
            ocr = extract_text(image_path)

            return {
                "ocr": ocr,
                "mode": "quick"
            }

        except Exception as e:
            return {
                "error": str(e),
                "mode": "quick"
            }

    # ----------------------------------------
    # 🔄 SAFE RUN (NO CRASH GUARANTEE)
    # ----------------------------------------
    def safe_run(self, image_path: str) -> Dict:

        try:
            return self.run(image_path)

        except Exception as e:
            return {
                "components": [],
                "ocr": {},
                "segmentation": {},
                "metadata": {},
                "errors": [f"Pipeline failed: {str(e)}"]
            }


# ----------------------------------------
# 🔧 UTILITY FUNCTION (OPTIONAL)
# ----------------------------------------
def run_pipeline(image_path: str) -> Dict:
    """
    Simple wrapper for external use
    """

    pipeline = PCBPipeline()
    return pipeline.safe_run(image_path)
