"""
SLAM Box
Nodes for launching SLAM pipeline
"""

import time
import numpy as np

import cv2
from skimage.measure import LineModelND, ransac  # type: ignore
from .slam_toolbox import Kalman3D
from .root_nodes import Node
from .misc import Color, show_attributes, frame_error

cc = Color()


class GeneralGraphOptimization(Node):
    """
    SLAM GeneralGraphOptimization Node
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.solverSE3 = self.param["solverSE3"]
        self.step_frame = self.param["step_frame"]
        self.culled_pt = 0

    def out_frame(self):
        image = self.get_frame(0)
        if image is None:
            print("LineModelOptimization stop")
            return None
        elif self.disabled:
            return image
        elif not "slam_data" in self.buffer.variable:
            return frame_error(
                image,
                f"{self.type_} Slam data is missing",
                y_offset=100,
                x_offset=400,
            )

        frame, self.mapp = self.buffer.variable["slam_data"][:2]
        # optimize the map
        if frame.id >= 2 and frame.id % self.step_frame == 0:
            err, self.culled_pt = self.mapp.g2optimize(
                solverSE3=self.solverSE3
            )  # verbose=False
            # print("Optimize: %f units of error" % err)

        return show_attributes(
            image,
            [
                "solverSE3: " + self.solverSE3,
                "Culled: {} points".format(self.culled_pt),
            ],
            x_offset=200,
        )

    def update(self, param):
        self.disabled = param["disabled"]
        self.solverSE3 = param["solverSE3"]
        self.step_frame = param["step_frame"]


class LineModelOptimization(Node):
    """
    SLAM LineModelOptimization Node
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.m_samples = self.param["m_samples"]
        self.r_threshold = self.param["r_threshold"]
        self.m_trials = self.param["m_trials"]
        self.delete_points = self.param["delete_points"]

    def out_frame(self):
        image = self.get_frame(0)
        if image is None:
            print("LineModelOptimization stop")
            return None
        elif self.disabled:
            return image
        elif not "slam_data" in self.buffer.variable:
            return frame_error(
                image,
                f"{self.type_} Slam data is missing",
                y_offset=150,
                x_offset=400,
            )

        map_points = self.buffer.variable["slam_data"][1].points
        if map_points:
            points = np.array([(kp.pt[0], kp.pt[1]) for kp in map_points])
            model_robust, inliers = ransac(
                points,
                LineModelND,
                min_samples=self.m_samples,
                residual_threshold=self.r_threshold,
                max_trials=self.m_trials,
            )
            outliers = inliers == False
            for out_lie, ptx in zip(outliers, map_points):
                if out_lie:
                    if self.delete_points:
                        map_points.remove(ptx)  # remove outliers points
                    ptx.color = np.array([255.0, 0.0, 0.0])  # the point red color

        return image

    def update(self, param):
        self.disabled = param["disabled"]
        self.m_samples = param["m_samples"]
        self.r_threshold = param["r_threshold"]
        self.m_trials = param["m_trials"]
        self.delete_points = param["delete_points"]


class KalmanFilterOptimization(Node):
    """
    SLAM KalmanFilterOptimization Node
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.KF = Kalman3D(
            drag=self.param["drag"],
            debug=False,
            grav=self.param["grav"],
            procNoise=self.param["procNoise"],
            measNoise=self.param["measNoise"],
        )
        self.KF.init(np.float32([0.0, 0.0, 0.0]))
        self.fps = 1 / self.param["fps"]

    def out_frame(self):
        image = self.get_frame(0)
        if image is None:
            print("KalmanFilterOptimization stop")
            return None
        elif self.disabled:
            return image
        elif not "slam_data" in self.buffer.variable:
            return frame_error(
                image,
                f"{self.type_} Slam data is missing",
                y_offset=200,
                x_offset=400,
            )

        """The Kalman filter keeps track of the estimated state 
        of the system and the variance or uncertainty of the estimate. """
        current_pose = self.buffer.variable["slam_data"][0].pose
        x = current_pose.ravel()[3]
        y = current_pose.ravel()[7]
        z = current_pose.ravel()[11]

        track = self.KF.track(np.float32([x, y, z]), self.fps)
        pred = self.KF.predict(self.fps)

        # Position correction
        current_pose.ravel()[3] = pred[0]
        current_pose.ravel()[7] = pred[1]
        current_pose.ravel()[11] = pred[2]

        return image

    def update(self, param):
        self.disabled = param["disabled"]

