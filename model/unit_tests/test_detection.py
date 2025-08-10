import unittest
from unittest.mock import MagicMock, patch

import ultralytics  # noqa: F401

from model.detection import ContributionImageDetector
from model.exceptions import InvalidBoxesException


class ContributionImageDetectorTest(unittest.TestCase):
    @patch("ultralytics.YOLO.__init__")
    def test_ContributionImageDetector_equal_bounding_boxes(self, yolo_mock):
        yolo_mock.return_value = None
        detector = ContributionImageDetector()

        prediction = MagicMock()
        prediction.boxes = [MagicMock(), MagicMock()]
        detector.get_station_label_roi(prediction)

    @patch("ultralytics.YOLO.__init__")
    def test_ContributionImageDetector_less_bounding_boxes(self, yolo_mock):
        yolo_mock.return_value = None
        detector = ContributionImageDetector()

        with self.assertRaises(InvalidBoxesException):
            prediction = MagicMock()
            prediction.boxes = [MagicMock()]
            detector.get_station_label_roi(prediction)

    @patch("ultralytics.YOLO.__init__")
    def test_ContributionImageDetector_more_bounding_boxes(self, yolo_mock):
        yolo_mock.return_value = None
        detector = ContributionImageDetector()

        with self.assertRaises(InvalidBoxesException):
            prediction = MagicMock()
            prediction.boxes = [MagicMock(), MagicMock(), MagicMock()]
            detector.get_station_label_roi(prediction)
