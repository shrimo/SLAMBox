"""
Description of the point and location map
"""

import numpy as np

from boxes.slam_toolbox.optimize_g2o import optimize

CULLING_ERR_THRES = 0.02

def hamming_distance(a, b):
    r = (1 << np.arange(8))[:, None]
    return np.count_nonzero((np.bitwise_xor(a, b) & r) != 0)


class Point:
    """
    A 3D point in the world coordinate system.
    Each point is observed in multiple frames.
    """

    def __init__(self, mapp, loc, color, tid=None):
        self.pt = np.array(loc)
        self.frames = []
        self.idxs = []
        self.color = np.copy(color)
        self.id = tid if tid is not None else mapp.add_point(self)

    def homogeneous(self):
        """Convert point to homogeneous coordinates."""
        if len(self.pt.shape) == 1:
            return np.concatenate([self.pt, np.array([1.0])], axis=0)
        return np.concatenate([self.pt, np.ones((self.pt.shape[0], 1))], axis=1)

    def orb(self):
        """Get ORB descriptors from all observations."""
        return [f.descriptors[idx] for f, idx in zip(self.frames, self.idxs)]

    def orb_distance(self, des):
        """Compute minimum Hamming distance to descriptor."""
        return min([hamming_distance(o, des) for o in self.orb()])

    def delete(self):
        """Remove this point from all frames."""
        for f, idx in zip(self.frames, self.idxs):
            f.pts[idx] = None
        del self

    def add_observation(self, frame, idx):
        """Add an observation of this point in a frame."""
        assert frame.pts[idx] is None
        assert frame not in self.frames
        frame.pts[idx] = self
        self.frames.append(frame)
        self.idxs.append(idx)


class Map:
    """
    Global map containing frames, 3D points, and bridge constraints.
    """
    
    def __init__(self):
        self.frames = []
        self.points = []
        self.max_frame = 0
        self.max_point = 0
        self.bridge_edges = []  # Store bridge constraints from marginalization
        self.frames_to_remove_after_opt = []  # Frames marked for removal after next optimization
        self.slid_win_size = 10

    def add_point(self, point):
        """Add a new point to the map."""
        ret = self.max_point
        self.max_point += 1
        self.points.append(point)
        return ret

    def add_frame(self, frame):
        """Add a new frame to the map."""
        ret = self.max_frame
        self.max_frame += 1
        self.frames.append(frame)
        return ret

    def g2optimize(
        self,
        local_window=20,
        fix_points=False,
        verbose=False,
        rounds=50,
        solverSE3="EigenSE3",
        slid_win=False,
        win_size=10,
    ):
        """
        Perform bundle adjustment optimization.
        
        Args:
            local_window: Number of recent frames to optimize
            fix_points: Keep 3D points fixed
            verbose: Enable verbose output
            rounds: Optimization iterations
            solverSE3: Linear solver type
            slid_win: Apply sliding window before optimization
            
        Returns:
            tuple: (error, culled_points_count)
        """

        # Sliding window logic (only if enabled)
        if slid_win:
            self.slid_win_size = win_size
            # FIRST: Remove frames that were marked in previous sliding window
            if self.frames_to_remove_after_opt:
                print(f"[Map] Removing {len(self.frames_to_remove_after_opt)} frames marked in previous sliding window")
                self._remove_old_frames(self.frames_to_remove_after_opt)
                self.frames_to_remove_after_opt = []

            # SECOND: Apply sliding window (marks frames for NEXT optimization)
            self.slide_window()

            # THIRD: Run optimization with current frames and bridges
            err = optimize(
                self.frames,
                self.points,
                local_window,
                fix_points,
                verbose,
                rounds,
                solverSE3,
                bridge_edges=self.bridge_edges,
            )
        else:
            # No sliding window - standard optimization without bridges
            err = optimize(
                self.frames,
                self.points,
                local_window,
                fix_points,
                verbose,
                rounds,
                solverSE3,
                bridge_edges=None,  # No bridge constraints
            )

        # FOURTH: Prune low-quality points
        culled_pt_count = 0
        for p in self.points[:]:
            # Old points with few observations
            old_point = len(p.frames) <= 4 and p.frames[-1].id + 7 < self.max_frame

            # Compute reprojection errors
            errs = []
            for f, idx in zip(p.frames, p.idxs):
                uv = f.kps[idx]
                proj = f.pose[:3] @ p.homogeneous()
                proj = proj[0:2] / proj[2]
                errs.append(np.linalg.norm(proj - uv))

            # Cull bad points
            if old_point or np.mean(errs) > CULLING_ERR_THRES:
                culled_pt_count += 1
                self.points.remove(p)
                p.delete()
        
        return err, culled_pt_count

    def slide_window(self):
        """
        Sliding window: create bridge and mark old frames for removal.
        Frames will be removed at the START of NEXT g2optimize() call.
        """
        if len(self.frames) <= self.slid_win_size:
            return

        # Identify frames to keep and mark for removal
        frames_to_mark = self.frames[:-self.slid_win_size]
        frames_to_keep = self.frames[-self.slid_win_size:]
        
        if not frames_to_mark:
            return
            
        last_old = frames_to_mark[-1]
        first_new = frames_to_keep[0]

        print(f"[SlidingWindow] Total frames: {len(self.frames)}")
        print(f"[SlidingWindow] Marking {len(frames_to_mark)} frames for removal: {[f.id for f in frames_to_mark]}")
        print(f"[SlidingWindow] Will keep: {[f.id for f in frames_to_keep]}")

        # Create bridge constraint between last old and first new
        T_old = last_old.pose
        T_new = first_new.pose
        rel_T = np.linalg.inv(T_old) @ T_new

        # Important: Store bridge with CURRENT frame IDs before removal
        # After old frames are removed, this bridge becomes a "fixed constraint"
        # that keeps the trajectory connected
        bridge_data = {
            "from_id": last_old.id,
            "to_id": first_new.id,
            "rel_pose": rel_T,
            "info": np.eye(6) * 100.0,
            "is_active": True  # Bridge is active while both frames exist
        }
        
        # Check if this bridge already exists
        bridge_exists = any(
            b["from_id"] == last_old.id and b["to_id"] == first_new.id 
            for b in self.bridge_edges
        )
        
        if not bridge_exists:
            self.bridge_edges.append(bridge_data)
            print(f"[SlidingWindow] Created bridge {last_old.id}→{first_new.id}")
        else:
            print(f"[SlidingWindow] Bridge {last_old.id}→{first_new.id} already exists")

        # Mark frames for removal (will be removed at start of NEXT optimization)
        self.frames_to_remove_after_opt = frames_to_mark[:]
        print(f"[SlidingWindow] Frames will be removed in NEXT optimization call")

    def _remove_old_frames(self, frames_to_remove):
        """
        Remove old frames and their orphaned points.
        """
        frames_to_keep = [f for f in self.frames if f not in frames_to_remove]
        removed_frame_ids = {f.id for f in frames_to_remove}
        
        # Remove points that are ONLY observed in old frames
        points_removed = 0
        for point in self.points[:]:
            has_new_observations = any(f in frames_to_keep for f in point.frames)
            
            if not has_new_observations:
                self.points.remove(point)
                point.delete()
                points_removed += 1
            else:
                # Remove observations from old frames
                for i in range(len(point.frames) - 1, -1, -1):
                    if point.frames[i] in frames_to_remove:
                        frame = point.frames[i]
                        idx = point.idxs[i]
                        if idx < len(frame.pts) and frame.pts[idx] is point:
                            frame.pts[idx] = None
                        point.frames.pop(i)
                        point.idxs.pop(i)

        print(f"[Cleanup] Removed {points_removed} orphaned points")

        # Remove old frames
        for frame in frames_to_remove:
            if frame in self.frames:
                self.frames.remove(frame)
        
        print(f"[Cleanup] Removed {len(frames_to_remove)} frames: {sorted(removed_frame_ids)}")
        
        # Clean up bridges: remove those where from_id no longer exists
        # These bridges have already served their purpose during the last optimization
        remaining_frame_ids = {f.id for f in self.frames}
        old_bridge_count = len(self.bridge_edges)
        
        self.bridge_edges = [
            b for b in self.bridge_edges 
            if b["from_id"] in remaining_frame_ids and b["to_id"] in remaining_frame_ids
        ]
        
        removed_bridges = old_bridge_count - len(self.bridge_edges)
        if removed_bridges > 0:
            print(f"[Cleanup] Removed {removed_bridges} used bridges (they already did their job)")
        
        print(f"[Cleanup] Map now: {len(self.frames)} frames, {len(self.points)} points, {len(self.bridge_edges)} active bridges")
