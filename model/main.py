import base64
import time
import typing
from enum import Enum
from io import BytesIO

import numpy as np
from google import genai
from google.genai import types
from loguru import logger
from PIL import Image
from preprocessor import GaugePreprocessor, StationLabelPreprocessor
from pydantic import BaseModel
from ultralytics import YOLO


class GaugeReading(BaseModel):
    is_valid_gauge: bool
    gauge_reading: typing.Optional[float] = None


class StationIdEnum(str, Enum):
    NY1019 = "NY1019"
    NY1021 = "NY1021"
    NY1010 = "NY1010"
    NY1003 = "NY1003"
    NY1025 = "NY1025"
    NY1022 = "NY1022"
    NY1020 = "NY1020"
    NY1011 = "NY1011"
    NY1009 = "NY1009"
    NY1002 = "NY1002"
    NY1004 = "NY1004"
    NY1006 = "NY1006"
    NY1005 = "NY1005"
    NY1008 = "NY1008"
    NY1007 = "NY1007"
    NY1000 = "NY1000"
    PA1002 = "PA1002"
    PA1001 = "PA1001"
    PA1000 = "PA1000"
    WI1020 = "WI1020"
    WI2017 = "WI2017"
    WI2016 = "WI2016"
    WI2015 = "WI2015"
    WI2014 = "WI2014"
    WI2013 = "WI2013"
    WI2012 = "WI2012"
    WI2011 = "WI2011"
    WI2010 = "WI2010"
    WI2009 = "WI2009"
    WI2008 = "WI2008"
    WI2007 = "WI2007"
    WI2006 = "WI2006"
    WI2005 = "WI2005"
    WI2004 = "WI2004"
    WI2003 = "WI2003"
    WI2002 = "WI2002"
    WI2001 = "WI2001"
    WI9007 = "WI9007"
    WI9006 = "WI9006"
    WI9005 = "WI9005"
    WI9004 = "WI9004"
    WI9003 = "WI9003"
    WI9002 = "WI9002"
    WI9001 = "WI9001"
    WI9000 = "WI9000"
    WI1010 = "WI1010"
    NL1001 = "NL1001"
    NL1005 = "NL1005"
    NL1009 = "NL1009"
    WI1002 = "WI1002"
    WI1007 = "WI1007"
    WI1004 = "WI1004"
    NL1008 = "NL1008"
    NL1004 = "NL1004"
    NL1007 = "NL1007"
    NL1006 = "NL1006"
    WI1005 = "WI1005"
    WI1003 = "WI1003"
    WI1001 = "WI1001"
    WI1000 = "WI1000"
    UT1000 = "UT1000"
    OR1000 = "OR1000"
    OR1001 = "OR1001"
    NE1001 = "NE1001"
    NE1000 = "NE1000"
    MN1008 = "MN1008"
    MN1010 = "MN1010"
    MN1007 = "MN1007"
    MN1006 = "MN1006"
    MN1005 = "MN1005"
    MN1004 = "MN1004"
    MN1003 = "MN1003"
    MN1002 = "MN1002"
    MN1001 = "MN1001"
    MN1000 = "MN1000"
    MI1061 = "MI1061"
    MI1060 = "MI1060"
    MI1059 = "MI1059"
    MI1058 = "MI1058"
    MI1057 = "MI1057"
    MI1056 = "MI1056"
    MI1055 = "MI1055"
    MI1031 = "MI1031"
    MI1030 = "MI1030"
    MI1029 = "MI1029"
    MI1027 = "MI1027"
    MI1033 = "MI1033"
    MI1026 = "MI1026"
    MI1025 = "MI1025"
    MI1024 = "MI1024"
    MI1023 = "MI1023"
    MI1022 = "MI1022"
    MI1021 = "MI1021"
    MI1020 = "MI1020"
    MI1018 = "MI1018"
    MI1019 = "MI1019"
    MI1017 = "MI1017"
    MI1016 = "MI1016"
    MI1015 = "MI1015"
    MI1007 = "MI1007"
    MI1006 = "MI1006"
    MI1004 = "MI1004"
    MI1003 = "MI1003"
    MI1002 = "MI1002"
    MI1001 = "MI1001"
    MI1000 = "MI1000"
    MD1001 = "MD1001"
    MD1000 = "MD1000"
    IA1003 = "IA1003"
    IA1002 = "IA1002"
    IA1001 = "IA1001"
    IA1000 = "IA1000"
    MI1028 = "MI1028"
    CA1001 = "CA1001"
    CA1000 = "CA1000"
    AL1000 = "AL1000"
    MI1041 = "MI1041"
    NY1001 = "NY1001"
    NY1024 = "NY1024"
    MI1032 = "MI1032"
    MI2026 = "MI2026"
    MI2025 = "MI2025"
    MI2024 = "MI2024"
    MI2023 = "MI2023"
    MI2022 = "MI2022"
    IL1001 = "IL1001"
    IL1002 = "IL1002"
    IL1004 = "IL1004"
    AZ1006 = "AZ1006"
    AZ1002 = "AZ1002"
    AZ1014 = "AZ1014"
    AZ1001 = "AZ1001"
    AZ1007 = "AZ1007"
    AZ1004 = "AZ1004"
    AZ1011 = "AZ1011"
    AZ1012 = "AZ1012"
    AZ1000 = "AZ1000"
    AZ1008 = "AZ1008"
    AZ1009 = "AZ1009"
    AZ1003 = "AZ1003"
    AZ1010 = "AZ1010"
    AZ1005 = "AZ1005"
    AZ1016 = "AZ1016"
    AZ1017 = "AZ1017"
    AZ1019 = "AZ1019"
    AZ1020 = "AZ1020"
    AZ1022 = "AZ1022"
    MN1016 = "MN1016"
    MN1015 = "MN1015"
    MN1014 = "MN1014"
    MN1013 = "MN1013"
    MN1012 = "MN1012"
    MN1011 = "MN1011"
    AZ1013 = "AZ1013"
    MT1000 = "MT1000"
    MO1001 = "MO1001"
    MO1000 = "MO1000"
    NY1038 = "NY1038"
    AZ1027 = "AZ1027"
    AZ1028 = "AZ1028"
    AZ1029 = "AZ1029"
    AZ1030 = "AZ1030"
    MN1018 = "MN1018"
    NY1039 = "NY1039"
    CA1002 = "CA1002"
    OH1000 = "OH1000"
    IL1003 = "IL1003"
    IL1005 = "IL1005"
    OH1001 = "OH1001"
    OH1002 = "OH1002"
    OH1003 = "OH1003"
    OH1004 = "OH1004"
    AZ1015 = "AZ1015"
    MN1026 = "MN1026"
    MN1027 = "MN1027"
    MN1028 = "MN1028"
    NC1000 = "NC1000"
    IL1007 = "IL1007"
    MN1019 = "MN1019"
    MN1020 = "MN1020"
    MI1052 = "MI1052"
    MN1021 = "MN1021"
    IN1002 = "IN1002"
    IN1003 = "IN1003"
    IN1004 = "IN1004"
    NJ1001 = "NJ1001"
    IN1005 = "IN1005"
    LA1000 = "LA1000"
    LA1001 = "LA1001"
    LA1002 = "LA1002"
    LA1003 = "LA1003"
    LA1004 = "LA1004"
    LA1005 = "LA1005"
    MS1000 = "MS1000"
    MS1001 = "MS1001"
    MS1002 = "MS1002"
    MS1003 = "MS1003"
    NY1044 = "NY1044"
    WI1021 = "WI1021"
    OH1005 = "OH1005"
    NH1000 = "NH1000"
    OH1007 = "OH1007"
    NY9999 = "NY9999"
    PA1014 = "PA1014"
    OH1009 = "OH1009"
    OH1010 = "OH1010"
    OH1011 = "OH1011"
    OH1008 = "OH1008"
    OH1012 = "OH1012"
    PA1003 = "PA1003"
    PA1004 = "PA1004"
    PA1005 = "PA1005"
    PA1006 = "PA1006"
    PA1007 = "PA1007"
    PA1008 = "PA1008"
    PA1009 = "PA1009"
    PA1010 = "PA1010"
    PA1011 = "PA1011"
    PA1012 = "PA1012"
    PA1013 = "PA1013"
    PA1015 = "PA1015"
    PA1016 = "PA1016"
    PA1017 = "PA1017"
    PA1018 = "PA1018"
    PA1019 = "PA1019"
    PA1020 = "PA1020"
    PA1021 = "PA1021"
    PA1022 = "PA1022"
    PA1023 = "PA1023"
    PA1024 = "PA1024"
    PA1025 = "PA1025"
    PA1026 = "PA1026"
    PA1027 = "PA1027"
    PA1028 = "PA1028"
    PA1029 = "PA1029"
    PA1030 = "PA1030"
    PA1031 = "PA1031"
    MI1063 = "MI1063"
    OH1013 = "OH1013"
    OH1014 = "OH1014"
    OH1015 = "OH1015"
    OH1016 = "OH1016"
    OH1017 = "OH1017"
    MI1067 = "MI1067"
    OH1021 = "OH1021"
    OH1022 = "OH1022"
    OH1023 = "OH1023"
    OH1024 = "OH1024"
    OH1025 = "OH1025"
    OH1026 = "OH1026"
    OH1027 = "OH1027"
    OH1028 = "OH1028"
    NH1001 = "NH1001"
    NY1047 = "NY1047"
    NY1046 = "NY1046"
    NY1051 = "NY1051"
    NY1050 = "NY1050"
    NY1049 = "NY1049"
    NY1048 = "NY1048"
    NY1045 = "NY1045"
    PA1032 = "PA1032"
    NY1234 = "NY1234"
    WV1000 = "WV1000"
    OH1018 = "OH1018"
    OH1019 = "OH1019"
    OH1020 = "OH1020"
    WA1000 = "WA1000"
    OH1029 = "OH1029"
    OH1030 = "OH1030"
    OH1031 = "OH1031"
    OH1032 = "OH1032"
    OH1033 = "OH1033"
    OH1034 = "OH1034"


class StationLabel(BaseModel):
    is_valid_station_label: bool
    station_id: typing.Optional[StationIdEnum] = None


class ValidMMSContribution(BaseModel):
    station_label: StationLabel
    gauge_reading: GaugeReading


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
