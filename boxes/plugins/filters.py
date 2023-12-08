"""
Filters nodes
"""

import cv2
import numpy as np
from boxes import RootNode, get_tuple


class Blur(RootNode):
    """Blur video or image"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blur_size = self.param["blur_size"]

    def out_frame(self):
        # frame = cv2.UMat(self.get_frame(0))
        frame = self.get_frame(0)
        if frame is None:
            print("BlurNode stop")
            return None
        if self.disabled:
            return frame
        return cv2.blur(frame, ksize=(self.blur_size, self.blur_size))

    def update(self, param):
        self.disabled = param["disabled"]
        self.blur_size = param["blur_size"]


class EdgeDetection(RootNode):
    """Canny edge detection video or image"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.param1 = self.param["minVal"]
        self.param2 = self.param["maxVal"]

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("EdgeNode stop")
            return None
        return cv2.Canny(frame, self.param1, self.param2)

    def update(self, param):
        self.param1 = param["minVal"]
        self.param2 = param["maxVal"]


class Sharpen(RootNode):
    """Sharpen video or image"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kernel_sharpen = np.array(
            [[0, -1, 0], [-1, self.param["size"], -1], [0, -1, 0]]
        )

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("BrightnessNode stop")
            return None
        if self.disabled:
            return frame
        return cv2.filter2D(frame, -1, self.kernel_sharpen)

    def update(self, param):
        self.disabled = param["disabled"]
        self.kernel_sharpen = np.array(
            [[0, -1, 0], [-1, param["size"], -1], [0, -1, 0]]
        )
