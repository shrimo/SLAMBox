"""
Show camera and kitti path
"""
from multiprocessing import Process, Queue
import numpy as np
from scipy.spatial.transform import Rotation as scipyR  # type: ignore
import open3d as o3d  # type: ignore


class DisplayOpen3D:
    """This class is designed to visualize and write to a file
    the robot's position, key point cloud, and trajectory.
    """

    def __init__(
        self, width=1280, height=720, scale=0.5, point_size=2.0, write_pcd=False
    ):
        self.display_id = str(hex(id(self)))
        self.width = width
        self.height = height
        self.scale = scale
        self.point_size = point_size
        self.write_pcd = write_pcd
        # Rotation matrix for the scene
        self.rotation_matrix = scipyR.from_euler("zyx", [0, 0, 180], degrees=True)
        self.state = None
        self.queue = Queue()
        self.vp = Process(
            name="DisplayOpen3D", target=self.viewer_thread, args=(self.queue,)
        )
        self.vp.daemon = True
        self.vp.start()

    def viewer_thread(self, q):
        """Loop update point cloud and camera poses
        After the loop completes, destroy the window
        """
        self.viewer_init(self.width, self.height)
        while True:
            if self.viewer_refresh(q):
                break
        self.vis.destroy_window()

    def viewer_init(self, w, h):
        """Initializing the window, camera and their parameters"""
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(
            window_name="Open3D Map", width=w, height=h, left=100, top=200
        )

        self.ctr = self.vis.get_view_control()
        self.ctr.change_field_of_view(step=0.45)
        # self.ctr.camera_local_translate(0, 10, 0)
        self.ctr.set_constant_z_far(20000.0)
        self.ctr.set_constant_z_near(0.01)

        self.widget3d = self.vis.get_render_option()
        self.widget3d.show_coordinate_frame = True
        self.widget3d.background_color = np.asarray([0, 0, 0])
        self.widget3d.point_size = self.point_size

        self.pcl = o3d.geometry.PointCloud()
        self.pcl.points = o3d.utility.Vector3dVector(np.random.randn(100, 3))
        self.pcl.paint_uniform_color((0.5, 0.1, 0.1))

        self.pcl_kitti = o3d.geometry.PointCloud()
        self.pcl_kitti.points = o3d.utility.Vector3dVector(np.random.randn(100, 3))
        self.pcl_kitti.paint_uniform_color((0.0, 0.0, 0.5))

        self.axis = o3d.geometry.TriangleMesh.create_coordinate_frame()
        self.axis.scale(self.scale, center=self.axis.get_center())
        self.robot = o3d.geometry.TriangleMesh.create_coordinate_frame()
        self.robot.scale(self.scale, center=self.robot.get_center())
        # self.robot.compute_vertex_normals()
        # self.robot.paint_uniform_color((1.0, 0.0, 0.0))

        self.vis.add_geometry(self.pcl)
        self.vis.add_geometry(self.pcl_kitti)
        self.vis.add_geometry(self.axis)
        self.vis.add_geometry(self.robot)

    def viewer_refresh(self, q):
        """We receive point cloud data and robot positions
        from the queue and visualize them.
        We also write the point cloud to a file *.pcd.
        """
        while not q.empty():
            self.state = q.get()

        if self.state is not None:
            if self.state[0].shape[0] >= 1:
                # draw keypoints

                self.pcl.points = o3d.utility.Vector3dVector(
                    self.rotation_matrix.apply(self.state[0])
                )
                self.pcl.colors = o3d.utility.Vector3dVector(self.state[1])

                self.pcl_kitti.points = o3d.utility.Vector3dVector(
                    self.rotation_matrix.apply(self.state[2])
                )
                self.pcl_kitti.colors = o3d.utility.Vector3dVector(self.state[3])

                self.robot.translate(
                    self.rotation_matrix.apply(self.state[0][-1]), relative=False
                )

            if self.write_pcd:
                # write the point cloud to a file
                o3d.io.write_point_cloud(
                    f"./pcd/slam_map_{self.state[3]:04}.pcd", self.pcl
                )

        self.vis.update_geometry(self.pcl)
        self.vis.update_geometry(self.pcl_kitti)
        self.vis.update_geometry(self.robot)
        self.vis.update_renderer()
        # If closing vis window
        if not self.vis.poll_events():
            return True

    def send_to_visualization(self, track, kitti, color, kitti_color):
        """Sending data to the visualization process
        Combine two arrays: an camera trajectory points and kitti points,
        color of camera points is red, kiiti is green"""
        if self.queue is None:
            return
        self.queue.put((track, color, kitti, kitti_color))

    def __del__(self):
        """When closing an object, display its ID"""
        print(f"Close {self.display_id} DisplayOpen3D")
