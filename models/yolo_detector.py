"""
PCB Component Detector (YOLO / Safe Fallback)

Modes:
- "mock"  → default (no heavy deps, works everywhere)
- "yolo"  → uses Ultralytics YOLO if installed

Output format:
[
    {
        "component": "IC",
        "bbox": [x1, y1, x2, y2],
        "confidence": 0.91,
        "class_id": 0
    },
    ...
]
"""

from typing import List, Dict, Any
import random

# Optional YOLO import
try:
    from ultralytics import YOLO
except Exception:
    YOLO = None


# ----------------------------------------
# 🧠 MAIN DETECTOR CLASS
# ----------------------------------------
class PCBDetector:

    def __init__(self, model_path: str = None, mode: str = "mock"):
        """
        mode:
            - "mock" → safe default
            - "yolo" → use real YOLO if available
        """

        self.mode = mode

        if self.mode == "yolo" and YOLO is not None:
            try:
                self.model = YOLO(model_path or "yolov8n.pt")
            except Exception:
                self.model = None
                self.mode = "mock"
        else:
            self.model = None
            self.mode = "mock"

    # ----------------------------------------
    # 🚀 MAIN DETECTION
    # ----------------------------------------
    def detect(self, image_path: str) -> List[Dict[str, Any]]:

        if self.mode == "yolo" and self.model:
            return self._detect_yolo(image_path)

        return self._detect_mock(image_path)

    # ----------------------------------------
    # 🤖 REAL YOLO DETECTION (OPTIONAL)
    # ----------------------------------------
    def _detect_yolo(self, image_path: str):

        try:
            results = self.model(image_path)

            detections = []

            for r in results:
                if not hasattr(r, "boxes"):
                    continue

                for box in r.boxes:
                    bbox = box.xyxy.tolist()[0]

                    detections.append({
                        "component": self._map_class(int(box.cls)),
                        "bbox": [float(x) for x in bbox],
                        "confidence": float(box.conf),
                        "class_id": int(box.cls)
                    })

            return detections

        except Exception as e:
            return [{
                "error": f"YOLO detection failed: {str(e)}"
            }]

    # ----------------------------------------
    # 🧪 MOCK DETECTION (SAFE)
    # ----------------------------------------
    def _detect_mock(self, image_path: str):

        components = ["IC", "Resistor", "Capacitor", "Diode"]

        detections = []

        for i in range(random.randint(2, 5)):
            x1 = random.randint(10, 200)
            y1 = random.randint(10, 200)
            x2 = x1 + random.randint(40, 120)
            y2 = y1 + random.randint(40, 120)

            detections.append({
                "component": random.choice(components),
                "bbox": [x1, y1, x2, y2],
                "confidence": round(random.uniform(0.6, 0.95), 2),
                "class_id": i
            })

        return detections

    # ----------------------------------------
    # 🧠 CLASS MAPPING (OPTIONAL)
    # ----------------------------------------
    def _map_class(self, class_id: int) -> str:

        mapping = {
            0: "IC",
            1: "Resistor",
            2: "Capacitor",
            3: "Diode",
            4: "Transistor"
        }

        return mapping.get(class_id, "Unknown")


# ----------------------------------------
# ⚡ QUICK UTILITY FUNCTION
# ----------------------------------------
def detect_components(image_path: str):

    detector = PCBDetector(mode="mock")  # change to "yolo" later
    return detector.detect(image_path)
