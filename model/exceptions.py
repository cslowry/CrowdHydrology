class InvalidBoxesException(Exception):
    """Exception raised for invalid number of bounding boxes detected."""

    def __init__(self, message="Invalid number of bounding boxes detected."):
        self.message = message
        super().__init__(self.message)
