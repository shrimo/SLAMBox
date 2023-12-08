""" Node library for drawing """

import time
import cv2
import numpy as np
from dataclasses import fields
from boxes import RootNode, get_tuple, Color, show_attributes


class ColorSet(RootNode):
    """Shows the set of colors available in the system"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_rows = self.param["num_rows"]
        self.num_cols = self.param["num_cols"]
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.color_set = Color()
        self.color_dict = {}
        self.color_inv = {
            "white": self.color_set.black,
            "black": self.color_set.white,
            "yellow": self.color_set.gray,
            "cyan": self.color_set.gray,
            "green": self.color_set.gray,
        }
        for field in fields(self.color_set):
            field_value = getattr(self.color_set, field.name)
            self.color_dict[field.name] = field_value

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("ColorSet stop")
            return None
        elif self.disabled:
            return frame
        frame_height, frame_width, _ = frame.shape
        tile_width = frame_width // self.num_cols
        tile_height = frame_height // self.num_rows
        for i, key in enumerate(self.color_dict):
            row = i // self.num_cols
            col = i % self.num_cols
            x1, y1 = col * tile_width, row * tile_height
            x2, y2 = (col + 1) * tile_width, (row + 1) * tile_height
            cv2.rectangle(frame, (x1, y1), (x2, y2), self.color_dict[key], -1)
            text_color = self.color_set.white
            if key in self.color_inv.keys():
                text_color = self.color_inv[key]
            cv2.putText(
                frame,
                key.replace("_", " ").capitalize(),
                (x1 + 5, y2 - 10),
                self.font,
                0.5,
                text_color,
                1,
            )
        show_attributes(frame, [f'SLAMBOX{" "*4}'])
        return frame

    def update(self, param):
        self.disabled = param["disabled"]
        self.num_rows = param["num_rows"]
        self.num_cols = param["num_cols"]


class FPS(RootNode):
    """Show FPS Information"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prev_frame_time = 0
        self.new_frame_time = 0
        self.color = self.color_reversed(self.param["color_picker"])
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def out_frame(self):
        self.new_frame_time = time.time()
        frame = self.get_frame(0)
        if frame is None:
            print("FPS stop")
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
            (self.color),
            1,
        )
        self.prev_frame_time = self.new_frame_time
        return frame

    def update(self, param):
        self.disabled = param["disabled"]
        self.color = self.color_reversed(param["color_picker"])


class Counter(RootNode):
    """Show Frame Counter Information"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = self.color_reversed(self.param["counter_color"])
        self.frame_counter = 0
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("Counter stop")
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
        self.color = self.color_reversed(param["counter_color"])


class Constant(RootNode):
    """Constant background with specified color"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = self.color_reversed(self.param["constant_color"])
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
        self.color = self.color_reversed(param["constant_color"])
        self.width = int(param["width"])
        self.height = int(param["height"])


class Text(RootNode):
    """Show FPS Information"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = self.color_reversed(self.param["text_color_"])        
        self.text = self.param["text"]
        self.px = int(self.param["px"])
        self.py = int(self.param["py"])
        self.size = float(self.param["size_"])
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("Text stop")
            return None
        elif self.disabled:
            return frame
        cv2.putText(
            frame, self.text, (self.px, self.py), self.font, self.size, (self.color), 1
        )
        return frame

    def update(self, param):
        self.disabled = param["disabled"]
        self.color = self.color_reversed(param["text_color_"])
        self.text = param["text"]
        self.px = int(param["px"])
        self.py = int(param["py"])
        self.size = float(param["size_"])


class Trajectory(RootNode):
    """Trajectory tracking"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.length = int(self.param["length"])
        self.size = int(self.param["size"])
        self.color = self.color_reversed(self.param["track_color"])
        self.variable = self.param["variable"]
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.tr = []

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("FPS stop")
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
        self.track_color = self.color_reversed(param["track_color"])
        self.variable = param["variable"]

