"""
Node and function library for Tracking
"""

import cv2
import numpy as np
from solvers_flask.root_nodes import Node
from solvers_flask.misc import insert_frame, get_tuple, show_attributes, Color

cc = Color()


class AllTrackers(Node):
    """
    A set of trackers available in the OpenCV library
    'BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'MOSSE', 'CSRT'
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.variable = self.param["variable"]
        self.show_ROI = self.param["show_ROI"]
        self.tracker_type = self.param["tracker_type"]
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.tracker = None
        self.go = None
        self.Image = None

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("AllTrackers a stop")
        elif self.disabled:
            return frame
        if self.buffer.roi:
            self.go = self.calculations_for_ROI(frame, self.buffer.roi)
            self.buffer.roi = self.empty_roi
        elif self.go:
            tmp, bbox = self.tracker.update(frame)
            (x, y, w, h) = [np.int32(pt) for pt in bbox]
            center = (np.int32(x + w * 0.5), np.int32(y + h * 0.5))
            self.buffer.variable[self.variable] = center
            cv2.rectangle(frame, (x, y), (x + w, y + h), cc.yellow, 1)
            cv2.circle(frame, center, 2, cc.red, -1)
            if self.show_ROI:
                insert_frame(frame, self.Image)

        return frame

    def calculations_for_ROI(self, frame, coord):
        """
        Set region of interest (ROI) and traker init
        """
        x0, y0, x1, y1 = coord
        track_window = (x0, y0, x1 - x0, y1 - y0)
        if not sum(track_window):
            return False
        print(f'window: {track_window}')
        self.tracker = self.get_tracker(self.tracker_type)
        tmp = self.tracker.init(frame, track_window)
        if not tmp:
            print("[ERROR] tracker not initialized")
        frame = frame[coord[1] : coord[3], coord[0] : coord[2]]
        self.Image = frame.copy()
        return True

    def get_tracker(self, tracker_type):
        return {
            "BOOSTING": cv2.legacy.TrackerBoosting_create(),
            "MIL": cv2.legacy.TrackerMIL_create(),
            "KCF": cv2.legacy.TrackerKCF_create(),
            "TLD": cv2.legacy.TrackerTLD_create(),
            "MEDIANFLOW": cv2.legacy.TrackerMedianFlow_create(),
            "MOSSE": cv2.legacy.TrackerMOSSE_create(),
            "CSRT": cv2.legacy.TrackerCSRT_create(),
        }[tracker_type]

    def update(self, param):
        self.disabled = param["disabled"]
        self.variable = param["variable"]
        self.show_ROI = param["show_ROI"]
        self.tracker_type = param["tracker_type"]
