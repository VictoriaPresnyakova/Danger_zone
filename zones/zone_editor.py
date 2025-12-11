import cv2
import numpy as np


class ZoneEditor:
    def __init__(self, video_source):
        self.video_source = video_source
        self.cap = cv2.VideoCapture(video_source)
        self.zones = []
        self.current_zone = []
        self.window_name = "Zone Editor"

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.current_zone.append([x, y])
        elif event == cv2.EVENT_RBUTTONDOWN and len(self.current_zone) > 2:
            self.zones.append(self.current_zone.copy())
            self.current_zone = []

    def run(self, existing_zones=None):
        if existing_zones:
            self.zones = existing_zones.copy()

        ret, frame = self.cap.read()
        if not ret:
            return self.zones

        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        instructions = [
            "Left Click: Add point",
            "Right Click: Finish zone",
            "Press 's' to Save",
            "Press 'q' to Quit without saving"
        ]

        while True:
            display = frame.copy()

            for zone in self.zones:
                if len(zone) > 2:
                    pts = np.array(zone, np.int32)
                    cv2.fillPoly(display, [pts], (0, 0, 100))
                    cv2.polylines(display, [pts], True, (0, 0, 255), 2)

            if self.current_zone:
                pts = np.array(self.current_zone, np.int32)
                if len(self.current_zone) > 1:
                    cv2.polylines(display, [pts], False, (0, 255, 0), 2)
                for point in self.current_zone:
                    cv2.circle(display, tuple(point), 3, (0, 255, 0), -1)

            y = 30
            for line in instructions:
                cv2.putText(display, line, (10, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                y += 25

            cv2.imshow(self.window_name, display)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('s'):
                break
            elif key == ord('q'):
                self.zones = existing_zones if existing_zones else []
                break

        cv2.destroyWindow(self.window_name)
        self.cap.release()
        return self.zones
