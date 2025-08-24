from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar, Union

from google import genai
from google.genai import types
from PIL import Image
from ultralytics import YOLO
from ultralytics.engine.results import Results

from model.exceptions import InvalidBoxesException
from model.helper import Image_to_b64
from model.responses import AbstractLLMResponse, ValidMMSContribution


# decorator for limiting bounding boxes
def limit_boxes(num_boxes: int = 2):
    def decorator(func):
        def wrapper(self, prediction: Results):
            if len(prediction.boxes) != num_boxes:
                raise InvalidBoxesException(
                    "It seems that the image is not clear or is invalid. Please try again."
                )
            return func(self, prediction)

        return wrapper

    return decorator


def detect_images(directory: str) -> list:
    model = YOLO("./models/best.pt")
    return model.predict(directory)


class ContributionImageDetector:
    def __init__(self, model_path: str = "./models/best.pt"):
        self.model = YOLO(model_path)

    def detect(self, image_path: Union[str, Image]) -> list[Results]:
        return self.model.predict(image_path)

    @limit_boxes(2)
    def get_station_label_roi(self, prediction: Results):
        label1 = prediction.boxes[0].cls.cpu().numpy().astype(int)[0]

        x1, y1, x2, y2 = (
            map(int, prediction[1].boxes[0].xyxy[0])
            if label1 == 0
            else map(int, prediction[0].boxes[0].xyxy[0])
        )
        return prediction.plot(labels=False, boxes=False)[y1:y2, x1:x2]

    @limit_boxes(2)
    def get_gauge_roi(self, prediction: Results):
        label1 = prediction.boxes[0].cls.cpu().numpy().astype(int)[0]

        x1, y1, x2, y2 = (
            map(int, prediction[1].boxes[0].xyxy[0])
            if label1 == 1
            else map(int, prediction[0].boxes[0].xyxy[0])
        )
        return prediction.plot(labels=False, boxes=False)[y1:y2, x1:x2]


LLM_CLIENT_TYPE = TypeVar("LLM_CLIENT_TYPE")  # For the LLM client type


class AbstractLLMClient(ABC, Generic[LLM_CLIENT_TYPE]):
    def __init__(self, model_name: str, secret_key: Optional[str] = None):
        self.client: LLM_CLIENT_TYPE = self._initialize_client(secret_key)
        self.model_name = model_name

    @abstractmethod
    def _initialize_client(self, secret_key: str) -> LLM_CLIENT_TYPE:
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abstractmethod
    def get_gauge_and_station_label_reading(
        self, prompt: str, gauge_roi: Image, station_label_roi: Image
    ) -> AbstractLLMResponse:
        raise NotImplementedError("This method should be implemented by subclasses.")


class GeminiClient(AbstractLLMClient[genai.Client]):
    def __init__(
        self, model_name: str = "gemini-2.5-flash", secret_key: Optional[str] = None
    ):
        super().__init__(model_name, secret_key)

    def _initialize_client(self, secret_key: str) -> genai.Client:
        return genai.Client(api_key=secret_key)  # Replace with your actual API key

    def get_gauge_and_station_label_reading(
        self, prompt: str, gauge_roi: Image, station_label_roi: Image
    ) -> ValidMMSContribution:
        # Implement Gemini-specific response generation logic here
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[
                types.Part.from_bytes(
                    data=Image_to_b64(gauge_roi),
                    mime_type="image/jpeg",
                ),
                types.Part.from_bytes(
                    data=Image_to_b64(station_label_roi),
                    mime_type="image/jpeg",
                ),
                prompt,
            ],
            config={
                "response_mime_type": "application/json",
                "response_schema": ValidMMSContribution,
            },
        )
        return response.parsed
