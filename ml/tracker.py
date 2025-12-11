import torch
from deep_sort_realtime.deepsort_tracker import DeepSort


class ObjectTracker:
    def __init__(self):
        self.tracker = DeepSort(max_age=20, embedder="mobilenet", embedder_gpu=True if torch.cuda.is_available() else False, half=True)

    def update(self, detections, frame):
        tracks = self.tracker.update_tracks(detections, frame=frame)
        result = []

        for track in tracks:
            if track.is_confirmed():
                bbox = track.to_tlbr().astype(int)
                result.append({
                    "id": track.track_id,
                    "bbox": bbox,
                    "center": self._center(bbox)
                })
        return result

    @staticmethod
    def _center(b):
        return ((b[0] + b[2]) // 2, (b[1] + b[3]) // 2)
