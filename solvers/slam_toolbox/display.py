"""
Show 3D map and camera path
"""

from multiprocessing import Process, Queue
import pangolin  # type: ignore
import OpenGL.GL as gl  # type: ignore
import numpy as np


def draw_axis(size):
    gl.glColor3f(1.0, 0.0, 0.0)
    pangolin.DrawLine([[0.0, 0.0, 0.0], [size, 0.0, 0.0]])
    gl.glColor3f(0.0, 1.0, 0.0)
    pangolin.DrawLine([[0.0, 0.0, 0.0], [0.0, -size, 0]])
    gl.glColor3f(0.0, 0.0, 1.0)
    pangolin.DrawLine([[0.0, 0.0, 0.0], [0.0, 0.0, size]])

def draw_grid(col):
    gl.glColor3f(0.7, 0.7, 0.7)
    for line in np.arange(col+1):
        pangolin.DrawLine([[line, 0.0, 0.0], [line, 0.0, col]])
        pangolin.DrawLine([[0.0, 0.0, line], [col, 0.0, line]])

def draw_trajectory(points, psize, color):
    gl.glLineWidth(psize)
    gl.glColor3f(*color)
    pangolin.DrawLine(points)

class Display3D:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        self.state = None
        self.q = Queue()
        self.vp = Process(target=self.viewer_thread, args=(self.q,))
        self.vp.daemon = True
        self.vp.start()

    def viewer_thread(self, q):
        self.viewer_init(self.width, self.height)
        while True:
            self.viewer_refresh(q)

    def viewer_init(self, w, h):
        pangolin.CreateWindowAndBind('Map Viewer', w, h)
        gl.glEnable(gl.GL_DEPTH_TEST)

        self.scam = pangolin.OpenGlRenderState(
            pangolin.ProjectionMatrix(w, h, 420, 420, w//2, h//2, 0.2, 30000),
            pangolin.ModelViewLookAt(0, -10, -8,
                                                             0, 0, 0,
                                                             0, -1, 0))
        self.handler = pangolin.Handler3D(self.scam)

        # Create Interactive View in window
        self.dcam = pangolin.CreateDisplay()
        self.dcam.SetBounds(0.0, 1.0, 0.0, 1.0, w/h)
        self.dcam.SetHandler(self.handler)
        # hack to avoid small Pangolin, no idea why it's *2
        self.dcam.Resize(pangolin.Viewport(0,0,w*2,h*2))
        self.dcam.Activate()

        # Create panel
        self.panel = pangolin.CreatePanel('ui')
        self.panel.SetBounds(0.0, 0.2, 0.0, 100/640.)
        self.psize = pangolin.VarFloat('ui.Point_size', value=2, min=0.5, max=5)
        self.gain = pangolin.VarFloat('ui.Gain', value=1.0, min=0, max=3)
        self.background = pangolin.VarFloat('ui.Background', value=0.0, min=0, max=1)
        self.alpha = pangolin.VarFloat('ui.Alpha', value=1.0, min=0, max=1)
        self.screenshot = pangolin.VarBool('ui.Screenshot', value=False, toggle=False)
        # self.sequence = pangolin.VarBool('ui.Sequence', value=False, toggle=True)

    def viewer_refresh(self, q):
        while not q.empty():
            self.state = q.get()

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glClearColor(self.background, self.background, self.background, self.alpha)
        self.dcam.Activate(self.scam)

        if pangolin.Pushed(self.screenshot):
            pangolin.SaveWindowOnRender('screenshot_'+str(len(self.state[1])))

        draw_axis(3.0)
        draw_grid(5.0)

        if self.state is not None:
            # if self.state[0].shape[0] >= 2:
            #     # draw poses
            #     gl.glColor3f(0.0, 0.3, 0.7)
            #     pangolin.DrawCameras(self.state[0][:-1])

            if self.state[0].shape[0] >= 1:
                # draw current pose as yellow
                gl.glColor3f(1.0, 1.0, 0.0)
                pangolin.DrawCameras(self.state[0])

            if self.state[1].shape[0] != 0:
                # draw keypoints
                points_color = self.state[2]*np.single(self.gain)
                gl.glPointSize(self.psize)
                gl.glColor3f(1.0, 0.0, 0.0)
                pangolin.DrawPoints(self.state[1], points_color)

            draw_trajectory(self.state[3], 1, (1.0, 0.0, 0.0))
        pangolin.FinishFrame()

    def paint(self, mapp):
        if self.q is None:
            return
        pts, colors, cam_pts = [], [], []
        poses = mapp.frames[-1].pose # np.linalg.inv(mapp.frames[-1].pose)
        for f in mapp.frames:
            # invert pose for display only
            f_pose = f.pose # np.linalg.inv(f.pose)
            # get position from transform matrix
            cam_position = f_pose[:,[-1]][:3].ravel()
            cam_pts.append(cam_position)
        for p in mapp.points:
            pts.append(p.pt)
            colors.append(p.color)
        self.q.put((np.array([poses]), np.array(pts), np.array(colors)/256.0, np.array(cam_pts)))

