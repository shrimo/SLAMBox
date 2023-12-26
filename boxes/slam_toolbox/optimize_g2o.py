"""
g2o is an open-source C++ framework for optimizing graph-based nonlinear error functions.
https://github.com/RainerKuemmerle/g2o/tree/pymem
"""

import os
import sys
import numpy as np

# from config import g2opy_path
# if g2opy_path not in sys.path:
#     sys.path.append(g2opy_path)

# # Checking for the presence of the framework and required methods
# try:
#     import g2opy as g2o  # type: ignore
# except ModuleNotFoundError as er:
#     print(f"{er}: Framework g2opy not available")
#     try:
#         import g2o  # type: ignore
#     except ModuleNotFoundError as er:
#         print(f"{er}: Framework g2o not available")
# finally:
#     if getattr(g2o, "__name__", None):
#         if getattr(g2o, "LinearSolverCSparseSE3", None):
#             # Pymem version https://github.com/RainerKuemmerle/g2o/tree/pymem
#             SolverSE3 = {
#                 "CSparseSE3": g2o.LinearSolverCSparseSE3,
#                 "EigenSE3": g2o.LinearSolverEigenSE3,
#                 "CholmodSE3": g2o.LinearSolverCholmodSE3,
#                 "DenseSE3": g2o.LinearSolverDenseSE3,
#             }
#         else:
#             # g2o version by https://github.com/miquelmassot/g2o-python
#             SolverSE3 = {
#                 "EigenSE3": g2o.LinearSolverEigenSE3,
#                 "DenseSE3": g2o.LinearSolverDenseSE3,
#             }

import g2o  # type: ignore
SolverSE3 = {
                "EigenSE3": g2o.LinearSolverEigenSE3,
                "DenseSE3": g2o.LinearSolverDenseSE3,
            }

from boxes.slam_toolbox.match_frames import poseRt


def optimize(
    frames,
    points,
    local_window,
    fix_points,
    verbose=False,
    rounds=50,
    solverSE3="SolverEigenSE3",
):
    if local_window is None:
        local_frames = frames
    else:
        local_frames = frames[-local_window:]

    # create g2o optimizer
    opt = g2o.SparseOptimizer()
    # solver = g2o.BlockSolverSE3(g2o.LinearSolverCSparseSE3())
    solver = g2o.BlockSolverSE3(SolverSE3[solverSE3]())
    solver = g2o.OptimizationAlgorithmLevenberg(solver)
    opt.set_algorithm(solver)

    # add normalized camera
    cam = g2o.CameraParameters(1.0, (0.0, 0.0), 0)
    cam.set_id(0)
    opt.add_parameter(cam)

    robust_kernel = g2o.RobustKernelHuber(np.sqrt(5.991))
    graph_frames, graph_points = {}, {}

    # add frames to graph
    for f in local_frames if fix_points else frames:
        pose = f.pose
        se3 = g2o.SE3Quat(pose[0:3, 0:3], pose[0:3, 3])
        v_se3 = g2o.VertexSE3Expmap()
        v_se3.set_estimate(se3)

        v_se3.set_id(f.id * 2)
        v_se3.set_fixed(f.id <= 1 or f not in local_frames)
        # v_se3.set_fixed(f.id != 0)
        opt.add_vertex(v_se3)

        # confirm pose correctness
        est = v_se3.estimate()
        assert np.allclose(pose[0:3, 0:3], est.rotation().matrix())
        assert np.allclose(pose[0:3, 3], est.translation())

        graph_frames[f] = v_se3

    # add points to frames
    for p in points:
        if not any([f in local_frames for f in p.frames]):
            continue

        # pt = g2o.VertexSBAPointXYZ()
        pt = g2o.VertexPointXYZ()
        pt.set_id(p.id * 2 + 1)
        pt.set_estimate(p.pt[0:3])
        pt.set_marginalized(True)
        pt.set_fixed(fix_points)
        opt.add_vertex(pt)
        graph_points[p] = pt

        # add edges
        for f, idx in zip(p.frames, p.idxs):
            if f not in graph_frames:
                continue
            edge = g2o.EdgeProjectXYZ2UV()
            edge.set_parameter_id(0, 0)
            edge.set_vertex(0, pt)
            edge.set_vertex(1, graph_frames[f])
            edge.set_measurement(f.kps[idx])
            edge.set_information(np.eye(2))
            edge.set_robust_kernel(robust_kernel)
            opt.add_edge(edge)

    if verbose:
        opt.set_verbose(True)
    opt.initialize_optimization()
    opt.optimize(rounds)

    # put frames back
    for f in graph_frames:
        est = graph_frames[f].estimate()
        R = est.rotation().matrix()
        t = est.translation()
        f.pose = poseRt(R, t)

    # put points back
    if not fix_points:
        for p in graph_points:
            p.pt = np.array(graph_points[p].estimate())

    return opt.active_chi2()
