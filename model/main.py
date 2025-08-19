import time

import numpy as np
from google import genai
from google.genai import types
from loguru import logger
from PIL import Image
from preprocessor import GaugePreprocessor, StationLabelPreprocessor
from ultralytics import YOLO

from model.helper import Image_to_b64
from model.responses import GaugeReading, ValidMMSContribution


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


# if __name__ == "__main__":
#     logger.trace("Beginning Gauge Reading")
#     # predictions = detect_images("./data/all")
#     # create global csv variable to store results
#     results = []
#     # Iterate through predictions and process each image
#     try:
#         for i in range(0, 141):
#             predictions = detect_images(f"./data/all/{i + 1}.JPG")
#             for prediction in predictions:
#                 logger.warning(f"Processing Gauge Image: {i + 1}")
#                 label1, label2 = (
#                     prediction.boxes[0].cls.cpu().numpy().astype(int)[0],
#                     prediction.boxes[1].cls.cpu().numpy().astype(int)[0],
#                 )
#                 x1, y1, x2, y2 = (
#                     map(int, prediction[1].boxes[0].xyxy[0])
#                     if label1 == 1
#                     else map(int, prediction[0].boxes[0].xyxy[0])
#                 )
#
#                 stationLabel = prediction.plot(labels=False, boxes=False)[y1:y2, x1:x2]
#
#                 preprocessor = GaugePreprocessor()
#                 stationLabel = preprocessor.preprocess(stationLabel)
#
#                 processed_pil = Image.fromarray((stationLabel * 255).astype(np.uint8))
#                 processed_pil.save(f"data/preprocessed_images/gauge/{i + 1}.png")
#                 logger.success(f"Detected Water Line for Gauge Image: {i + 1}")
#
#                 logger.warning(f"Sending Gauge Image: {i + 1} to Gemini for Reading")
#                 client = genai.Client(api_key="")
#                 parsed = process_gauge_reading(processed_pil)
#                 logger.success(
#                     f"Received Gauge Reading for Image: {i + 1} - {parsed.gauge_reading}"
#                 )
#                 time.sleep(3)
#     except Exception as e:
#         logger.error(f"An error occurred: {e}")
#         raise e
#     finally:
#         # Save results to a CSV file
#         import pandas as pd
#
#         logger.warning("Saving results to CSV")
#         df = pd.DataFrame(results)
#         df.to_csv("gauge_readings.csv", index=False)
#         logger.success("Results saved to gauge_readings.csv")


if __name__ == "__main__":
    logger.trace("Beginning Gauge Reading")
    # predictions = detect_images("./data/all")
    # create global csv variable to store results
    results = []
    # Iterate through predictions and process each image
    try:
        for i in range(74, 141):
            predictions = detect_images(f"./data/all/{i + 1}.JPG")
            for prediction in predictions:
                logger.warning(f"Processing Gauge Image: {i + 1}")
                label1, label2 = (
                    prediction.boxes[0].cls.cpu().numpy().astype(int)[0],
                    prediction.boxes[1].cls.cpu().numpy().astype(int)[0],
                )
                x1, y1, x2, y2 = (
                    map(int, prediction[1].boxes[0].xyxy[0])
                    if label1 == 0
                    else map(int, prediction[0].boxes[0].xyxy[0])
                )

                station_label_roi = prediction.plot(labels=False, boxes=False)[
                    y1:y2, x1:x2
                ]
                x1, y1, x2, y2 = (
                    map(int, prediction[1].boxes[0].xyxy[0])
                    if label1 == 1
                    else map(int, prediction[0].boxes[0].xyxy[0])
                )

                gauge_roi = prediction.plot(labels=False, boxes=False)[y1:y2, x1:x2]

                slp = StationLabelPreprocessor()
                gp = GaugePreprocessor()

                station_label_roi = slp.preprocess(station_label_roi)

                station_label_pil = Image.fromarray(
                    (station_label_roi * 255).astype(np.uint8)
                )
                station_label_pil.save(
                    f"data/preprocessed_images/station_labels/{i + 1}.png"
                )

                gauge_roi = gp.preprocess(gauge_roi)

                gauge_pil = Image.fromarray((gauge_roi * 255).astype(np.uint8))
                gauge_pil.save(f"data/preprocessed_images/gauge/{i + 1}.png")
                logger.success(f"Detected Water Line for Gauge Image: {i + 1}")

                # Station Label and Gauge Numeric Reading Extraction via Gemini.
                logger.warning(
                    f"Sending Station Label Image: {i + 1} to Gemini for Reading"
                )

                client = genai.Client(api_key="")
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        types.Part.from_bytes(
                            data=Image_to_b64(gauge_pil),
                            mime_type="image/jpeg",
                        ),
                        types.Part.from_bytes(
                            data=Image_to_b64(station_label_pil),
                            mime_type="image/jpeg",
                        ),
                        """
                        Task: You are given two images in a single prompt.

                        Image 1: Staff Gauge

                        - Decide if this is a clear staff-gauge photo.
                        - If it’s not a staff gauge, or if it’s too unclear for a confident reading (confidence < 0.70),
                        - set "is_valid_gauge": false and stop.
                        - Otherwise, calculate the exact water-level reading at the red line.
                        - The gauge reading is always a positive floating-point number in 2 decimal places.

                        Gauge Details:
                        - Major stripes: longer, labeled marks (e.g. 1.0, 1.1, …).
                        - Minor stripes: shorter, evenly spaced between two majors.

                        Step-by-Step Instructions:
                        - Detect two consecutive, fully visible major stripes and note their labels (e.g. 1.0 & 1.1).
                        - Count the minor stripes between them; compute
                        minor_unit = (major2_label − major1_label) ÷ minor_count_between.
                        - Locate the red waterline.
                        - Identify the first major stripe above that line; record its label M.
                        - Count how many minor stripes lie between the waterline and stripe M; call that n.
                        - Compute reading = M + (n × minor_unit).

                        Image 2: Station Label
                        - Analyze the image to verify if it is a valid station label.
                        - A valid station label contains a station ID that matches one of the predefined station IDs.
                        - If not valid, respond with "is_valid_station_label": false and "station_id": null.
                        - If valid, set "is_valid_station_label": true and return the "station_id".

                        Critical Consideration:
                        - If the image is beyond the ability to analyze, unreadable,
                        or if the confidence of the output is below 40%, mark it invalid.
                        """,
                    ],
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": ValidMMSContribution,
                    },
                )
                parsed: ValidMMSContribution = response.parsed
                results.append(
                    {
                        "image": f"{i + 1}.png",
                        "is_valid_station_label": parsed.station_label.is_valid_station_label,
                        "station_id": parsed.station_label.station_id.value
                        if parsed.station_label.is_valid_station_label
                        else None,
                        "is_valid_gauge": parsed.gauge_reading.is_valid_gauge,
                        "gauge_reading": parsed.gauge_reading.gauge_reading
                        if parsed.gauge_reading.is_valid_gauge
                        else None,
                    }
                )
                logger.success(
                    f"Image: {i + 1} -- "
                    f"Station ID: "
                    f"{parsed.station_label.station_id.value if parsed.station_label.is_valid_station_label else None}"
                    f"-- Gauge Reading: "
                    f"{parsed.gauge_reading.gauge_reading if parsed.gauge_reading.is_valid_gauge else None}"
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
        df.to_csv("station_labels_old.csv", index=False)
        logger.success("Results saved to station_labels_old.csv")
