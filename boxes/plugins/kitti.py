"""
SLAM Box
Nodes for KITTI Vision Benchmark
"""

# import time
import numpy as np
import cv2
from boxes import RootNode, frame_error, Color, show_attributes, slam_toolbox

cc = Color()


class KITTICamera(RootNode):
    """
    SLAM KITTI Camera Node
    The camera intrinsic matrix represents the internal
    parameters of a camera, including the focal length,
    and it allows to project 3D points in the world
    onto the 2D image plane.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        file_name = self.param["file_name"]
        K, W, H = self.get_camera_matrix(file_name)
        self.buffer.variable["camera_data"] = [K, W, H]

    def out_frame(self):
        return self.get_frame(0)

    def get_camera_matrix(self, calib_file):
        with open(calib_file) as f:
            firstLine = f.readlines()[0][4:]
            focal, _, cx, _, _, _, cy, _, _, _, _, _ = list(
                map(float, firstLine.rstrip().split(" "))
            )

            K = np.zeros((3, 3))
            K[0, 0] = focal
            K[0, 2] = cx
            K[1, 1] = focal
            K[1, 2] = cy
            K[2, 2] = 1
            return K, int(cx * 2), int(cy * 2)

    def update(self, param):
        self.disabled = param["disabled"]
