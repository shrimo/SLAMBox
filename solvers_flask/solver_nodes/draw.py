""" Node library for drawing """

import time
import cv2
import numpy as np
from solvers_flask import Node, get_tuple
# from .misc import insert_frame, get_tuple


class FPS(Node):
    """Show FPS Information"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = get_tuple(self.param["fps_color"])
        self.prev_frame_time = 0
        self.new_frame_time = 0
        self.color_x = self.color_reversed(self.param["color_picker"])
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def out_frame(self):
        self.new_frame_time = time.time()
        frame = self.get_frame(0)
        if frame is None:
            print("FPSNode stop")
            return None
        elif self.disabled:
            return frame
        WH = frame.shape
        # print(self.new_frame_time, self.prev_frame_time)
        fps = str(int(1 / (self.new_frame_time - self.prev_frame_time)))
        cv2.rectangle(
            frame,
            (int(WH[1] - 140), int(WH[0] - 50)),
            (int(WH[1] - (70 - len(fps) * 12)), int(WH[0])),
            (110, 50, 30),
            -1,
        )
        cv2.putText(
            frame,
            "fps:" + fps,
            (int(WH[1] - 130), int(WH[0] - 20)),
            self.font,
            0.75,
            (self.color_x),
            1,
        )
        self.prev_frame_time = self.new_frame_time
        return frame

    def update(self, param):
        self.disabled = param["disabled"]
        self.color = get_tuple(param["fps_color"])
        self.color_x = self.color_reversed(param["color_picker"])


class Counter(Node):
    """Show Frame Counter Information"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = get_tuple(self.param["counter_color"])
        self.frame_counter = 0
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("CounterNode stop")
            return None
        elif self.disabled:
            return frame
        height, width, channels = frame.shape
        cv2.rectangle(frame, (20, height - 50), (180, height), (110, 50, 30), -1)
        cv2.putText(
            frame,
            "frame:" + str(self.frame_counter),
            (int(30), int(height - 20)),
            self.font,
            0.75,
            self.color,
            1,
        )
        self.frame_counter += 1
        return frame

    def update(self, param):
        self.disabled = param["disabled"]
        self.color = get_tuple(param["counter_color"])


class Constant(Node):
    """Constant background with specified color"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = get_tuple(self.param["constant_color"])
        self.width = int(self.param["width_"])
        self.height = int(self.param["height_"])

    def out_frame(self):
        return self.create_blank(self.width, self.height, self.color)

    def create_blank(self, width, height, color):
        """Create Constant"""
        image = np.zeros((height, width, 3), np.uint8)
        image[:] = color
        return image

    def update(self, param):
        self.color = get_tuple(param["constant_color"])
        self.width = int(param["width"])
        self.height = int(param["height"])


class Text(Node):
    """Show FPS Information"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = get_tuple(self.param["text_color_"])
        self.text = self.param["text"]
        self.px = int(self.param["px"])
        self.py = int(self.param["py"])
        self.size = float(self.param["size_"])
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("TextNode stop")
            return None
        elif self.disabled:
            return frame
        cv2.putText(
            frame, self.text, (self.px, self.py), self.font, self.size, (self.color), 1
        )
        return frame

    def update(self, param):
        self.disabled = param["disabled"]
        self.color = get_tuple(param["text_color_"])
        self.text = param["text"]
        self.px = int(param["px"])
        self.py = int(param["py"])
        self.size = float(param["size_"])


class Trajectory(Node):
    """Trajectory tracking"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.length = int(self.param["length"])
        self.size = int(self.param["size"])
        self.color = get_tuple(self.param["track_color"])
        self.variable = self.param["variable"]
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.tr = []

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("FPSNode stop")
            return None
        elif self.disabled:
            return frame
        elif self.variable in self.buffer.variable:
            x, y = self.buffer.variable[self.variable]
            self.tr.append(np.array([int(x), int(y)]))
            frame = cv2.polylines(
                frame, np.int32([self.tr[-self.length :]]), False, self.color, self.size
            )
        return frame

    def update(self, param):
        self.disabled = param["disabled"]
        if self.disabled:
            self.tr.clear()
        self.length = int(param["length"])
        self.size = int(param["size"])
        self.track_color = get_tuple(param["track_color"])
        self.variable = param["variable"]
