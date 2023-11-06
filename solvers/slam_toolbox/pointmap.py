"""
Description of the point and location map
"""

import sys

sys.path.append("/home/cds/github/g2o-pymem/build/lib")

import numpy as np

# import g2opy # type: ignore
from .optimize_g2o import optimize

CULLING_ERR_THRES = 0.02


def add_ones(x):
    if len(x.shape) == 1:
        return np.concatenate([x, np.array([1.0])], axis=0)
    else:
        return np.concatenate([x, np.ones((x.shape[0], 1))], axis=1)


def hamming_distance(a, b):
    r = (1 << np.arange(8))[:, None]
    return np.count_nonzero((np.bitwise_xor(a, b) & r) != 0)


class Point:
    # A Point is a 3-D point in the world
    # Each Point is observed in multiple Frames

    def __init__(self, mapp, loc, color, tid=None):
        self.pt = np.array(loc)
        self.frames = []
        self.idxs = []
        self.color = np.copy(color)
        self.id = tid if tid is not None else mapp.add_point(self)

    def homogeneous(self):
        return add_ones(self.pt)

    def orb(self):
        return [f.descriptors[idx] for f, idx in zip(self.frames, self.idxs)]

    def orb_distance(self, des):
        return min([hamming_distance(o, des) for o in self.orb()])

    def delete(self):
        for f, idx in zip(self.frames, self.idxs):
            f.pts[idx] = None
        del self

    def add_observation(self, frame, idx):
        assert frame.pts[idx] is None
        assert frame not in self.frames
        frame.pts[idx] = self
        self.frames.append(frame)
        self.idxs.append(idx)


class Map:
    def __init__(self):
        self.frames = []
        self.points = []
        self.max_frame = 0
        self.max_point = 0

    def add_point(self, point):
        ret = self.max_point
        self.max_point += 1
        self.points.append(point)
        return ret

    def add_frame(self, frame):
        ret = self.max_frame
        self.max_frame += 1
        self.frames.append(frame)
        return ret

    # Optimizer
    def g2optimize(
        self,
        local_window=20,
        fix_points=False,
        verbose=False,
        rounds=50,
        solverSE3="SolverEigenSE3",
    ):
        err = optimize(
            self.frames,
            self.points,
            local_window,
            fix_points,
            verbose,
            rounds,
            solverSE3,
        )

        # prune points
        culled_pt_count = 0
        for p in self.points:
            # <= 4 match point that's old
            old_point = len(p.frames) <= 4 and p.frames[-1].id + 7 < self.max_frame

            # compute reprojection error
            errs = []
            for f, idx in zip(p.frames, p.idxs):
                uv = f.kps[idx]
                proj = f.pose[:3] @ p.homogeneous()
                proj = proj[0:2] / proj[2]
                errs.append(np.linalg.norm(proj - uv))

            # cull
            if old_point or np.mean(errs) > CULLING_ERR_THRES:
                culled_pt_count += 1
                self.points.remove(p)
                p.delete()
        # print("Culled:   %d points" % (culled_pt_count))
        # print("Optimize: %f units of error" % err)
        return err, culled_pt_count
