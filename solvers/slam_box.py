"""
SLAM Box
Separate nodes(tools) for SLAM
"""

import numpy as np
import cv2
from .slam_toolbox import Frame, Map, Point, Display3D, generate_match, denormalize
from .root_nodes import Node
from .misc import Color, show_attributes

cc = Color()

def triangulate(pose1, pose2, pts1, pts2):
    """
    change on cv.triangulatePoints
    Recreating bunch of points using Triangulation
    Given the relative poses, calculating the 3d points
    """
    ret = np.zeros((pts1.shape[0], 4))
    pose1 = np.linalg.inv(pose1)
    pose2 = np.linalg.inv(pose2)
    for i, p in enumerate(zip(pts1, pts2)):
        A = np.zeros((4,4))
        A[0] = p[0][0] * pose1[2] - pose1[0]
        A[1] = p[0][1] * pose1[2] - pose1[1]
        A[2] = p[1][0] * pose2[2] - pose2[0]
        A[3] = p[1][1] * pose2[2] - pose2[1]
        _, _, vt = np.linalg.svd(A)
        ret[i] = vt[3]
    return ret / ret[:, 3:]

class DetectorDescriptor(Node):
    """
    SLAM Node 01
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.F = 400
        self.W, self.H = 1920//2, 1080//2
        self.K = np.array([[self.F, 0, self.W//2],
                            [0, self.F, self.H//2],
                            [0, 0, 1]])

        self.algorithm = self.param['algorithm']
        self.nfeatures = self.param['nfeatures']
        self.mapp = Map()
        # self.display3d = Display3D()

    def out_frame(self):
        image = self.get_frame(0)
        if image is None:
            print('DetectorDescriptor stop')
            return None
        if self.disabled: return image

        frame = Frame(self.mapp, image, self.K, self.algorithm)
        self.buffer.variable['slam_frame'] = frame
        self.buffer.variable['slam_map'] = self.mapp

        attributes = ['Algorithm: '+self.algorithm]
        return show_attributes(image, attributes)

    def update(self, param):
        self.disabled = param['disabled']
        self.algorithm = param['algorithm']
        self.nfeatures = param['nfeatures']


class MatchPoints(Node):
    """
    SLAM Node 02
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.F = 400
        self.W, self.H = 1920//2, 1080//2
        self.K = np.array([[self.F, 0, self.W//2],
                            [0, self.F, self.H//2],
                            [0, 0, 1]])

        self.marker_size = self.param['marker_size']
        self.show_marker = self.param['show_marker']

    def out_frame(self):
        image = self.get_frame(0)
        if image is None:
            print('MatchPoints stop')
            return None
        if self.disabled: return image

        frame = self.buffer.variable['slam_frame']
        mapp = self.buffer.variable['slam_map']
        if frame.id == 0:
            return image

        frame1 = mapp.frames[-1]
        frame2 = mapp.frames[-2]
        x1, x2, Id = generate_match(frame1, frame2)
        frame1.pose = Id @ frame2.pose
        for i, idx in enumerate(x2):
            if frame2.pts[idx] is not None:
                frame2.pts[idx].add_observation(frame1, x1[i])

        pts4d = triangulate(frame1.pose, frame2.pose, frame1.key_pts[x1], frame2.key_pts[x2])
        unmatched_points = np.array([frame1.pts[i] is None for i in x1])
        good_pts4d = (np.abs(pts4d[:, 3]) > 0.005) & (pts4d[:, 2] > 0) & unmatched_points

        for i, p in enumerate(pts4d):
            if not good_pts4d[i]:
                continue
            # get point color and add in list
            cx, cy = denormalize(self.K, frame1.key_pts[x1][i])
            color = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)[cy, cx]
            pt = Point(mapp, p[0:3], color)
            pt.add_observation(frame1, x1[i])
            pt.add_observation(frame2, x2[i])

        for pt1, pt2 in zip(frame1.key_pts[x1], frame2.key_pts[x2]):
            u1, v1 = denormalize(self.K, pt1)
            u2, v2 = denormalize(self.K, pt2)
            cv2.drawMarker(image, (u1, v1), (0, 255, 255), 1, 10, 1, 8)
            cv2.line(image, (u1, v1), (u2, v2), (0, 0, 255), 1)

        return image

    def update(self, param):
        self.disabled = param['disabled']
        self.marker_size = param['marker_size']
        self.show_marker = param['show_marker']

class Show3DMap(Node):
    """
    SLAM Node 02
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.marker_size = self.param['marker_size']
        self.marker_color = self.param['marker_color']
        self.show_marker = self.param['show_marker']
        self.display3d = Display3D()

    def out_frame(self):
        image = self.get_frame(0)
        if image is None:
            print('Show3DMap stop')
            return None

        if self.disabled: return image
        mapp = self.buffer.variable['slam_map']
        self.display3d.paint(mapp)

        return image

    def update(self, param):
        self.disabled = param['disabled']
        self.marker_size = param['marker_size']
        self.marker_color = param['marker_color']
        self.show_marker = param['show_marker']