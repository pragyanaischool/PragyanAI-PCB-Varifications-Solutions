# models/pipeline.py

"""
Unified PCB Perception Pipeline (Enhanced)

Combines:
- YOLO Detection
- OCR
- Segmentation

Adds:
✔ Fusion (OCR + detection)
✔ Normalization
✔ Confidence scoring
✔ Robust error handling
✔ Metadata enrichment
"""

from typing import Dict, Any
import time

from models.ocr_model import extract_text
from models.yolo_detector import PCBDetector
from models.segmentation_model import PCBSegmentation


# ----------------------------------------
# 🧠 MAIN PIPELINE CLASS
# ----------------------------------------
class PCBPipeline:

    def __init__(self):

        self.detector = PCBDetector()
        self.segmenter = PCBSegmentation()

    # ----------------------------------------
    # 🚀 MAIN RUN
    # ----------------------------------------
    def run(self, image_path: str) -> Dict[str, Any]:

        start_time = time.time()

        result = {
            "components": [],
            "ocr": {},
            "segmentation": {},
            "metadata": {},
            "errors": [],
            "timings": {}
        }

        # ----------------------------------------
        # 🔍 DETECTION
        # ----------------------------------------
        t0 = time.time()
        try:
            detections = self.detector.detect(image_path)
            result["components"] = self._normalize_components(detections)
        except Exception as e:
            result["errors"].append(f"Detection error: {str(e)}")
        result["timings"]["detection"] = round(time.time() - t0, 2)

        # ----------------------------------------
        # 🔤 OCR
        # ----------------------------------------
        t0 = time.time()
        try:
            ocr_data = extract_text(image_path)
            result["ocr"] = self._normalize_ocr(ocr_data)
        except Exception as e:
            result["errors"].append(f"OCR error: {str(e)}")
        result["timings"]["ocr"] = round(time.time() - t0, 2)

        # ----------------------------------------
        # 🧩 SEGMENTATION
        # ----------------------------------------
        t0 = time.time()
        try:
            segmentation = self.segmenter.segment(image_path)
            result["segmentation"] = segmentation
        except Exception as e:
            result["errors"].append(f"Segmentation error: {str(e)}")
        result["timings"]["segmentation"] = round(time.time() - t0, 2)

        # ----------------------------------------
        # 🔗 FUSION (IMPORTANT)
        # ----------------------------------------
        result["components"] = self._fuse_components(
            result["components"],
            result["ocr"]
        )

        # ----------------------------------------
        # 🧠 METADATA
        # ----------------------------------------
        result["metadata"] = self._build_metadata(result)

        result["timings"]["total"] = round(time.time() - start_time, 2)

        return result

    # ----------------------------------------
    # 🧠 NORMALIZE COMPONENTS
    # ----------------------------------------
    def _normalize_components(self, detections):

        normalized = []

        for d in detections:

            bbox = d.get("bbox", [])

            # Ensure bbox format
            if not isinstance(bbox, list) or len(bbox) != 4:
                bbox = None

            normalized.append({
                "component": d.get("component", "unknown"),
                "bbox": bbox,
                "confidence": d.get("confidence", 0.7)
            })

        return normalized

    # ----------------------------------------
    # 🧠 NORMALIZE OCR
    # ----------------------------------------
    def _normalize_ocr(self, ocr_data):

        text = (
            ocr_data.get("full_text")
            or ocr_data.get("text")
            or ""
        )

        lines = ocr_data.get("lines", text.split("\n"))

        return {
            "text": text,
            "lines": lines,
            "components": ocr_data.get("components", [])
        }

    # ----------------------------------------
    # 🔗 FUSION LOGIC
    # ----------------------------------------
    def _fuse_components(self, components, ocr):

        ocr_labels = set(ocr.get("components", []))

        for comp in components:
            name = comp.get("component")

            # Boost confidence if OCR confirms
            if name in ocr_labels:
                comp["confidence"] = min(1.0, comp["confidence"] + 0.2)
                comp["verified_by_ocr"] = True
            else:
                comp["verified_by_ocr"] = False

        return components

    # ----------------------------------------
    # 🧠 METADATA BUILDER
    # ----------------------------------------
    def _build_metadata(self, data: Dict) -> Dict:

        components = data.get("components", [])
        ocr = data.get("ocr", {})
        segmentation = data.get("segmentation", {})

        component_count = len(components)

        types = list(set([
            c.get("component", "unknown")
            for c in components
        ]))

        trace_density = segmentation.get("trace_density", "unknown")

        high_conf = [
            c for c in components if c.get("confidence", 0) > 0.8
        ]

        return {
            "component_count": component_count,
            "component_types": types,
            "high_conf_components": len(high_conf),
            "ocr_labels": ocr.get("components", []),
            "trace_density": trace_density,
            "has_errors": len(data.get("errors", [])) > 0
        }

    # ----------------------------------------
    # ⚡ QUICK MODE
    # ----------------------------------------
    def quick_run(self, image_path: str) -> Dict:

        try:
            ocr = extract_text(image_path)

            return {
                "ocr": self._normalize_ocr(ocr),
                "mode": "quick"
            }

        except Exception as e:
            return {
                "error": str(e),
                "mode": "quick"
            }

    # ----------------------------------------
    # 🔄 SAFE RUN
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
# 🔧 UTILITY FUNCTION
# ----------------------------------------
def run_pipeline(image_path: str) -> Dict:

    pipeline = PCBPipeline()
    return pipeline.safe_run(image_path)
    
