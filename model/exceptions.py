INVALID_STATION_LABEL_EXCEPTION = (
    "The station label is invalid or not recognized. Please try again."
)
INVALID_GAUGE_READING_EXCEPTION = (
    "The gauge reading is invalid or not recognized. Please try again."
)


class InvalidBoxesException(Exception):
    """Exception raised for invalid number of bounding boxes detected."""

    def __init__(self, message="Invalid number of bounding boxes detected."):
        self.message = message
        super().__init__(self.message)
