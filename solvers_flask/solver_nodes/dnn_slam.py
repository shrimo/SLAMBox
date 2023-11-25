"""
Deep Neural Networks
Deep Learning with OpenCV DNN Module
"""

import cv2
import numpy as np
from solvers_flask import Node


class DNNMask(Node):
    """Deep Neural Networks. Mask for Detector Descriptor."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = self.param["config"]
        self.weights = self.param["weights"]
        self.threshold = float(self.param["threshold"])
        self.nms_threshold = float(self.param["nms_threshold"])
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.rand_color = np.random.uniform(0, 230, size=(100, 3))
        self.net = cv2.dnn_DetectionModel(self.weights, self.config)
        self.net.setInputSize(320, 320)
        self.net.setInputScale(1.0 / 127.5)
        self.net.setInputMean((127.5, 127.5, 127.5))
        self.net.setInputSwapRB(True)
        self.inclusion_list = [
            "train",
            "truck",
            "car",
            "bus",
            "motorcycle",
            "bicycle",
            "person",
            "bird"
        ]
        with open(self.param["class_names"]) as f:
            self.classNames = f.read().rstrip("\n").split("\n")
        self.show_mask = self.param["show_mask"]

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("DNNDetection stop")
            return None
        elif self.disabled:
            return frame
        classIds, confs, bbox = self.net.detect(frame, confThreshold=self.threshold)
        # lh, lw, lc = frame.shape
        if len(classIds):
            """NMSBoxes function, nms_threshold is the IOU threshold used in non-maximum suppression."""
            if self.show_mask:
                # width, height = self.buffer.metadata['frame_size']
                height, width = frame.shape[:-1]
                clean_plate = np.zeros((height, width, 3), np.uint8)
                clean_plate[:] = (255, 255, 255)
                indices = cv2.dnn.NMSBoxes(
                    bbox, confs, self.threshold, self.nms_threshold
                )
                for i in indices:
                    x, y, w, h = bbox[i][0], bbox[i][1], bbox[i][2], bbox[i][3]
                    label = self.classNames[classIds[i] - 1]
                    if label in self.inclusion_list:
                        cv2.rectangle(
                            clean_plate,
                            (x - 10, y - 10),
                            (x + w + 10, y + h + 10),
                            (0, 0, 0),
                            -1,
                        )
                return clean_plate

            else:
                indices = cv2.dnn.NMSBoxes(
                    bbox, confs, self.threshold, self.nms_threshold
                )
                for i in indices:
                    x, y, w, h = bbox[i][0], bbox[i][1], bbox[i][2], bbox[i][3]
                    label = self.classNames[classIds[i] - 1]
                    width_label = (6 * len(label)) + 16
                    color_rec = self.rand_color[classIds[i]]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color_rec, 2)
                    cv2.rectangle(
                        frame, (x, y), (x + width_label, y + 20), color_rec, -1
                    )
                    cv2.putText(
                        frame,
                        label,
                        (x + 2, y + 12),
                        self.font,
                        0.5,
                        (255, 255, 255),
                        1,
                    )
        return frame

    def update(self, param):
        self.disabled = param["disabled"]
        self.threshold = float(param["threshold"])
        self.nms_threshold = float(param["nms_threshold"])
        self.show_mask = param["show_mask"]
