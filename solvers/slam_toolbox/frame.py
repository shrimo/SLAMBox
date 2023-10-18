"""
frames processing
"""

import numpy as np
import cv2

def featureMappingORB(frame):
    orb = cv2.ORB_create()
    pts = cv2.goodFeaturesToTrack(np.mean(frame, axis=2).astype(np.uint8), 1000, qualityLevel=0.01, minDistance=7)
    key_pts = [cv2.KeyPoint(x=f[0][0], y=f[0][1], size=20) for f in pts]
    key_pts, descriptors = orb.compute(frame, key_pts)
    return np.array([(kp.pt[0], kp.pt[1]) for kp in key_pts]), descriptors

def featureMappingAKAZE(frame):
    detect = cv2.AKAZE_create()
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    key_pts, des = detect.detectAndCompute(frame_gray, None)
    return np.array([(kp.pt[0], kp.pt[1]) for kp in key_pts]), des

def normalize(count_inv, pts):
    return (count_inv @ np.concatenate([pts, np.ones((pts.shape[0], 1))], axis=1).T).T[:, 0:2]

def denormalize(count_inv, pt):
    ret = count_inv @ np.array([pt[0], pt[1], 1.0])
    ret /= ret[2]
    return np.int32(ret[0]), np.int32(ret[1])

Identity = np.eye(4)
FT = {'ORB':featureMappingORB, 'AKAZE':featureMappingAKAZE}
class Frame:
    """ Contains poses data """
    def __init__(self, mapp, image, count, algorithm):
        self.count_inv = np.linalg.inv(count)
        self.pose = Identity
        self.h, self.w = image.shape[0:2]
        key_pts, self.descriptors = FT[algorithm](image)
        self.key_pts = normalize(self.count_inv, key_pts)
        self.pts = [None]*len(self.key_pts)
        self.id = len(mapp.frames)
        mapp.frames.append(self)
        

