""" Misc functions for pipeline """

import cv2
import numpy as np
from dataclasses import dataclass


@dataclass
class Color:
    """
    Colors Class (color palette set)
    OpenCV uses BGR image format
    """

    white: tuple = (255, 255, 255)
    gray: tuple = (25, 25, 25)
    black: tuple = (0, 0, 0)
    red: tuple = (0, 0, 255)
    green: tuple = (0, 255, 0)
    blue: tuple = (255, 0, 0)
    yellow: tuple = (0, 255, 255)
    cyan: tuple = (255, 255, 0)
    magenta: tuple = (255, 0, 255)
    dark_red: tuple = (0, 0, 150)
    midnight_blue: tuple = (110, 50, 30)
    cerulean: tuple = (167, 123, 0)
    claret: tuple = (49, 19, 129)
    aquamarine: tuple = (190, 200, 10)
    cinnamon: tuple = (30, 105, 210)
    bud_green: tuple = (97, 182, 123)
    skobeloff_green: tuple = (116, 116, 0)
    asparagus: tuple = (88, 144, 121)
    caramel: tuple = (81, 118, 191)
    greenery: tuple = (75, 176, 136)
    sheer_lilac: tuple = (192, 147, 183)
    baja_blue: tuple = (176, 109, 95)
    teal_blue: tuple = (136, 117, 54)
    kiwi: tuple = (90, 171, 97)
    jade_green: tuple = (107, 168, 0)
    lavender: tuple = (220, 126, 181)
    blue_perennial: tuple = (191, 129, 75)
    red_dahlia: tuple = (39, 32, 125)
    blue_atoll: tuple = (210, 177, 0)
    burnt_sienna: tuple = (82, 93, 198)
    viva_magenta: tuple = (85, 52, 190)
    persimmon: tuple = (102, 120, 246)
    strong_blue: tuple = (160, 93, 31)
    kohlrabi: tuple = (101, 207, 156)
    red_orange: tuple = (39, 83, 239)
    high_visibility: tuple = (0, 199, 241)


cc = Color()
font = cv2.FONT_HERSHEY_SIMPLEX


def frame_error(frame, msg, x_offset=300, y_offset=0):
    """Error while working with frames"""
    cx = (frame.shape[1] // 2) - x_offset
    cy = frame.shape[0] // 2 + y_offset
    return cv2.putText(frame, msg, (cx, cy), font, 1, cc.red, 1)


def insert_frame(frame_a, frame_b):
    """Inserting one frame into another"""
    if frame_a.shape[1] < frame_b.shape[1]:
        return frame_error(frame_a, "Inserted frame B - out of bounds")
    height_b, width_b, channels_b = frame_b.shape
    frame_a[:height_b, :width_b, :] = frame_b
    return frame_a


def merge_frame(frame_a, frame_b, op_a, op_b):
    """Merging one frame into another"""
    height_a, width_a, channels_a = frame_a.shape
    height_b, width_b, channels_b = frame_b.shape
    h_max = max(height_a, height_b)
    w_max = max(width_a, width_b)
    frame_a = cv2.resize(frame_a, (w_max, h_max))
    frame_b = cv2.resize(frame_b, (w_max, h_max))
    return cv2.addWeighted(frame_a, op_a, frame_b, op_b, 0)


def get_tuple(in_str, ttype=int):
    """convert string to tulpe"""
    return tuple(map(ttype, in_str.split(",")))


def move_to_center(tx, ty, cx, cy):
    """function shifts frame along tracker point to center of frame"""
    return np.float32([[1, 0, -(tx - cx)], [0, 1, -(ty - cy)]])


def show_attributes(frame, list_attributes, x_offset=0, color=cc.midnight_blue):
    """
    Display object attributes
    a list can have a number of string attributes
    """
    step = 30
    ssize = len(max(list_attributes, key=len))
    for ns, attribut in enumerate(list_attributes):
        ns = (ns + 1) * step
        cv2.rectangle(
            frame,
            (30 + x_offset, ns - step),
            (ssize * 12 + x_offset, ns + (step // 2) - 10),
            color,
            -1,
        )
        cv2.putText(frame, attribut, (45 + x_offset, ns - 10), font, 0.5, cc.white, 1)
    return frame
