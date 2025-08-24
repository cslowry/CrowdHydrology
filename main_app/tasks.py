from io import BytesIO

import requests
from django.conf import settings
from loguru import logger
from PIL import Image
from rest_framework.status import HTTP_200_OK
from twilio.rest import Client

from main_app.contribution_database import (
    get_station_by_id,
    get_success_contribution_message,
    hash_phone_number,
    save_invalid_contribution,
    save_valid_contribution,
)
from model.detection import ContributionImageDetector, GeminiClient
from model.exceptions import (
    INVALID_GAUGE_READING_EXCEPTION,
    INVALID_STATION_LABEL_EXCEPTION,
    InvalidBoxesException,
)
from model.preprocessor import GaugePreprocessor, StationLabelPreprocessor

PROMPT_TEXT = """
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
"""


def process_mms_image(
    media_url: str, senders_phone_number: str, twilio_number: str, twilio_client: Client
):
    """
    Process the MMS image in the background.
    Returns a tuple of (success, message) where success is a boolean and message is the response text.
    """
    hashed_phone_number = hash_phone_number(senders_phone_number)
    try:
        logger.info("Processing MMS media in background task.")

        # Get gauge measurement
        slp, gp = StationLabelPreprocessor(), GaugePreprocessor()
        detector = ContributionImageDetector(
            f"{settings.BASE_DIR}/model/models/best.pt"
        )

        media = requests.get(media_url)
        if media.status_code != HTTP_200_OK:
            raise Exception("Failed to retrieve the media. Please try again.")

        media = Image.open(BytesIO(media.content))
        logger.info("Detecting image in MMS media.")
        detected = detector.detect(media)  # Detect the ROIs

        # Extract ROIs
        station_label_roi = detector.get_station_label_roi(detected[0])
        gauge_roi = detector.get_gauge_roi(detected[0])
        logger.info("Detected and extracted ROIs from the image media.")

        station_label_roi = slp.preprocess(station_label_roi)
        gauge_roi = gp.preprocess(gauge_roi)

        logger.info("Extracting Gauge and Station Label Values.")

        # Extract reading values
        llm_client = GeminiClient(secret_key=settings.GEMINI_API_KEY)

        logger.warning("Extracting gauge and station label reading from the image...")
        contribution = llm_client.get_gauge_and_station_label_reading(
            PROMPT_TEXT, gauge_roi, station_label_roi
        )
        logger.success(
            f"Successfully extracted gauge and station label reading from the image. "
            f"Gauge Reading: {contribution.gauge_reading.gauge_reading}, "
            f"Station Label: {contribution.station_label.station_id}"
        )

        if not contribution.station_label.is_valid_station_label:
            raise InvalidBoxesException(INVALID_STATION_LABEL_EXCEPTION)
        if not contribution.gauge_reading.is_valid_gauge:
            raise InvalidBoxesException(INVALID_GAUGE_READING_EXCEPTION)

        # Save Contribution
        station = get_station_by_id(contribution.station_label.station_id)
        contribution = save_valid_contribution(
            hashed_phone_number,
            station,
            contribution.gauge_reading.gauge_reading,
        )

        twilio_client.messages.create(
            from_=twilio_number,
            to=senders_phone_number,
            body=get_success_contribution_message(contribution),
        )

    except InvalidBoxesException:
        save_invalid_contribution(hashed_phone_number, media_url)
        twilio_client.messages.create(
            from_=twilio_number,
            to=senders_phone_number,
            body="It seems that the image is not clear or is invalid. Please try again.",
        )
        raise

    except Exception as e:
        logger.error(f"Error processing MMS: {str(e)}")
        twilio_client.messages.create(
            from_=twilio_number,
            to=senders_phone_number,
            body="An error occurred while processing your contribution. Please try again later.",
        )
        raise
