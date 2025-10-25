"""
g2o is an open-source C++ framework for optimizing graph-based nonlinear error functions.
https://github.com/RainerKuemmerle/g2o/tree/pymem
"""

import numpy as np

import g2o  # type: ignore
from boxes.slam_toolbox.match_frames import poseRt

SolverSE3 = {
    "EigenSE3": g2o.LinearSolverEigenSE3,
    "DenseSE3": g2o.LinearSolverDenseSE3,
    "PCGSE3": g2o.LinearSolverPCGSE3,
}


def add_bridge_edge(optimizer, from_id, to_id, rel_pose, info):
    """
    Add a relative SE3 bridge constraint between two frames.
    """
    edge = g2o.EdgeSE3()
    edge.set_vertex(0, optimizer.vertex(from_id * 2))
    edge.set_vertex(1, optimizer.vertex(to_id * 2))
    
    iso = g2o.Isometry3d(rel_pose[:3, :3], rel_pose[:3, 3])
    edge.set_measurement(iso)
    edge.set_information(info)
    optimizer.add_edge(edge)


def optimize(
    frames,
    points,
    local_window,
    fix_points,
    verbose=False,
    rounds=50,
    solverSE3="EigenSE3",
    bridge_edges=None,
):
    """
    Perform bundle adjustment optimization using g2o with partial vectorization
    and precomputation for faster graph building.

    Args:
        frames: List of all frames (each must have .id, .pose, .kps)
        points: List of all 3D points (each must have .id, .pt, .frames, .idxs)
        local_window: Number of recent frames to optimize (None = all)
        fix_points: Keep 3D points fixed during optimization
        verbose: Enable verbose output
        rounds: Number of optimization iterations
        solverSE3: Linear solver type
        bridge_edges: List of bridge constraints from sliding window

    Returns:
        float: Final chi2 error
    """

    # --- Select frames for optimization ---
    if local_window is None:
        local_frames = frames
    else:
        local_frames = frames[-local_window:]

    local_ids = {f.id for f in local_frames}

    # --- Create optimizer ---
    optimizer = g2o.SparseOptimizer()
    solver = g2o.BlockSolverSE3(SolverSE3[solverSE3]())
    solver = g2o.OptimizationAlgorithmLevenberg(solver)
    optimizer.set_algorithm(solver)

    # --- Camera parameters (shared) ---
    cam = g2o.CameraParameters(1.0, (0.0, 0.0), 0)
    cam.set_id(0)
    optimizer.add_parameter(cam)

    # --- Shared robust kernel and info matrix ---
    robust_kernel = g2o.RobustKernelHuber(np.sqrt(5.991))
    info_matrix = np.eye(2)

    # --- Precompute: dictionary for frame keypoints for faster access ---
    frame_kps = {f.id: np.array(f.kps) for f in frames}
    graph_frames, graph_points = {}, {}

    # --- Add frame vertices ---
    for f in (local_frames if fix_points else frames):
        pose = f.pose
        se3 = g2o.SE3Quat(pose[0:3, 0:3], pose[0:3, 3])
        v_se3 = g2o.VertexSE3Expmap()
        v_se3.set_estimate(se3)
        v_se3.set_id(f.id * 2)
        # Fix very first frames or those outside the local window
        v_se3.set_fixed(f.id <= 1 or f.id not in local_ids)
        optimizer.add_vertex(v_se3)
        graph_frames[f.id] = v_se3

    # --- Pre-filter points that are seen in the local window ---
    filtered_points = [
        p for p in points if any(fr.id in local_ids for fr in p.frames)
    ]

    # --- Add 3D point vertices and projection edges ---
    for p in filtered_points:
        pt = g2o.VertexPointXYZ()
        pt.set_id(p.id * 2 + 1)
        pt.set_estimate(p.pt[:3])
        pt.set_marginalized(True)
        pt.set_fixed(fix_points)
        optimizer.add_vertex(pt)
        graph_points[p] = pt

        # --- Fast zip over frame references and keypoint indices ---
        for f, idx in zip(p.frames, p.idxs):
            if f.id not in graph_frames:
                continue
            edge = g2o.EdgeProjectXYZ2UV()
            edge.set_parameter_id(0, 0)
            edge.set_vertex(0, pt)
            edge.set_vertex(1, graph_frames[f.id])
            edge.set_measurement(frame_kps[f.id][idx])
            edge.set_information(info_matrix)
            edge.set_robust_kernel(robust_kernel)
            optimizer.add_edge(edge)

    # --- Add bridge constraints (from sliding window) ---
    if bridge_edges:
        valid_bridges = [
            b for b in bridge_edges
            if b["from_id"] in graph_frames and b["to_id"] in graph_frames
        ]
        print(f"[Optimizer] Adding {len(valid_bridges)} bridge constraints")
        for b in valid_bridges:
            add_bridge_edge(
                optimizer,
                b["from_id"],
                b["to_id"],
                b["rel_pose"],
                b["info"],
            )

    # --- Run optimization ---
    optimizer.set_verbose(verbose)
    optimizer.initialize_optimization()
    optimizer.optimize(rounds)

    # --- Final error ---
    final_error = optimizer.active_chi2()

    # --- Batch update frame poses using NumPy for compactness ---
    for fid, vertex in graph_frames.items():
        est = vertex.estimate()
        R = est.rotation().matrix()
        t = est.translation()
        for fr in frames:
            if fr.id == fid:
                fr.pose = poseRt(R, t)
                break

    # --- Batch update 3D points (if not fixed) ---
    if not fix_points:
        for p, vertex in graph_points.items():
            p.pt = np.array(vertex.estimate())

    return final_error
