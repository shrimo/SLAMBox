"""
In computer vision, triangulation refers to the process 
of determining a point in 3D space given its projections onto two,
or more, images. In order to solve this problem it is necessary to
know the parameters of the camera projection function from 3D to 2D
for the cameras involved, in the simplest case represented
by the camera matrices. 
"""

import numpy as np


def triangulate(pose1, pose2, pts1, pts2):
    """Taking into account relative poses,
    we calculate the 3d point.
    linalg.svd - Singular Value Decomposition.
    """
    ret = np.zeros((pts1.shape[0], 4))
    for i, p in enumerate(zip(pts1, pts2)):
        A = np.zeros((4, 4))
        A[0] = p[0][0] * pose1[2] - pose1[0]
        A[1] = p[0][1] * pose1[2] - pose1[1]
        A[2] = p[1][0] * pose2[2] - pose2[0]
        A[3] = p[1][1] * pose2[2] - pose2[1]
        _, _, vt = np.linalg.svd(A)
        ret[i] = vt[3]
    return ret
