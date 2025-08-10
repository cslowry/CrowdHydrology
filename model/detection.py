from ultralytics import YOLO
from ultralytics.engine.results import Results

from model.exceptions import InvalidBoxesException


# decorator for limiting bounding boxes
def limit_boxes(num_boxes: int = 2):
    def decorator(func):
        def wrapper(self, prediction: Results):
            if len(prediction.boxes) != num_boxes:
                raise InvalidBoxesException(
                    f"Expected exactly {num_boxes} bounding boxes, but got {len(prediction.boxes)}."
                )
            return prediction

        return wrapper

    return decorator


def detect_images(directory: str) -> list:
    model = YOLO("./models/best.pt")
    return model.predict(directory)


class ContributionImageDetector:
    def __init__(self, model_path: str = "./models/best.pt"):
        self.model = YOLO(model_path)

    def detect(self, image_path: str) -> list[Results]:
        return self.model.predict(image_path)

    @limit_boxes(2)
    def get_gauge_roi(self, prediction: Results):
        pass
        # label1, label2 = (
        #     prediction.boxes[0].cls.cpu().numpy().astype(int)[0],
        #     prediction.boxes[1].cls.cpu().numpy().astype(int)[0],
        # )

        # x1, y1, x2, y2 = (
        #     map(int, prediction[1].boxes[0].xyxy[0])
        #     if label1 == 0
        #     else map(int, prediction[0].boxes[0].xyxy[0])
        # )
        # stationLabel = prediction.plot(labels=False, boxes=False)[y1:y2, x1:x2]

    @limit_boxes(2)
    def get_station_label_roi(self, prediction: Results):
        pass
