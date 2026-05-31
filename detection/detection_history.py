import json
from dataclasses import asdict

from config.settings import SAVE_ALL_DETECTIONS, DETECTION_HISTORY_PATH


class DetectionHistory:

    def __init__(self):
        self.path = DETECTION_HISTORY_PATH

    def save(self, signal):

        if not SAVE_ALL_DETECTIONS and not signal.trigger:
            return

        data = asdict(signal)
        data["timestamp"] = data["timestamp"].isoformat()

        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")