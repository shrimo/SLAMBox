"""
SLAM Box
Nodes for launching SLAM pipeline
"""

# import time
import numpy as np
import cv2
from boxes import RootNode, frame_error, Color, show_attributes, slam_toolbox

cc = Color()


class Camera(RootNode):
    """
    SLAM Camera Node
    The camera intrinsic matrix represents the internal
    parameters of a camera, including the focal length,
    and it allows to project 3D points in the world
    onto the 2D image plane.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        F = self.param["focal_length"]
        W = self.param["frame_width"]
        H = self.param["frame_height"]

        # Loading Camera Calibration Data
        # self.calibration_data = self.param['calibration_data']
        # cal_data = np.load(self.param['calibration_data'])
        # K = cal_data.get('intrinsic_matrix')

        K = self.camera_intrinsic_matrix(F, W, H)
        self.buffer.variable["camera_data"] = [K, W, H]

    def out_frame(self):
        return self.get_frame(0)

    def camera_intrinsic_matrix(self, F, W, H):
        # Camera Intrinsic Matrix (Camera-to-Image, Image-to-Pixel):
        if W > 1024:
            downscale = 1024.0 / W
            F *= downscale
            H = int(H * downscale)
            W = 1024
        return np.array([[F, 0, W // 2], [0, F, H // 2], [0, 0, 1]])

    def update(self, param):
        self.disabled = param["disabled"]
        F = param["focal_length"]
        W = param["frame_width"]
        H = param["frame_height"]
        # self.calibration_data = param['calibration_data']
        K = self.camera_intrinsic_matrix(F, W, H)
        self.buffer.variable["camera_data"] = [K, W, H]


class DetectorDescriptor(RootNode):
    """
    SLAM DetectorDescriptor Node
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.algorithm = self.param["algorithm"]
        self.nfeatures = self.param["nfeatures"]
        self.show_points = self.param["show_points"]
        self.mapp = slam_toolbox.Map()
        self.mask = None

    def out_frame(self):
        image = self.get_frame(0)
        if image is None:
            print("DetectorDescriptor stop")
            return None
        if len(self.get_input()) > 1:
            self.mask = cv2.cvtColor(self.get_frame(1), cv2.COLOR_BGR2GRAY)
        if self.disabled:
            return image
        # Read Camera data
        if not "camera_data" in self.buffer.variable:
            return frame_error(
                image,
                f"{self.type_} Camera node is missing",
                y_offset=-50,
                x_offset=400,
            )
        K, W, H = self.buffer.variable["camera_data"]
        frame = slam_toolbox.Frame(
            self.mapp,
            image,
            K,
            verts=None,
            algorithm=self.algorithm,
            mask=self.mask,
            nfeatures=self.nfeatures,
        )
        # save the received object in a buffer
        self.buffer.variable["slam_data"] = [frame, self.mapp, K, W, H]
        if self.show_points:
            for fpt in frame.key_pts:
                cv2.circle(image, np.int32(fpt), 5, cc.green, 1)

        attributes = ["Algorithm: " + self.algorithm]
        return show_attributes(image, attributes)

    def update(self, param):
        self.disabled = param["disabled"]
        self.algorithm = param["algorithm"]
        self.nfeatures = param["nfeatures"]
        self.show_points = param["show_points"]


class MatchPoints(RootNode):
    """
    SLAM MatchPoints Node
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.m_samples = self.param["m_samples"]
        self.r_threshold = self.param["r_threshold"]
        self.m_trials = self.param["m_trials"]
        self.marker_size = self.param["marker_size"]
        self.show_marker = self.param["show_marker"]

    def out_frame(self):
        # start_time = time.time()
        image = self.get_frame(0)
        if image is None:
            print("MatchPoints stop")
            return None
        elif self.disabled:
            return image
        elif not "slam_data" in self.buffer.variable:
            return frame_error(
                image,
                f"{self.type_} Slam data is missing",
                y_offset=0,
                x_offset=400,
            )

        frame, mapp = self.buffer.variable["slam_data"][:2]
        if frame.id == 0:
            return image

        idx1, idx2, Rt = slam_toolbox.match_frame(
            mapp.frames[-1],
            mapp.frames[-2],
            self.m_samples,
            self.r_threshold,
            self.m_trials,
        )

        # Adding new data to the buffer
        self.buffer.variable["slam_data"].extend([idx1, idx2, Rt])

        if self.show_marker:
            for pt1 in mapp.frames[-1].key_pts[idx1]:
                cv2.circle(image, np.int32(pt1), self.marker_size, cc.yellow)

        return image

    def update(self, param):
        self.disabled = param["disabled"]
        self.m_samples = param["m_samples"]
        self.r_threshold = param["r_threshold"]
        self.m_trials = param["m_trials"]
        self.marker_size = param["marker_size"]
        self.show_marker = param["show_marker"]


class Triangulate(RootNode):
    """
    SLAM Triangulate Node
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orb_distance = self.param["orb_distance"]
        self.show_marker = self.param["show_marker"]

    def out_frame(self):
        # start_time = time.time()
        image = self.get_frame(0)
        if image is None:
            print("Triangulate stop")
            return None
        elif self.disabled:
            return image
        elif not "slam_data" in self.buffer.variable:
            return frame_error(
                image,
                f"{self.type_} Slam data is missing",
                y_offset=50,
                x_offset=400,
            )
        elif len(self.buffer.variable["slam_data"]) < 6:
            return image

        frame, mapp, K, W, H, idx1, idx2, Rt = self.buffer.variable["slam_data"]

        f1 = mapp.frames[-1]
        f2 = mapp.frames[-2]
        # add new observations if the point is already observed in the previous frame
        # TODO: consider tradeoff doing this before/after search by projection
        for i, idx in enumerate(idx2):
            if f2.pts[idx] is not None and f1.pts[idx1[i]] is None:
                f2.pts[idx].add_observation(f1, idx1[i])

        # get initial positions from fundamental matrix
        f1.pose = Rt @ f2.pose

        # pose optimization
        # pose_opt = mapp.optimize(local_window=1, fix_points=True)
        # sbp_pts_count = 0

        # search by projection
        if mapp.points:
            # project *all* the map points into the current frame
            map_points = np.array([p.homogeneous() for p in mapp.points])
            projs = (K @ f1.pose[:3] @ map_points.T).T
            projs = projs[:, 0:2] / projs[:, 2:]

            # only the points that fit in the frame
            good_pts = (
                (projs[:, 0] > 0)
                & (projs[:, 0] < W)
                & (projs[:, 1] > 0)
                & (projs[:, 1] < H)
            )

            for i, p in enumerate(mapp.points):
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
                        if b_dist < self.orb_distance:
                            p.add_observation(f1, m_idx)
                            # sbp_pts_count += 1
                            break

        # triangulate the points we don't have matches for
        good_pts4d = np.array([f1.pts[i] is None for i in idx1])

        # do triangulation in global frame
        pts4d = slam_toolbox.triangulate(f1.pose, f2.pose, f1.kps[idx1], f2.kps[idx2])
        good_pts4d &= np.abs(pts4d[:, 3]) != 0
        pts4d /= pts4d[:, 3:]  # homogeneous 3-D coords

        # adding new points to the map from pairwise matches
        # new_pts_count = 0
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
            pp1 = K @ pl1[:3]
            pp2 = K @ pl2[:3]

            # check reprojection error
            pp1 = (pp1[0:2] / pp1[2]) - f1.key_pts[idx1[i]]
            pp2 = (pp2[0:2] / pp2[2]) - f2.key_pts[idx2[i]]
            pp1 = np.sum(pp1**2)
            pp2 = np.sum(pp2**2)
            if pp1 > 2 or pp2 > 2:
                continue

            # color points from frame
            cx = np.int32(f1.key_pts[idx1[i], 0])
            cy = np.int32(f1.key_pts[idx1[i], 1])
            color = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)[cy, cx]

            pt = slam_toolbox.Point(mapp, p[0:3], color)

            pt.add_observation(f2, idx2[i])
            pt.add_observation(f1, idx1[i])
            # new_pts_count += 1

        # print("Adding:   %d new points, %d search by projection" % (new_pts_count, sbp_pts_count))
        # print("Map:      %d points, %d frames" % (len(self.mapp.points), len(self.mapp.frames)))
        # print("Time:     %.2f ms" % ((time.time()-start_time)*1000.0))
        # print(np.linalg.inv(f1.pose))
        if self.show_marker:
            for pt1, pt2 in zip(
                mapp.frames[-1].key_pts[idx1], mapp.frames[-2].key_pts[idx2]
            ):
                # cv2.circle(image, np.int32(pt1), 3, (0, 255, 255))
                cv2.drawMarker(image, np.int32(pt1), cc.red, 1, 5, 1, 8)
                cv2.line(image, np.int32(pt1), np.int32(pt2), cc.red, 1)

        return image

    def update(self, param):
        self.disabled = param["disabled"]
        self.orb_distance = param["orb_distance"]
        self.show_marker = param["show_marker"]


class Show2DMap(RootNode):
    """
    SLAM Open3DMap Node
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.amount = 500
        self.point_size = self.param["point_size"]
        self.point_color = self.param["point_color"]
        self.offsetx = self.param["offsetx"]
        self.offsety = self.param["offsety"]

    def out_frame(self):
        image = self.get_frame(0)
        if image is None:
            print("Show2DMap stop")
            return None
        elif self.disabled:
            return image
        elif "slam_data" in self.buffer.variable:
            mapp = self.buffer.variable["slam_data"][1]
            height, width = image.shape[:-1]
            clean_plate = np.zeros((height, width, 3), np.uint8)
            clean_plate[:] = (10, 10, 10)
            for idx, point in enumerate(mapp.points):
                cv2.circle(
                    clean_plate,
                    (
                        np.int32(point.pt[0] + self.offsetx),
                        np.int32(point.pt[2] + self.offsety),
                    ),
                    self.point_size,
                    (int(point.color[0]), int(point.color[1]), int(point.color[2])),
                    1,
                )

            cam_pts = np.linalg.inv(mapp.frames[-1].pose)[:, [-1]][:3].ravel()
            cv2.circle(
                clean_plate,
                (
                    np.int32(cam_pts[0] + self.offsetx),
                    np.int32(cam_pts[2] + self.offsety),
                ),
                5,
                (0, 0, 255),
                2,
            )

            return clean_plate
        return image

    def update(self, param):
        self.disabled = param["disabled"]
        self.point_size = param["point_size"]
        self.point_color = param["point_color"]
        self.offsetx = param["offsetx"]
        self.offsety = param["offsety"]


class Open3DMap(RootNode):
    """
    SLAM Open3DMap Node
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.amount = 500
        self.point_size = self.param["point_size"]
        self.point_color = self.param["point_color"]
        self.write_pcd = self.param["write_pcd"]
        self.d3d = slam_toolbox.DisplayOpen3D(
            width=int(self.param["window_size"][0]),
            height=int(self.param["window_size"][1]),
            scale=0.05,
            point_size=self.point_size,
            write_pcd=self.write_pcd,
            file=self.param["file"],
        )

    def out_frame(self):
        image = self.get_frame(0)
        if image is None:
            print("Open3DMap stop")
            return None
        elif self.disabled:
            return image
        elif "slam_data" in self.buffer.variable:
            self.d3d.send_to_visualization(
                self.buffer.variable["slam_data"][1], self.point_size
            )

        return image

    def update(self, param):
        self.disabled = param["disabled"]
        self.point_size = param["point_size"]
        self.point_color = param["point_color"]
        self.write_pcd = param["write_pcd"]
