import base64
import time
import typing
from io import BytesIO

import numpy as np
from google import genai
from google.genai import types
from loguru import logger
from PIL import Image
from preprocessor import GaugePreprocessor
from pydantic import BaseModel
from ultralytics import YOLO


class GaugeReading(BaseModel):
    is_valid_gauge: bool
    gauge_reading: typing.Optional[float] = None


def process_gauge_reading(client: genai.Client, image: Image.Image) -> GaugeReading:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=Image_to_b64(image),
                mime_type="image/jpeg",
            ),
            """
            **Task:** You’re given an image of a staff gauge.

                First, decide if this is a clear staff‑gauge photo.
                If it’s not a staff gauge, or if it’s too unclear for a confident reading (confidence < 0.70), set "is_valid_gauge": false and stop.

                Otherwise, calculate the exact water‑level reading at the red line.

                The gauge reading is always a positive floating‑point number in 2 decimal places.

            **Gauge Details:**

                Major stripes: longer, labeled marks (e.g. 1.0, 1.1, …)

                Minor stripes: shorter, evenly spaced between two majors.

            **Step‑by‑Step Instructions:**

                - Detect two consecutive, fully visible major stripes and note their labels (e.g. 1.0 & 1.1).

                - Count the minor stripes between them; compute
                minor_unit = (major2_label − major1_label) ÷ minor_count_between.

                - Locate the red waterline.

                - Identify the first major stripe above that line; record its label M.

                - Count how many minor stripes lie between the waterline and stripe M; call that n.

                - Compute reading = M + (n × minor_unit).

            """,
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": GaugeReading,
        },
    )
    return response.parsed


def detect_images(directory: str) -> list:
    model = YOLO("./models/best.pt")
    return model.predict(directory)


def Image_to_b64(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


if __name__ == "__main__":
    logger.trace("Beginning Gauge Reading")
    # predictions = detect_images("./data/all")
    # create global csv variable to store results
    results = []
    # Iterate through predictions and process each image
    try:
        for i in range(0, 141):
            predictions = detect_images(f"./data/all/{i + 1}.JPG")
            for prediction in predictions:
                logger.warning(f"Processing Gauge Image: {i + 1}")
                label1, label2 = (
                    prediction.boxes[0].cls.cpu().numpy().astype(int)[0],
                    prediction.boxes[1].cls.cpu().numpy().astype(int)[0],
                )
                x1, y1, x2, y2 = (
                    map(int, prediction[1].boxes[0].xyxy[0])
                    if label1 == 1
                    else map(int, prediction[0].boxes[0].xyxy[0])
                )

                stationLabel = prediction.plot(labels=False, boxes=False)[y1:y2, x1:x2]

                preprocessor = GaugePreprocessor()
                stationLabel = preprocessor.preprocess(stationLabel)

                processed_pil = Image.fromarray((stationLabel * 255).astype(np.uint8))
                processed_pil.save(f"data/preprocessed_images/gauge/{i + 1}.png")
                logger.success(f"Detected Water Line for Gauge Image: {i + 1}")

                logger.warning(f"Sending Gauge Image: {i + 1} to Gemini for Reading")
                client = genai.Client(api_key="")
                parsed = process_gauge_reading(processed_pil)
                logger.success(
                    f"Received Gauge Reading for Image: {i + 1} - {parsed.gauge_reading}"
                )
                time.sleep(3)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e
    finally:
        # Save results to a CSV file
        import pandas as pd

        logger.warning("Saving results to CSV")
        df = pd.DataFrame(results)
        df.to_csv("gauge_readings.csv", index=False)
        logger.success("Results saved to gauge_readings.csv")
