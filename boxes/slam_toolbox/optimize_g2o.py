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
    Perform bundle adjustment optimization using g2o.
    
    Args:
        frames: List of all frames
        points: List of all 3D points
        local_window: Number of recent frames to optimize (None = all)
        fix_points: Keep 3D points fixed during optimization
        verbose: Enable verbose output
        rounds: Number of optimization iterations
        solverSE3: Linear solver type
        bridge_edges: List of bridge constraints from sliding window
    
    Returns:
        float: Final chi2 error
    """
    
    # Select frames for optimization
    if local_window is None:
        local_frames = frames
    else:
        local_frames = frames[-local_window:]

    # Create optimizer
    optimizer = g2o.SparseOptimizer()
    solver = g2o.BlockSolverSE3(SolverSE3[solverSE3]())
    solver = g2o.OptimizationAlgorithmLevenberg(solver)
    optimizer.set_algorithm(solver)

    # Camera parameters
    cam = g2o.CameraParameters(1.0, (0.0, 0.0), 0)
    cam.set_id(0)
    optimizer.add_parameter(cam)

    robust_kernel = g2o.RobustKernelHuber(np.sqrt(5.991))
    graph_frames, graph_points = {}, {}

    # Add frames to graph
    for f in local_frames if fix_points else frames:
        pose = f.pose
        se3 = g2o.SE3Quat(pose[0:3, 0:3], pose[0:3, 3])
        v_se3 = g2o.VertexSE3Expmap()
        v_se3.set_estimate(se3)
        v_se3.set_id(f.id * 2)
        v_se3.set_fixed(f.id <= 1 or f not in local_frames)
        optimizer.add_vertex(v_se3)
        graph_frames[f.id] = v_se3

    # Add 3D points
    for p in points:
        if not any([f in local_frames for f in p.frames]):
            continue
        pt = g2o.VertexPointXYZ()
        pt.set_id(p.id * 2 + 1)
        pt.set_estimate(p.pt[0:3])
        pt.set_marginalized(True)
        pt.set_fixed(fix_points)
        optimizer.add_vertex(pt)
        graph_points[p] = pt

        # Add reprojection edges
        for f, idx in zip(p.frames, p.idxs):
            if f.id not in graph_frames:
                continue
            edge = g2o.EdgeProjectXYZ2UV()
            edge.set_parameter_id(0, 0)
            edge.set_vertex(0, pt)
            edge.set_vertex(1, graph_frames[f.id])
            edge.set_measurement(f.kps[idx])
            edge.set_information(np.eye(2))
            edge.set_robust_kernel(robust_kernel)
            optimizer.add_edge(edge)

    # Add bridge edges from sliding window (if enabled)
    if bridge_edges:
        print(f"[Optimizer] Adding {len(bridge_edges)} bridge constraints")
        for bridge in bridge_edges:
            from_id = bridge["from_id"]
            to_id = bridge["to_id"]
            if from_id in graph_frames and to_id in graph_frames:
                add_bridge_edge(optimizer, from_id, to_id, 
                              bridge["rel_pose"], bridge["info"])
                print(f"[Optimizer] Added bridge {from_id}→{to_id}")
            else:
                print(f"[Optimizer] Warning: Bridge {from_id}→{to_id} endpoints not in graph")

    # Run optimization
    if verbose:
        optimizer.set_verbose(True)
    
    optimizer.initialize_optimization()
    optimizer.optimize(rounds)

    # Get final error
    final_error = optimizer.active_chi2()

    # Update frame poses
    for f in graph_frames:
        est = graph_frames[f].estimate()
        R = est.rotation().matrix()
        t = est.translation()
        for fr in frames:
            if fr.id == f:
                fr.pose = poseRt(R, t)
                break

    # Update point positions
    if not fix_points:
        for p in graph_points:
            p.pt = np.array(graph_points[p].estimate())

    return final_error
