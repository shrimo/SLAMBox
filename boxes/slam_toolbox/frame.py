"""
frames processing
"""

import numpy as np
import cv2
from scipy.spatial import cKDTree  # type: ignore


def featureMappingORB(*frame):
    orb = cv2.ORB_create()
    pts = cv2.goodFeaturesToTrack(
        np.mean(frame[0], axis=2).astype(np.uint8),
        frame[2],
        qualityLevel=0.01,
        minDistance=7,
        mask=frame[1],
    )
    key_pts = [cv2.KeyPoint(x=f[0][0], y=f[0][1], size=20) for f in pts]
    key_pts, descriptors = orb.compute(frame[0], key_pts)
    return np.array([(kp.pt[0], kp.pt[1]) for kp in key_pts]), descriptors


def featureMappingAKAZE(*frame):
    detect = cv2.AKAZE_create()
    frame_gray = cv2.cvtColor(frame[0], cv2.COLOR_BGR2GRAY)
    key_pts, des = detect.detectAndCompute(frame_gray, None)
    return np.array([(kp.pt[0], kp.pt[1]) for kp in key_pts]), des


def normalize(count_inv, pts):
    return (count_inv @ np.concatenate([pts, np.ones((pts.shape[0], 1))], axis=1).T).T[
        :, 0:2
    ]


def denormalize(count_inv, pt):
    ret = count_inv @ np.array([pt[0], pt[1], 1.0])
    ret /= ret[2]
    return np.int32(ret[0]), np.int32(ret[1])


FT = {"ORB": featureMappingORB, "AKAZE": featureMappingAKAZE}


class Frame:
    """Contains poses data"""

    def __init__(
        self,
        mapp,
        image,
        K,
        pose=np.eye(4),
        tid=None,
        verts=None,
        algorithm="ORB",
        mask=None,
        nfeatures=1000,
    ):
        self.K = np.array(K)
        self.pose = np.array(pose)
        self.h, self.w = image.shape[0:2]
        self.key_pts, self.descriptors = FT[algorithm](image, mask, nfeatures)
        self.pts = [None] * len(self.key_pts)
        self.id = tid if tid is not None else mapp.add_frame(self)

    # inverse of intrinsics matrix
    @property
    def Kinv(self):
        if not hasattr(self, "_Kinv"):
            self._Kinv = np.linalg.inv(self.K)
        return self._Kinv

    # normalized keypoints
    @property
    def kps(self):
        if not hasattr(self, "_kps"):
            self._kps = normalize(self.Kinv, self.key_pts)
        return self._kps

    # KD tree of unnormalized keypoints
    @property
    def kd(self):
        if not hasattr(self, "_kd"):
            self._kd = cKDTree(self.key_pts)
        return self._kd
