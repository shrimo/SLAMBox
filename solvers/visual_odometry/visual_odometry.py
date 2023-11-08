#!/usr/bin/python3.10

import cv2
import numpy as np

from kitti_reader import DatasetReaderKITTI
from feature_tracking import FeatureTracker
from utils import drawFrameFeatures
from display_open3d import DisplayOpen3D

if __name__ == "__main__":
    tracker = FeatureTracker()
    detector = cv2.GFTTDetector_create()
    dataset_reader = DatasetReaderKITTI("/home/cds/github/video/09/")

    scale = 0.05
    K = dataset_reader.readCameraMatrix()
    # print(K)

    prev_points = np.empty(0)
    prev_frame_BGR = dataset_reader.readFrame(0)
    kitti_positions, track_positions = [], []
    camera_rot, camera_pos = np.eye(3), np.zeros((3, 1))
    cv2.namedWindow("2D Viewer", cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow("2D Viewer", 100, 100)

    d3d = DisplayOpen3D(
        width=int(prev_frame_BGR.shape[1]),
        height=int(prev_frame_BGR.shape[0]),
        scale=0.5,
        point_size=2.0,
        write_pcd=False,
    )

    # Process next frames
    for frame_no in range(1, dataset_reader.getFramesCount()):
        curr_frame_BGR = dataset_reader.readFrame(frame_no)
        prev_frame = cv2.cvtColor(prev_frame_BGR, cv2.COLOR_BGR2GRAY)
        curr_frame = cv2.cvtColor(curr_frame_BGR, cv2.COLOR_BGR2GRAY)

        # Feature detection & filtering
        prev_points = detector.detect(prev_frame)
        prev_points = cv2.KeyPoint_convert(
            sorted(prev_points, key=lambda p: p.response, reverse=True)
        )

        # Feature tracking (optical flow)
        prev_points, curr_points = tracker.trackFeatures(
            prev_frame, curr_frame, prev_points, removeOutliers=True
        )
        # print (f"{len(curr_points)} features left after feature tracking.")

        # Essential matrix, pose estimation
        E, mask = cv2.findEssentialMat(
            curr_points, prev_points, K, cv2.RANSAC, 0.99, 1.0, None
        )
        prev_points = np.array(
            [pt for (idx, pt) in enumerate(prev_points) if mask[idx] == 1]
        )
        curr_points = np.array(
            [pt for (idx, pt) in enumerate(curr_points) if mask[idx] == 1]
        )
        _, R, T, _ = cv2.recoverPose(E, curr_points, prev_points, K)
        # print(f"{len(curr_points)} features left after pose estimation.")

        # Read groundtruth translation T and absolute scale for computing trajectory
        kitti_pos, kitti_scale = dataset_reader.readGroundtuthPosition(frame_no)
        if kitti_scale <= 0.1:
            continue

        camera_pos = camera_pos + kitti_scale * camera_rot.dot(T)
        camera_rot = R.dot(camera_rot)

        track_positions.append(
            np.array([camera_pos[0][0], 0.0, camera_pos[2][0]]) * scale
        )
        kitti_positions.append(
            np.array([kitti_pos[0], 0.0, kitti_pos[2]]) * scale
        )
        cam_colors = [(1.0, 0.0, 0.0)] * len(track_positions)
        kitti_colors = [(0.0, 1.0, 0.0)] * len(kitti_positions)

        drawFrameFeatures(curr_frame, prev_points, curr_points, frame_no)
        d3d.send_to_visualization(
            np.array(track_positions),
            np.array(kitti_positions),
            cam_colors,
            kitti_colors,
        )

        p_key = cv2.waitKey(1)
        if p_key == ord("q"):
            break
        elif p_key == ord("p"):
            cv2.waitKey(-1)

        prev_points, prev_frame_BGR = curr_points, curr_frame_BGR

    cv2.destroyAllWindows()
