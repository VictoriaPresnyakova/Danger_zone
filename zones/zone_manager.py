import json
import numpy as np
import cv2
from pathlib import Path


class ZoneManager:

    @staticmethod
    def load_zones(config_path):
        if Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f).get("restricted_zones", [])
        return []

    @staticmethod
    def save_zones(zones, config_path, video_source, frame_size):
        config = {
            "video_source": video_source,
            "frame_size": frame_size,
            "restricted_zones": zones
        }
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

    @staticmethod
    def draw_zones(frame, zones):
        for zone in zones:
            if len(zone) > 2:
                pts = np.array(zone, np.int32)
                cv2.polylines(frame, [pts], True, (0, 0, 255), 2)
        return frame
