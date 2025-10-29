"""
Optimized DisplayOpen3D — compact and faster visualization of SLAM map and trajectory.
"""
import numpy as np
import open3d as o3d
from multiprocessing import Process, Queue
from scipy.spatial.transform import Rotation as R


class DisplayOpen3D:
    """Visualizes point clouds, camera poses, and trajectory using Open3D."""

    def __init__(self, width=1280, height=720, scale=0.05, point_size=2.0,
                 write_pcd=False, file="./data/pcd/slam_map_"):
        # Initialize visualization parameters
        self.width, self.height = width, height
        self.scale, self.point_size = scale, point_size
        self.write_pcd, self.file = write_pcd, file

        # Precompute rotation matrices
        self.rotation = R.from_euler("zyx", [0, 0, 180], degrees=True)
        self.rotation_np = self.rotation.as_matrix()
        self.flip_x = np.diag([1, -1, -1])
        self.align_frustum = np.array([[0, 1, 0], [0, 0, -1], [1, 0, 0]], dtype=float)
        self.color_scale = 0.003
        self.queue, self.state = Queue(), None

        # Start visualization process
        self.proc = Process(target=self.viewer_thread, args=(self.queue,), daemon=True)
        self.proc.start()

    def viewer_thread(self, q):
        """Runs the visualization loop in a separate process."""
        # Create Open3D visualization window
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window("Open3D Map", self.width, self.height, 100, 200)

        # Configure render options
        opt = self.vis.get_render_option()
        opt.show_coordinate_frame = True
        opt.background_color = [0.0] * 3
        opt.point_size = self.point_size
        opt.mesh_show_back_face = True
        # opt.mesh_show_wireframe = True
        # opt.light_on = False

        # Initialize point cloud with one dummy point
        self.pcl = o3d.geometry.PointCloud()
        self.pcl.points = o3d.utility.Vector3dVector(np.array([[0, 0, 0]], dtype=np.float64))
        self.pcl.colors = o3d.utility.Vector3dVector(np.array([[0.5, 0.5, 0.5]], dtype=np.float64))

        # Create world coordinate axis
        self.axis = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.5)

        # Create camera frustum representing the robot
        self.robot = self._create_camera_frustum(0.3)

        # Initialize trajectory with one small dummy line
        self.trajectory = o3d.geometry.LineSet()
        dummy_points = np.array([[0, 0, 0], [0.01, 0, 0]], dtype=np.float64)
        self.trajectory.points = o3d.utility.Vector3dVector(dummy_points)
        self.trajectory.lines = o3d.utility.Vector2iVector([[0, 1]])
        self.trajectory.colors = o3d.utility.Vector3dVector([[1.0, 0.7, 0.0]])

        # Add all geometries to the scene
        for g in [self.pcl, self.axis, self.robot, self.trajectory]:
            self.vis.add_geometry(g)

        # Configure view control and camera parameters
        self.prev_tf = np.eye(4)
        self.ctr = self.vis.get_view_control()
        self.ctr.set_constant_z_far(5000)
        self.ctr.set_constant_z_near(0.01)
        self.vis.reset_view_point(True)
        self.ctr.set_zoom(2.5)

        # Run visualization update loop
        while self.vis.poll_events():
            self._refresh(q)
            self.vis.update_renderer()

        # Cleanly destroy the window on exit
        self.vis.destroy_window()

    def _create_camera_frustum(self, size):
        """Creates a colored 3D frustum to represent the camera."""
        # Define frustum dimensions
        w, h, d = size * 0.6, size * 0.4, size
        # Define vertices and faces
        v = np.array([[0, 0, 0], [d, -w, -h], [d, w, -h], [d, w, h], [d, -w, h]])
        f = np.array([[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 1], [1, 3, 2], [1, 4, 3]])
        # Create mesh and set colors
        mesh = o3d.geometry.TriangleMesh(
            o3d.utility.Vector3dVector(v),
            o3d.utility.Vector3iVector(f)
        )
        c = np.tile([[0.3, 0.7, 1.0]], (5, 1))
        c[0] = [0.2, 0.6, 1.0]
        mesh.vertex_colors = o3d.utility.Vector3dVector(c)
        mesh.compute_vertex_normals()
        return mesh

    def _refresh(self, q):
        """Updates the Open3D visualization with the latest data."""
        # Get latest queued state
        while not q.empty():
            self.state = q.get()
        if self.state is None:
            return

        # Unpack current visualization state
        pts, cols, psize, nframes, pose = self.state
        self.vis.get_render_option().point_size = psize

        # Update point cloud
        if len(pts):
            self.pcl.points = o3d.utility.Vector3dVector(self.rotation.apply(pts))
            self.pcl.colors = o3d.utility.Vector3dVector(cols)

        # Update camera trajectory
        if nframes > 1:
            cams = self.rotation.apply(pts[-nframes:])
            lines = np.column_stack([np.arange(len(cams) - 1), np.arange(1, len(cams))])
            self.trajectory.points = o3d.utility.Vector3dVector(cams)
            self.trajectory.lines = o3d.utility.Vector2iVector(lines)
            self.trajectory.colors = o3d.utility.Vector3dVector([[1.0, 0.7, 0.0]] * len(lines))

        # Update camera (robot) pose
        if pose is not None:
            pos = self.rotation.apply(pose[:3, 3] * self.scale)
            rot = self.rotation_np @ pose[:3, :3] @ self.align_frustum @ self.flip_x
            tf = np.eye(4)
            tf[:3, :3], tf[:3, 3] = rot, pos
            self.robot.transform(np.linalg.inv(self.prev_tf))
            self.robot.transform(tf)
            self.prev_tf = tf

        # Optionally save PCD file
        if self.write_pcd:
            o3d.io.write_point_cloud(f"{self.file}{nframes:04}.pcd", self.pcl)

        # Update all geometries
        for g in [self.pcl, self.robot, self.trajectory]:
            self.vis.update_geometry(g)

    def send_to_visualization(self, mapp, psize):
        """Sends map and frame data to the visualization process."""
        if not self.queue:
            return

        # Extract points and colors
        pts = np.array([p.pt for p in mapp.points]) * self.scale if mapp.points else np.empty((0, 3))
        cols = np.array([p.color for p in mapp.points]) * self.color_scale if mapp.points else np.empty((0, 3))
        poses = np.array([f.pose for f in mapp.frames]) if mapp.frames else np.empty((0, 4, 4))

        # Compute camera positions
        if poses.size:
            R, t = poses[:, :3, :3], poses[:, :3, 3]
            cam_pts = -np.einsum('nij,nj->ni', np.transpose(R, (0, 2, 1)), t) * self.scale
        else:
            cam_pts = np.empty((0, 3))

        # Combine points and trajectory
        all_pts = np.vstack([pts, cam_pts]) if pts.size else cam_pts
        cam_colors = np.full((len(mapp.frames), 3), [1.0, 0.0, 0.0])
        all_cols = np.vstack([cols, cam_colors]) if pts.size else cam_colors

        # Get last pose for robot
        pose = np.linalg.inv(mapp.frames[-1].pose) if mapp.frames else None
        self.queue.put((all_pts, all_cols, psize, len(mapp.frames), pose))

    def __del__(self):
        """Cleans up resources on object deletion."""
        print("Closed DisplayOpen3D instance.")
