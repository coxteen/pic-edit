from typing import Optional
import cv2
import numpy as np
from src.filters.base import ImageFilter


class ColorFilter(ImageFilter):
    """
    Applies chromatic balance transformations:
    - Temperature: Shift along the Blue (-100) to Amber/Yellow (+100) axis
    - Tint: Shift along the Green (-100) to Magenta (+100) axis
    """

    def __init__(self, temperature: float = 0.0, tint: float = 0.0):
        """
        :param temperature: Range [-100.0, 100.0]. 0.0 = Neutral.
        :param tint: Range [-100.0, 100.0]. 0.0 = Neutral.
        """
        self.temperature = float(temperature)
        self.tint = float(tint)

    def apply(self, image: np.ndarray) -> np.ndarray:
        if image is None or image.size == 0:
            raise ValueError("Invalid image buffer passed to ColorFilter.")

        if abs(self.temperature) < 0.01 and abs(self.tint) < 0.01:
            return image

        # Normalize factors to [-0.5, 0.5] scaling domain
        temp_factor = self.temperature / 200.0
        tint_factor = self.tint / 200.0

        # Calculate per-channel linear multipliers
        # Warm (+temp) increases R, decreases B
        # Cool (-temp) decreases R, increases B
        # Magenta (+tint) increases R & B, decreases G
        # Green (-tint) increases G, decreases R & B
        r_mult = 1.0 + temp_factor + (tint_factor * 0.5)
        g_mult = 1.0 - tint_factor
        b_mult = 1.0 - temp_factor + (tint_factor * 0.5)

        # Build 256-element 1D LUTs for R, G, and B
        base_range = np.arange(256, dtype=np.float32)

        lut_r = np.clip(base_range * r_mult, 0, 255).astype(np.uint8)
        lut_g = np.clip(base_range * g_mult, 0, 255).astype(np.uint8)
        lut_b = np.clip(base_range * b_mult, 0, 255).astype(np.uint8)

        # Merge into an RGB LUT (shape 1, 256, 3)
        merged_lut = np.dstack((lut_r, lut_g, lut_b))

        return cv2.LUT(image, merged_lut)