"""
Show 3D map and camera path
"""

from multiprocessing import Process, Queue
import numpy as np
from scipy.spatial.transform import Rotation as scipyR # type: ignore
import open3d as o3d # type: ignore

class DisplayOpen3D:
    def __init__(self, width=1280, height=720, scale=0.05, point_size=2.0):
        self.amount = 100
        self.width = width
        self.height = height
        self.scale = scale
        self.point_size = point_size
        self.state = None
        self.queue = Queue()
        self.vp = Process(target=self.viewer_thread, args=(self.queue,))
        self.vp.daemon = True
        self.vp.start()

    def viewer_thread(self, q):
        self.viewer_init(self.width, self.height)
        while True:
            self.viewer_refresh(q)

    def viewer_init(self, w, h):
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(window_name='Open3D Map',
            width = w, height = h, left=100, top=200)

        self.ctr = self.vis.get_view_control()
        self.ctr.change_field_of_view(step=0.45)
        self.ctr.set_constant_z_far(100.0)
        self.ctr.set_constant_z_near(0.01)

        self.widget3d = self.vis.get_render_option()
        self.widget3d.show_coordinate_frame = True
        self.widget3d.background_color = np.asarray([0, 0, 0])
        self.widget3d.point_size = self.point_size

        self.pcl = o3d.geometry.PointCloud()
        self.pcl.points = o3d.utility.Vector3dVector(np.random.randn(self.amount, 3))
        self.pcl.paint_uniform_color((0.5, 0.1, 0.1))

        # self.cube = o3d.geometry.TriangleMesh.create_box(0.2, 0.2, 0.2)
        # self.cube.compute_vertex_normals()
        # self.cube.paint_uniform_color((1.0, 0.0, 0.0))

        self.vis.add_geometry(self.pcl)

    def viewer_refresh(self, q):
        while not q.empty():
            self.state = q.get()

        if self.state is not None:
            if self.state[0].shape[0] >= 1:
                # draw keypoints
                self.widget3d.point_size = self.state[2]
                rotation_matrix = scipyR.from_euler('zyx', [0, 0, 180], degrees=True)
                self.pcl.points = o3d.utility.Vector3dVector(rotation_matrix.apply(self.state[0]))
                self.pcl.colors = o3d.utility.Vector3dVector(self.state[1])

        self.vis.update_geometry(self.pcl)
        self.vis.poll_events()
        self.vis.update_renderer()

    def send_to_visualization(self, mapp, psize):
        if self.queue is None:
            return
        pts = [p.pt*self.scale for p in mapp.points]
        colors = [p.color*0.003 for p in mapp.points] # 0.003 - coefficient for converting 0:255 to 0:1
        self.queue.put((np.array(pts), np.array(colors), psize))

    def __del__(self):
        self.vis.destroy_window()

