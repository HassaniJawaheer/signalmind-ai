import json
from dataclasses import asdict
from config.settings import SAVE_ALL_DETECTIONS,DETECTION_HISTORY_PATH

class DetectionHistory:
    def __init__(self):

        self.path = DETECTION_HISTORY_PATH


    def save(self, signal):


        if not SAVE_ALL_DETECTIONS:

            if not signal.trigger:

                return


        with open(

            self.path,

            "a",

            encoding="utf-8"

        ) as f:


            json.dump(

                asdict(signal),

                f
            )

            f.write("\n")