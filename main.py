# import json
#
# import cv2
# from ultralytics import YOLO
#
# zones_config_file = 'restricted_zones.json'
# source = 'sources/test.mp4'
#
# with open(zones_config_file, 'r', encoding='utf-8') as f:
#     zone_config = json.load(f)
#
# cap = cv2.VideoCapture(source)
# model = YOLO("yolo11m.pt")
#
#
# # Check if camera opened successfully
# if (cap.isOpened() == False):
#     print("Error opening video stream or file")
#
# while (cap.isOpened()):
#     ret, frame = cap.read()
#     if ret:
#         results = model.predict(source=frame, device=0, half=True, verbose=False, ) #classes=[0],
#         result = results[0]
#
#         xyxy = result.boxes.xyxy.cpu().numpy()
#         boxes = [list(map(int, box)) for box in xyxy]
#         for bbox in boxes:
#             cv2.rectangle(frame, bbox[:2], bbox[2:], (255, 255, 255))
#         cv2.imshow('Frame', frame)
#
#         if cv2.waitKey(25) & 0xFF == ord('q'):
#             break
#
#     else:
#         break
#
# cap.release()
#
# # Closes all the frames
# cv2.destroyAllWindows()


from core.monitor import SecurityMonitor


def main():
    monitor = SecurityMonitor(
        video_source="sources/test.mp4",
        output="output.mp4"
    )
    monitor.run()


if __name__ == "__main__":
    main()
