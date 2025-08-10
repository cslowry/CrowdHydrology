from abc import ABC, abstractmethod
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


class AbstractPreprocessor(ABC):
    @abstractmethod
    def preprocess(self, img: Any) -> np.ndarray:
        pass

    def to_pil(self, img: Any) -> Image.Image:
        if not isinstance(img, Image.Image):
            img = Image.fromarray(img)
        return img

    def to_grayscale(self, img: Image.Image) -> Image.Image:
        return img.convert("L")

    def enhance_contrast(self, img: Image.Image, factor: float = 2.0) -> Image.Image:
        return ImageEnhance.Contrast(img).enhance(factor)

    def sharpen(self, img: Image.Image) -> Image.Image:
        return img.filter(ImageFilter.SHARPEN)

    def invert(self, img: Image.Image) -> Image.Image:
        return ImageOps.invert(img)

    def normalize(self, img: Image.Image) -> np.ndarray:
        return np.array(img) / 255.0

    def resize(self, img: Image.Image, size: tuple[int, int]) -> Image.Image:
        return img.resize(size, Image.LANCZOS)

    def denoise(self, img: Image.Image) -> Image.Image:
        return img.filter(ImageFilter.MedianFilter(size=3))

    def adaptive_threshold(self, img: Image.Image, window_size=9) -> Image.Image:
        arr = img if type(img) is np.array else np.array(img)
        thresh = cv2.adaptiveThreshold(
            arr, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, window_size, 2
        )
        return Image.fromarray(thresh)

    def equalize(self, img: Image.Image) -> Image.Image:
        arr = np.array(img)
        eq = cv2.equalizeHist(arr)
        return Image.fromarray(eq)


class StationLabelPreprocessor(AbstractPreprocessor):
    def preprocess(self, img: Any) -> np.ndarray:
        # Initial conversion
        img = self.to_pil(img)

        # Basic preprocessing
        img = self.to_grayscale(img)

        # resize
        img = self.resize(img, (400, 300))  # Wider size for better text aspect ratio

        # Enhancement sequence
        img = self.enhance_contrast(img, factor=2.5)  # Increased contrast
        img = self.denoise(img)  # Remove noise after contrast
        img = self.equalize(img)  # Balance the brightness
        img = self.sharpen(img)  # Make text crisper

        # Thresholding with modified parameters
        img = self.adaptive_threshold(img)

        # Final normalization
        img = self.normalize(img)
        return img


class GaugePreprocessor(AbstractPreprocessor):
    def _output_enhance(self, img: Image.Image):
        img = self._resize_by_height(img, 600)
        img = self.enhance_contrast(img, factor=3)
        img = self.sharpen(img)
        img = np.array(img)
        return img

    def preprocess(self, img: Any) -> np.ndarray:
        # 1) PIL → Grayscale → proportional resize
        pil = self.to_pil(img)
        original_img = pil.copy()

        img = self.to_grayscale(pil)
        img = self._resize_by_height(img, 600)

        blurred = cv2.GaussianBlur(np.array(img), (5, 5), sigmaX=1.5)
        img = Image.fromarray(blurred)

        # 2) Denoise & contrast
        img = img.filter(ImageFilter.MedianFilter(3))
        # img = ImageEnhance.Contrast(img).enhance(3)
        # img = img.filter(ImageFilter.SHARPEN)

        # 3) Convert to numpy gray for waterline detection
        arr_gray = np.array(img, dtype=np.uint8)

        # 4) Detect waterline (paper’s method)
        row, cleaned = self.detect_waterline(arr_gray)

        # 5) Mark that waterline on an RGB version
        # rgb = cv2.cvtColor(arr_gray, cv2.COLOR_GRAY2BGR)  # pylint: disable=no-member

        original_img = self._output_enhance(original_img)

        marked = self.mark_waterline(np.array(original_img), row)
        # marked = self.mark_waterline(original_img, row)
        # marked = self.mark_waterline(cleaned, row)

        # 6) Normalize and return
        # marked_norm = marked.astype(np.float32) / 255.0
        return np.array(marked)

    def _resize_by_height(self, img: Image.Image, target_h: int) -> Image.Image:
        w, h = img.size
        new_w = int(w * (target_h / h))
        return img.resize((new_w, target_h), Image.LANCZOS)

    def detect_waterline(self, img_gray: np.ndarray) -> tuple[int, np.ndarray]:
        H, W = img_gray.shape

        # 1) Lightly smooth to suppress tiny specks
        img_gray = cv2.GaussianBlur(img_gray, (5, 5), 1.5)
        img_gray = cv2.medianBlur(img_gray, 5)

        # top-hat to remove uneven lighting
        kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        tophat = cv2.morphologyEx(img_gray, cv2.MORPH_TOPHAT, kernel1)

        # contrast stretch + Otsu threshold
        minV, maxV = tophat.min(), tophat.max()
        stretched = ((tophat - minV) * (255.0 / (maxV - minV))).astype(np.uint8)
        _, binary = cv2.threshold(stretched, 0, 255, cv2.THRESH_OTSU)

        # close then open to clean
        kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel2)
        cleaned = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel2)

        # sum white pixels per row → first row above threshold
        row_sums = cleaned.sum(axis=1)
        thresh = 0.5 * row_sums.max()  # e.g. 10% of max

        # Reverse scan: bottom row → top row
        rev = row_sums[::-1]  # flips it end←→start
        rev_idx = int(np.argmax(rev > thresh))  # first “hit” in reversed
        water_row = (cleaned.shape[0] - 1) - rev_idx  # map back to original row

        return water_row, cleaned

    def mark_waterline(self, rgb_img: np.ndarray, row: int) -> np.ndarray:
        marked = rgb_img.copy()
        cv2.line(marked, (0, row), (marked.shape[1] - 1, row), (255, 0, 0), 2)
        return marked
