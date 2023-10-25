"""
Python implementation of an ORB/AKAZE/SURF feature matching
based Monocular-vision SLAM.
"""

import numpy as np
import cv2
# from numba import njit
from .camera import denormalize, Camera
from .match_frames import generate_match
from .descriptor import Descriptor, Point

# @njit
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

class MVSLAM:
    """ Monocular-vision SLAM. """
    def __init__(self, focal_length = 500, width = 1920, height = 1080, algorithm = 'ORB'):
        self.F = focal_length
        self.algorithm = algorithm
        # self.W, self.H = width, height
        self.W, self.H = width//2, height//2
        self.K = np.array([[self.F, 0, self.W//2],
                            [0, self.F, self.H//2],
                            [0, 0, 1]])
        self.desc_solver = Descriptor()
        self.desc_solver.create_viewer()
        self.image = None
        print('Init {} SLAM'.format(self.algorithm), '\nFocal length:', self.F)
        self.slam_pose = None

    def calibrate(self, image):
        # camera intrinsics...<================ Check this
        return cv2.resize(image, (self.W, self.H))

    def generate(self, image, matcher, trials, optimization):
        # self.image = image
        self.image = self.calibrate(image)
        frame = Camera(self.desc_solver, self.image, self.K, self.algorithm)
        if frame.id == 0:
            return
        frame1 = self.desc_solver.frames[-1]
        frame2 = self.desc_solver.frames[-2]
        x1, x2, Id = generate_match(frame1, frame2, matcher, trials)
        frame1.pose = Id @ frame2.pose
        for i, idx in enumerate(x2):
            if frame2.pts[idx] is not None:
                frame2.pts[idx].add_observation(frame1, x1[i])
        # homogeneous 3-D coords
        pts4d = triangulate(frame1.pose, frame2.pose, frame1.key_pts[x1], frame2.key_pts[x2])
        # pts4d /= pts4d[:, 3:]
        unmatched_points = np.array([frame1.pts[i] is None for i in x1])
        # print("Adding:  %d points" % np.sum(unmatched_points))
        good_pts4d = (np.abs(pts4d[:, 3]) > 0.005) & (pts4d[:, 2] > 0) & unmatched_points

        for i, p in enumerate(pts4d):
            if not good_pts4d[i]:
                continue
            pt = Point(self.desc_solver, p)
            pt.add_observation(frame1, x1[i])
            pt.add_observation(frame2, x2[i])
            # get point color and add in list
            cx, cy = denormalize(self.K, frame1.key_pts[x1][i])
            pt.add_color(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)[cy, cx])

        for pt1, pt2 in zip(frame1.key_pts[x1], frame2.key_pts[x2]):
            u1, v1 = denormalize(self.K, pt1)
            u2, v2 = denormalize(self.K, pt2)
            cv2.drawMarker(self.image, (u1, v1), (0, 255, 255), 1, 10, 1, 8)
            cv2.line(self.image, (u1, v1), (u2, v2), (0, 0, 255), 1)

        # Points Optimization
        if optimization:
            # g2o optimization in development
            # if frame.id >= 4 and frame.id%5 == 0:
            #   err = self.desc_solver.optimize() #verbose=True)
            #   print("Optimize: %f units of error" % err)

            self.desc_solver.LineModelOptimization(m_samples=8, r_threshold=80, m_trials=100)
            self.desc_solver.KalmanFilterOptimization()
        # 3D display (put 3D data in Queue)
        self.desc_solver.put3D()
        # write data to slam_pose attribut for send to buffer variable 
        self.slam_pose = (self.desc_solver.frames[-1].pose.ravel()[3],
                        self.desc_solver.frames[-1].pose.ravel()[7], 
                        self.desc_solver.frames[-1].pose.ravel()[11])
        # xpos = self.desc_solver.frames[-1].pose.ravel()[3]
        # ypos = self.desc_solver.frames[-1].pose.ravel()[7]
        # zpos = self.desc_solver.frames[-1].pose.ravel()[11]
        # print(self.slam_pose)

    def __del__(self):
        print('Close SLAM D')
        return self.desc_solver.release()

    def slam_release(self):
        ''' Close object '''
        print('Close SLAM R')
        self.desc_solver.release()
        cv2.waitKey(3)
        return True
