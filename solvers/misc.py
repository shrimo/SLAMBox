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

class Draw3D:
    """ Class for drawing 3D primitives """
    def __init__(self, cube_xy):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.axes_color = [(255,0,0), (0,255,0), (0,0,255)]
        self.xyz = 'xyz'
        P = [[1,0,0], [0,1,0], [0,0,-1]]
        self.axis = np.float32(P).reshape(-1,3)
        self.axis_cube = np.float32([[0,0,0], [0,cube_xy,0], [cube_xy,cube_xy,0], [cube_xy,0,0],
                           [0,0,-cube_xy],[0,cube_xy,-cube_xy],[cube_xy,cube_xy,-cube_xy],[cube_xy,0,-cube_xy] ])

    def draw_points(self, img, points, color, size):
        for n, i in enumerate(points):
            gx, gy = np.int32(i.ravel())
            # img = cv2.drawMarker(img, (gx, gy), color, 1, 10, 2, 8)
            img = cv2.circle(img, (gx, gy), size, color, -1)
            img = cv2.putText(img, str(n), (gx+2, gy-2), self.font , 0.3, color, 1)
        return img

    def draw_cube(self, img, imgpts):
        imgpts = np.int32(imgpts).reshape(-1,2)
        # draw ground floor in green
        img = cv2.drawContours(img, [imgpts[:4]],-1,(0,255,0),2)
        # draw pillars in blue color
        for i,j in zip(range(4),range(4,8)):
            img = cv2.line(img, tuple(imgpts[i]), tuple(imgpts[j]),(255),2)
        # draw top layer in red color
        img = cv2.drawContours(img, [imgpts[4:]],-1,(0,0,255),2)
        return img

    def draw_axes(self, img, corners, imgpts):
        # cx, cy = np.int32(corners.ravel())
        cx, cy = np.int32(corners)
        for i in range(0,3):
            gx, gy = np.int32(imgpts[i].ravel())
            img = cv2.line(img, (cx, cy), (gx, gy), self.axes_color[i], 2)
            img = cv2.putText(img, self.xyz[i], (gx+10, gy-10), self.font , 1, self.axes_color[i], 2)
        return img

    @staticmethod
    def undistort(img, mtx, dist):
        h,  w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
        mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w,h), 5)
        return cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)

    @staticmethod
    def findChessboard_error(frame, msg):
        """ Error while working with frames """
        # msg = 'Chessboard Corners not found'
        cx = (frame.shape[1]//2)-200
        cy = frame.shape[0]//2
        cv2.rectangle(frame, (0, cy-40), (frame.shape[1], cy+20), cc.cerulean, -1)
        return cv2.putText(frame, msg, (cx, cy), font, 1, cc.white, 1)

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

