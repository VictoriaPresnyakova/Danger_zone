import os
import time

import cv2
import torch.cuda
from ultralytics import YOLO

from alarm.alarm_system import AlarmSystem
from ml.tracker import ObjectTracker
from utils.geometry import point_in_polygon
from zones.zone_editor import ZoneEditor
from zones.zone_manager import ZoneManager


class FPSCounter:
    def __init__(self, avg_frames=30):
        self.prev_time = time.time()
        self.fps = 0.0
        self.times = []
        self.avg_frames = avg_frames

    def update(self):
        now = time.time()
        dt = now - self.prev_time
        self.prev_time = now

        self.times.append(dt)
        if len(self.times) > self.avg_frames:
            self.times.pop(0)

        self.fps = 1.0 / (sum(self.times) / len(self.times))
        return self.fps


class SecurityMonitor:

    def __init__(self, video_source, output, save_video=False, model_path="yolo11n.pt"):
        os.makedirs("output_videos", exist_ok=True)
        self.output_path = f"output_videos/{output}"
        self.save_video = save_video

        self.video_source = video_source
        self.config_path = "restricted_zones.json"

        self.zones = ZoneManager.load_zones(self.config_path)
        self.alarm = AlarmSystem()
        self.tracker = ObjectTracker()

        self.model = YOLO(model_path)

        self.frame_count = 0
        self.persons_in_zones = set()

        self.fps_counter = FPSCounter()

    def run(self):
        cap = cv2.VideoCapture(self.video_source)
        if not cap.isOpened():
            print("Ошибка открытия видео")
            return

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        if self.save_video:
            out = cv2.VideoWriter(self.output_path, fourcc, fps, (width, height))

        pause = False

        while True:
            if not pause:
                ret, frame = cap.read()
                if not ret:
                    break

                self.frame_count += 1
                self._process_frame(frame)

            display = frame.copy()
            self._draw_ui(display, pause)

            fps = self.fps_counter.update()
            cv2.putText(display, f"FPS: {fps:.1f}", (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.imshow("Security Monitor", display)
            if self.save_video:
                out.write(display)

            key = cv2.waitKey(25 if not pause else 0) & 0xFF

            if key == ord('q'):
                break
            elif key == ord('e'):
                self._edit_zones(cap, width, height)
            elif key == ord('p'):
                pause = not pause

        cap.release()
        cv2.destroyAllWindows()

    def _process_frame(self, frame):
        self.alarm.update()

        results = self.model.predict(frame, classes=[0], verbose=False, device=0 if torch.cuda.is_available() else 'cpu', imgsz=1280, iou=0.5, half=True)[0]

        detections = []
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])

            detections.append(([x1, y1, x2 - x1, y2 - y1], conf, cls_id))

        tracks = self.tracker.update(detections, frame=frame)

        current_in_zones = set()
        for track in tracks:
            bbox = track['bbox']
            center = track['center']
            track_id = track['id']

            in_zone = self._check_point_in_zones(center)

            color = (0, 0, 255) if in_zone else (0, 255, 0)
            cv2.rectangle(frame, bbox[:2], bbox[2:], color, 2)
            cv2.putText(frame, f"ID:{track_id}", (bbox[0], bbox[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            if in_zone:
                current_in_zones.add(track_id)

        self.persons_in_zones = current_in_zones
        if self.persons_in_zones:
            self.alarm.trigger()

    def _check_point_in_zones(self, point):
        for zone in self.zones:
            if len(zone) > 2 and point_in_polygon(point, zone):
                return True
        return False

    def _draw_ui(self, frame, pause):
        ZoneManager.draw_zones(frame, self.zones)

        self.alarm.draw(frame)

        stats = [
            f"Frame: {self.frame_count}",
            f"Persons in zones: {len(self.persons_in_zones)}",
            f"Zones: {len(self.zones)}",
            f"Alarm: {'ON' if self.alarm.active else 'OFF'}",
            f"Status: {'PAUSED' if pause else 'RUNNING'}",
            "Settings: 'q' - exit, 'e' - edit zones, 'p' - pause"
        ]

        y = frame.shape[0] - 175
        for stat in stats:
            cv2.putText(frame, stat, (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y += 25

    def _edit_zones(self, cap, width, height):
        cap.release()
        cv2.destroyAllWindows()

        editor = ZoneEditor(self.video_source)
        new_zones = editor.run(self.zones)

        if new_zones != self.zones:
            self.zones = new_zones
            ZoneManager.save_zones(self.zones, self.config_path,
                                   self.video_source, {"width": width, "height": height})
            print(f"Зоны обновлены: {len(self.zones)} зон")

        # reopen
        return cv2.VideoCapture(self.video_source)