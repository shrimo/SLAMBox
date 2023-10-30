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
    red = (0,0,255)
    dark_red = (0,0,150)
    green = (0,255,0)
    blue = (255,0,0)
    yellow = (0,255,255)
    cyan = (255,255,0)
    magenta = (255,0,255)
    white = (255,255,255)
    black = (0,0,0)
    midnight_blue = (110,50,30)
    cerulean = (167,123,0)
    claret = (49,19,129)
    aquamarine = (190,200,10)
    cinnamon = (30,105,210)
    bud_green = (97,182,123)
    skobeloff_green = (116, 116, 0)
    asparagus = (88,144,121)
    caramel = (81,118,191)
    greenery = (75,176,136)
    sheer_lilac = (192,147,183)
    baja_blue = (176,109,95)
    teal_blue = (136,117,54)
    kiwi = (90,171,97)
    jade_green = (107,168,0)
    lavender = (220, 126, 181)
    blue_perennial = (191, 129, 75)
    red_dahlia = (39, 32, 125)
    blue_atoll = (210, 177, 0)
    burnt_sienna = (81, 116, 233)
    viva_magenta = (85, 52, 190)

cc = Color()
font = cv2.FONT_HERSHEY_SIMPLEX

def frame_error(frame):
    """ Error while working with frames """
    msg = 'Inserted frame B - out of bounds'
    cx = (frame.shape[1]//2)-300
    cy = frame.shape[0]//2
    return cv2.putText(frame, msg, (cx, cy), font, 1, cc.red, 1)

def insert_frame(frame_a, frame_b):
    """ Inserting one frame into another """
    if frame_a.shape[1] < frame_b.shape[1]:
        return frame_error(frame_a)
    height_b, width_b, channels_b = frame_b.shape
    frame_a[:height_b, :width_b, :] = frame_b
    return frame_a

def merge_frame(frame_a, frame_b, op_a, op_b):
    """ Merging one frame into another """
    height_a, width_a, channels_a = frame_a.shape
    height_b, width_b, channels_b = frame_b.shape
    h_max = max(height_a, height_b)
    w_max = max(width_a, width_b)
    frame_a = cv2.resize(frame_a, (w_max,h_max))
    frame_b = cv2.resize(frame_b, (w_max,h_max))
    return cv2.addWeighted(frame_a, op_a, frame_b, op_b, 0)

def get_tuple(in_str, ttype = int):
    """ convert string to tulpe"""
    return tuple(map(ttype, in_str.split(',')))

def move_to_center(tx, ty, cx, cy):
    """ function shifts frame along tracker point to center of frame """
    return np.float32([[1, 0, -(tx - cx)], [0, 1, -(ty - cy)]])

def show_attributes(frame, list_attributes, x_offset = 0, color = cc.midnight_blue):
    """
    Display object attributes
    a list can have a number of string attributes
    """
    step = 30
    ssize = len(max(list_attributes, key=len))
    for ns, attribut in enumerate(list_attributes):
        ns = (ns+1)*step
        cv2.rectangle(frame, (30 + x_offset, ns-step), (ssize*12 + x_offset, ns+(step//2)-10), color, -1)
        cv2.putText(frame, attribut, (45 + x_offset, ns-10), font , 0.5, cc.white, 1)
    return frame

