import time
import cv2


class AlarmSystem:
    def __init__(self, cooldown=3.0):
        self.active = False
        self.start_time = 0
        self.cooldown = cooldown

    def trigger(self):
        if not self.active:
            self.active = True
            self.start_time = time.time()

    def update(self):
        if self.active and (time.time() - self.start_time) > self.cooldown:
            self.active = False

    def draw(self, frame):
        if self.active:
            cv2.putText(
                frame, f"ALARM {int(time.time() - self.start_time)}",
                (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3
            )
