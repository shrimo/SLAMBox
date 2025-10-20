"""
Description of the point and location map
"""

import numpy as np

from boxes.slam_toolbox.optimize_g2o import optimize

CULLING_ERR_THRES = 0.02
SLIDING_WINDOW_SIZE = 10  # number of keyframes to keep


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
        if len(self.pt.shape) == 1:
            return np.concatenate([self.pt, np.array([1.0])], axis=0)
        return np.concatenate([self.pt, np.ones((self.pt.shape[0], 1))], axis=1)

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
        self.max_point
        # priors collected from marginalization: list of dicts {'frame_id', 'pose', 'info'}
        self.priors = []

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
        slid_win=False,
    ):

        # Apply sliding window before optimization
        if slid_win:
            self.slide_window()

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

    def slide_window(self):
        """
        Keep only the most recent frames and points observed in them.
        """
        if len(self.frames) <= SLIDING_WINDOW_SIZE:
            return

        # keep only last N frames
        active_frames = self.frames[-SLIDING_WINDOW_SIZE:]
        active_frame_ids = {f.id for f in active_frames}

        # remove old frames
        old_frames = [f for f in self.frames if f.id not in active_frame_ids]
        for f in old_frames:
            self.frames.remove(f)

        # remove points that are not seen in active frames
        removed_points = 0
        for p in list(self.points):
            # keep point if any observation is from active frames
            if not any(f.id in active_frame_ids for f in p.frames):
                self.points.remove(p)
                p.delete()
                removed_points += 1

        print(
            f"[SlidingWindow] Removed {len(old_frames)} old frames and {removed_points} points."
        )
