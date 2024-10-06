"""
Node and function library for Tracking
"""

import cv2
import numpy as np
from boxes import RootNode, insert_frame, Color

cc = Color()


class VitTrack(RootNode):
    """
    VIT tracker(vision transformer tracker)
    is a much better model for real-time object tracking.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.variable = self.param["variable"]
        self.show_ROI = self.param["show_ROI"]
        self.model_path = self.param["model_path"]
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.go = False
        self.Image = None
        self.backend_target_pairs = [cv2.dnn.DNN_BACKEND_OPENCV, cv2.dnn.DNN_TARGET_CPU]
        self.backend_id = self.backend_target_pairs[0]
        self.target_id = self.backend_target_pairs[1]
        self.params = cv2.TrackerVit_Params()
        self.params.net = self.model_path
        self.params.backend = self.backend_id
        self.params.target = self.target_id
        self.model = cv2.TrackerVit_create(self.params)

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("VitTrack stop")
        elif self.disabled:
            return frame
        elif self.buffer.switch:
            self.go = self.calculations_for_ROI(frame, self.buffer.roi)
            self.buffer.switch = False
        elif self.go:
            isLocated, bbox, score = self.infer(frame)
            self.visualize(frame, bbox, score, isLocated)
            if self.show_ROI:
                insert_frame(frame, self.Image)

        return frame

    def calculations_for_ROI(self, frame, coord):
        """
        Set region of interest (ROI) and traker init
        """
        x0, y0, x1, y1 = coord
        track_window = (x0, y0, x1 - x0, y1 - y0)
        # print(f'window: {track_window}')

        tmp = self.model.init(frame, track_window)
        if not tmp:
            print("[ERROR] tracker not initialized")
        frame = frame[coord[1] : coord[3], coord[0] : coord[2]]
        self.Image = frame.copy()
        return True

    def infer(self, image):
        is_located, bbox = self.model.update(image)
        score = self.model.getTrackingScore()
        return is_located, bbox, score

    def visualize(
        self,
        frame,
        bbox,
        score,
        isLocated,
        fontScale=0.5,
        fontSize=1,
    ):
        h, w, _ = frame.shape

        if isLocated and score >= 0.3:
            # bbox: Tuple of length 4
            x, y, w, h = bbox
            cv2.rectangle(frame, (x, y), (x + w, y + h), cc.yellow, 1)
            label = "{:.2f}".format(score)
            width_label = (6 * len(label)) + 16
            cv2.rectangle(frame, (x, y), (x + width_label, y + 20), cc.yellow, -1)
            cv2.putText(
                frame,
                label,
                (x + 2, y + 15),
                self.font,
                fontScale,
                cc.gray,
                fontSize,
            )
            center = (np.int32(x + w * 0.5), np.int32(y + h * 0.5))
            cv2.circle(frame, center, 2, cc.red, -1)
        else:
            text_size, baseline = cv2.getTextSize(
                "Target lost", cv2.FONT_HERSHEY_DUPLEX, fontScale, fontSize
            )
            text_x = int((w - text_size[0]) / 2)
            text_y = int((h - text_size[1]) / 2)
            cv2.putText(
                frame,
                "Target lost!",
                (text_x, text_y),
                cv2.FONT_HERSHEY_DUPLEX,
                fontScale,
                cc.red,
                fontSize,
            )

        return frame

    def update(self, param):
        self.disabled = param["disabled"]
        self.model_path = param["model_path"]
        self.variable = param["variable"]
        self.show_ROI = param["show_ROI"]
