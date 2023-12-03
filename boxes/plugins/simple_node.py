"""Example of a simple node (backend)"""

import cv2
import numpy as np
from boxes import RootNode


class SimpleNode(RootNode):
    """A simple node that draws
    a circle with a specific color
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size = self.param["size"]
        self.color = self.color_reversed(self.param["picker"])

    def out_frame(self):
        frame = self.get_frame(0)
        if self.disabled:
            return frame
        height, width, channels = frame.shape
        cv2.circle(
            frame,
            (np.int32(width * 0.5), np.int32(height * 0.5)),
            self.size,
            self.color,
            -1,
        )
        return frame

    def update(self, param):
        self.disabled = param["disabled"]
        self.size = param["size"]
        self.color = self.color_reversed(param["picker"])
