"""
SLAM Box
Separate nodes(tools) for SLAM
"""

import time
import numpy as np
import cv2
from skimage.measure import LineModelND, ransac # type: ignore
from .slam_toolbox import (Frame, Map, Point, 
    DisplayOpen3D, match_frame)
from .root_nodes import Node
from .misc import Color, show_attributes

cc = Color()

def triangulate(pose1, pose2, pts1, pts2):
    ret = np.zeros((pts1.shape[0], 4))
    for i, p in enumerate(zip(pts1, pts2)):
        A = np.zeros((4,4))
        A[0] = p[0][0] * pose1[2] - pose1[0]
        A[1] = p[0][1] * pose1[2] - pose1[1]
        A[2] = p[1][0] * pose2[2] - pose2[0]
        A[3] = p[1][1] * pose2[2] - pose2[1]
        _, _, vt = np.linalg.svd(A)
        ret[i] = vt[3]
    return ret

class DetectorDescriptor(Node):
    """
    SLAM Node 01
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.F = 500
        self.W, self.H = 1920, 1080

        if self.W > 1024:
            downscale = 1024.0/self.W
            self.F *= downscale
            self.H = int(self.H * downscale)
            self.W = 1024

        # print(self.W, self.H)
        # The camera intrinsic matrix represents the internal 
        # parameters of a camera, including the focal length, 
        # and it allows to project 3D points in the world 
        # onto the 2D image plane. 
        self.K = np.array([[self.F, 0, self.W//2],
                            [0, self.F, self.H//2],
                            [0, 0, 1]])

        self.algorithm = self.param['algorithm']
        self.nfeatures = self.param['nfeatures']
        self.show_points = self.param['show_points']
        self.mapp = Map()
        self.mask = None

    def out_frame(self):
        image = self.get_frame(0)
        if image is None:
            print('DetectorDescriptor stop')
            return None
        if len(self.get_input()) > 1:
            self.mask = cv2.cvtColor(self.get_frame(1), cv2.COLOR_BGR2GRAY)
        if self.disabled: return image
        frame = Frame(self.mapp, image, self.K, verts=None, algorithm = self.algorithm, mask=self.mask)
        # save the received object in a buffer
        self.buffer.variable['slam_data'] = [frame, self.mapp, self.K, self.W, self.H]
        if self.show_points:
            for fpt in frame.key_pts:
                cv2.circle(image, np.int32(fpt), 3, cc.green, 1)

        attributes = ['Algorithm: '+self.algorithm]
        return show_attributes(image, attributes)

    def update(self, param):
        self.disabled = param['disabled']
        self.algorithm = param['algorithm']
        self.nfeatures = param['nfeatures']
        self.show_points = param['show_points']

class MatchPoints(Node):
    """
    SLAM Node 02
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.K = None
        self.mapp = None
        self.m_samples = self.param['m_samples']
        self.r_threshold = self.param['r_threshold']
        self.m_trials = self.param['m_trials']
        self.marker_size = self.param['marker_size']
        self.show_marker = self.param['show_marker']

    def out_frame(self):
        # start_time = time.time()
        image = self.get_frame(0)
        if image is None:
            print('MatchPoints stop')
            return None
        if self.disabled: return image

        frame, self.mapp, self.K, self.W, self.H = self.buffer.variable['slam_data']
        if frame.id == 0:
            return image

        f1 = self.mapp.frames[-1]
        f2 = self.mapp.frames[-2]

        idx1, idx2, Rt = match_frame(f1, f2, self.m_samples, self.r_threshold, self.m_trials)

        # add new observations if the point is already observed in the previous frame
        # TODO: consider tradeoff doing this before/after search by projection
        for i, idx in enumerate(idx2):
            if f2.pts[idx] is not None and f1.pts[idx1[i]] is None:
                f2.pts[idx].add_observation(f1, idx1[i])

        # get initial positions from fundamental matrix
        f1.pose = Rt @ f2.pose

        # pose optimization
        # pose_opt = self.mapp.optimize(local_window=1, fix_points=True)
        # sbp_pts_count = 0

        # search by projection
        if len(self.mapp.points) > 0:
            # project *all* the map points into the current frame
            map_points = np.array([p.homogeneous() for p in self.mapp.points])
            projs = (self.K @ f1.pose[:3] @ map_points.T).T
            projs = projs[:, 0:2] / projs[:, 2:]

            # only the points that fit in the frame
            good_pts = (projs[:, 0] > 0) & (projs[:, 0] < self.W) & \
                                 (projs[:, 1] > 0) & (projs[:, 1] < self.H)

            for i, p in enumerate(self.mapp.points):
                if not good_pts[i]:
                    # point not visible in frame
                    continue
                if f1 in p.frames:
                    # we already matched this map point to this frame
                    # TODO: understand this better
                    continue
                for m_idx in f1.kd.query_ball_point(projs[i], 2):
                    # if point unmatched
                    if f1.pts[m_idx] is None:
                        b_dist = p.orb_distance(f1.descriptors[m_idx])
                        # if any descriptors within 64
                        if b_dist < 64.0:
                            p.add_observation(f1, m_idx)
                            # sbp_pts_count += 1
                            break

        # triangulate the points we don't have matches for
        good_pts4d = np.array([f1.pts[i] is None for i in idx1])

        # do triangulation in global frame
        pts4d = triangulate(f1.pose, f2.pose, f1.kps[idx1], f2.kps[idx2])
        good_pts4d &= np.abs(pts4d[:, 3]) != 0
        pts4d /= pts4d[:, 3:]       # homogeneous 3-D coords

        # adding new points to the map from pairwise matches
        new_pts_count = 0
        for i, p in enumerate(pts4d):
            if not good_pts4d[i]:
                continue

            # check parallax is large enough
            # TODO: learn what parallax means
            """
            r1 = np.dot(f1.pose[:3, :3], add_ones(f1.kps[idx1[i]]))
            r2 = np.dot(f2.pose[:3, :3], add_ones(f2.kps[idx2[i]]))
            parallax = r1.dot(r2) / (np.linalg.norm(r1) * np.linalg.norm(r2))
            if parallax >= 0.9998:
                continue
            """

            # check points are in front of both cameras
            pl1 = f1.pose @ p
            pl2 = f2.pose @ p
            if pl1[2] < 0 or pl2[2] < 0:
                continue

            # reproject
            pp1 = self.K @ pl1[:3]
            pp2 = self.K @ pl2[:3]

            # check reprojection error
            pp1 = (pp1[0:2] / pp1[2]) - f1.key_pts[idx1[i]]
            pp2 = (pp2[0:2] / pp2[2]) - f2.key_pts[idx2[i]]
            pp1 = np.sum(pp1**2)
            pp2 = np.sum(pp2**2)
            if pp1 > 2 or pp2 > 2:
                continue

            # color points from frame
            cx = np.int32(f1.key_pts[idx1[i],0])
            cy = np.int32(f1.key_pts[idx1[i],1])
            color = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)[cy, cx]

            pt = Point(self.mapp, p[0:3], color)
            pt.add_observation(f2, idx2[i])
            pt.add_observation(f1, idx1[i])
            new_pts_count += 1

        # print("Adding:   %d new points, %d search by projection" % (new_pts_count, sbp_pts_count))

        # print("Map:      %d points, %d frames" % (len(self.mapp.points), len(self.mapp.frames)))
        # print("Time:     %.2f ms" % ((time.time()-start_time)*1000.0))
        # print(np.linalg.inv(f1.pose))
        if self.show_marker:
            for pt1, pt2 in zip(f1.key_pts[idx1], f2.key_pts[idx2]):
                cv2.circle(image, np.int32(pt1), self.marker_size, (0, 255, 255))
                cv2.line(image, np.int32(pt1), np.int32(pt2), (0, 0, 255), 1)

        return image

    def update(self, param):
        self.disabled = param['disabled']
        self.m_samples = param['m_samples']
        self.r_threshold = param['r_threshold']
        self.m_trials = param['m_trials']
        self.marker_size = param['marker_size']
        self.show_marker = param['show_marker']

class Open3DMap(Node):
    """
    SLAM Node 03
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.amount = 500
        self.point_size = self.param['point_size']
        self.point_color = self.param['point_color']
        self.d3d = DisplayOpen3D(width=1280, height=720, scale=0.05, point_size=self.point_size)

    def out_frame(self):
        image = self.get_frame(0)
        if image is None:
            print('Open3DMap stop')
            return None
        if self.disabled: return image
        if self.buffer.variable['slam_data']:
            self.d3d.send_to_visualization(self.buffer.variable['slam_data'][1], self.point_size)

        return image

    def update(self, param):
        self.disabled = param['disabled']
        self.point_size = param['point_size']
        self.point_color = param['point_color']
        self.point_size = param['point_size']


class LineModelOptimization(Node):
    """
    SLAM Node 04
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.m_samples = self.param['m_samples']
        self.r_threshold = self.param['r_threshold']
        self.m_trials = self.param['m_trials']
        self.delete_points = self.param['delete_points']

    def out_frame(self):
        image = self.get_frame(0)
        if image is None:
            print('LineModelOptimization stop')
            return None
        if self.disabled: return image

        map_points = self.buffer.variable['slam_data'][1].points
        if map_points:
            points = np.array([(kp.pt[0], kp.pt[1]) for kp in map_points])
            model_robust, inliers = ransac(points, LineModelND, min_samples=self.m_samples,
                                           residual_threshold=self.r_threshold, 
                                           max_trials=self.m_trials)
            outliers = inliers == False
            for out_lie, ptx in zip(outliers, map_points):
                if out_lie:
                    if self.delete_points:
                        map_points.remove(ptx) # remove outliers points
                    ptx.color = np.array([255.0, 0.0, 0.0]) # the point red color

        return image

    def update(self, param):
        self.disabled = param['disabled']
        self.m_samples = param['m_samples']
        self.r_threshold = param['r_threshold']
        self.m_trials = param['m_trials']
        self.delete_points = param['delete_points']


class GeneralGraphOptimization(Node):
    """
    SLAM Node 05
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mapp = None
        self.step_frame = self.param['step_frame']
        self.delete_points = self.param['delete_points']

    def out_frame(self):
        image = self.get_frame(0)
        if image is None:
            print('LineModelOptimization stop')
            return None
        if self.disabled: return image

        frame, self.mapp = self.buffer.variable['slam_data'][:2]
        # optimize the map        
        if frame.id >= 2 and frame.id % self.step_frame == 0:
            err = self.mapp.optimize() #verbose=True)
            # print("Optimize: %f units of error" % err)

        return image

    def update(self, param):
        self.disabled = param['disabled']
        self.step_frame = param['step_frame']
        self.delete_points = param['delete_points']


