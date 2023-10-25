from multiprocessing import Process, Queue
import numpy as np
from skimage.measure import LineModelND, ransac # type: ignore
import OpenGL.GL as gl # type: ignore
import pangolin # type: ignore
from .kalman import Kalman3D
import g2o # type: ignore
from .optimize_g2o import optimize # type: ignore
from .helpers import poseRt, hamming_distance, add_ones

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

def draw_keypoints(points, psize, color):
    gl.glPointSize(psize)
    gl.glColor3f(*color)
    pangolin.DrawPoints(points)

def draw_keypoints_color(points, psize, color):
    gl.glPointSize(psize)
    pangolin.DrawPoints(points, color)

def draw_trajectory(points, psize, color):
    gl.glLineWidth(psize)
    gl.glColor3f(*color)
    pangolin.DrawLine(points)

def draw_all_poses(all_pose, all_color, current_pose, current_color):
    # Draw all pose
    gl.glColor3f(*all_color)
    pangolin.DrawCameras(all_pose, 0.75, 0.75, 0.75)
    # Draw current pose
    gl.glColor3f(*current_color)
    pangolin.DrawCameras(current_pose, 1.5, 0.75, 1.0)

def draw_single_poses(current_pose, current_color):
    ''' Draw current pose '''
    gl.glColor3f(*current_color)
    pangolin.DrawCameras(current_pose, 1.5, 0.75, 1.0)


class Point:
    """ Point is a 3D point in the world 
    Each Point is observed in multiple Frames """
    def __init__(self, mapp, loc):
        self.pt = loc
        self.frames = []
        self.idxs = []
        self.color = None
        self.id = len(mapp.points)
        mapp.points.append(self)

    def homogeneous(self):
        return add_ones(self.pt)

    def add_observation(self, frame, idx):
        frame.pts[idx] = self
        self.frames.append(frame)
        self.idxs.append(idx)

    def add_color(self, color):
        self.color = np.single(color) / 255.

    def delete(self):
        for f, idx in zip(self.frames, self.idxs):
          f.pts[idx] = None
        del self


class Descriptor:
    """ Storage, optimization, filtering, processing and 
    visualization of data by point cloud and camera pose """
    def __init__(self, width = 1280, height = 720, fps = 30.):
        self.width, self.height = width, height
        self.frames = []
        self.points = []
        self.state = None
        self.q3D = None # 3D data queue
        self.tr = []
        self.mvla = (0, -20, -20, 0, 0, 0, 0, -1, 0)
        self.pmx = (width, height, 420, 420,
                    width//2, height//2, 0.2, 10000)

        self.mod_opt = None
        self.KF = Kalman3D(drag=0.8, debug=0)
        self.KF.init(np.float32([0.0, 0.0, 0.0]))
        self.fps = 1/fps
        self.max_frame = 0

    def LineModelOptimization(self, m_samples=8, r_threshold=10, m_trials=100):
        """ Robust line model estimation using RANSAC """        
        points = np.array([(kp.pt[0], kp.pt[1]) for kp in self.points])
        model_robust, inliers = ransac(points, LineModelND, min_samples=m_samples,
                                       residual_threshold=r_threshold, 
                                       max_trials=m_trials)
        outliers = inliers == False
        self.mod_opt = (inliers, outliers)
        for out_lie, ptx in zip(outliers, self.points):
            if out_lie:
                self.points.remove(ptx) # remove outliers points
                # ptx.color = [1.0, 0.0, 0.0] # the point red color

    def KalmanFilterOptimization(self):
        """The Kalman filter keeps track of the estimated state 
        of the system and the variance or uncertainty of the estimate. """
        current_pose = self.frames[-1].pose
        x = current_pose.ravel()[3]
        y = current_pose.ravel()[7]
        z = current_pose.ravel()[11]

        position = np.float32([x, y, z])

        pred = self.KF.track(position, self.fps)
        predX = self.KF.predict(self.fps)
        self.frames[-1].predict_position = predX

        # Position correction
        current_pose.ravel()[3] = predX[0]
        current_pose.ravel()[7] = predX[1]
        current_pose.ravel()[11] = predX[2]

    def optimize(self, local_window=20, fix_points=False, verbose=False, rounds=50):
        err = optimize(self.frames, self.points, local_window, fix_points, verbose, rounds)

        # prune points
        culled_pt_count = 0
        for p in self.points:
          # <= 4 match point that's old
          old_point = len(p.frames) <= 4 #and p.frames[-1].id+7 < self.max_frame

          # compute reprojection error
          errs = []
          for f,idx in zip(p.frames, p.idxs):
            uv = f.key_pts[idx]
            proj = np.dot(f.pose[:3], p.homogeneous())
            proj = proj[0:2] / proj[2]
            errs.append(np.linalg.norm(proj-uv))

          # cull
          if old_point or np.mean(errs) > 0.02:
            culled_pt_count += 1
            self.points.remove(p)
            p.delete()
        print("Culled:   %d points" % (culled_pt_count))
        self.max_frame += 1
        return err

    def GeneralOptimization(self):
        """ General optimization interface """

        """ K-Means Clustering for 3D points """
        
        """ Move optimization methods out of class 
        into separate functions or a general class for optimization."""
        ...

    def create_viewer(self):
        self.q3D = Queue()
        self.vp = Process(target=self.viewer_thread, args=(self.q3D,))
        self.vp.daemon = True
        self.vp.start()

    def release(self):
        self.vp.kill()
        # self.vp.terminate()
        return True

    def viewer_thread(self, q3d):
        self.viewer_init()
        while True:
            self.viewer_refresh(q3d)

    def viewer_init(self):
        pangolin.CreateWindowAndBind('Viewport', self.width, self.height)
        gl.glEnable(gl.GL_DEPTH_TEST)

        self.scam = pangolin.OpenGlRenderState(
            pangolin.ProjectionMatrix(*self.pmx),
            pangolin.ModelViewLookAt(*self.mvla))
        self.handler = pangolin.Handler3D(self.scam)

        # Create Interactive View in window
        self.dcam = pangolin.CreateDisplay()
        self.dcam.SetBounds(0.0, 1.0, 0.0, 1.0, -self.width/self.height)
        self.dcam.SetHandler(self.handler)

        # Create panel
        self.panel = pangolin.CreatePanel('ui')
        self.panel.SetBounds(0.0, 0.2, 0.0, 100/640.)
        self.psize = pangolin.VarFloat('ui.Point_size', value=2, min=0.5, max=5)
        self.gain = pangolin.VarFloat('ui.Gain', value=1.0, min=0, max=3)
        self.background = pangolin.VarFloat('ui.Background', value=0.0, min=0, max=1)
        self.alpha = pangolin.VarFloat('ui.Alpha', value=1.0, min=0, max=1)
        self.screenshot = pangolin.VarBool('ui.Screenshot', value=False, toggle=False)

    def viewer_refresh(self, q3d):
        if self.state is None or not q3d.empty():
            self.state = q3d.get()

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glClearColor(self.background, self.background, self.background, self.alpha)
        self.dcam.Activate(self.scam)

        if pangolin.Pushed(self.screenshot):
            pangolin.SaveWindowOnRender('screenshot_'+str(len(self.state[1])))

        # draw Axis and Grid
        draw_axis(3.0)
        draw_grid(5.0)

        # draw keypoints
        points_color = self.state[1]*np.single(self.gain)
        draw_keypoints_color(self.state[0], self.psize, points_color)  # Inliers points
        # draw_keypoints(self.state[5], self.psize, (0.25, 0.25, 0.25)) # Outliers points

        # draw trajectory
        draw_trajectory(self.state[2], 1, (1.0, 0.0, 0.0))
        draw_trajectory(self.state[5], 1, (0.0, 1.0, 0.0))

        # draw all poses
        # draw_all_poses(self.state[3], (0.75, 0.75, 0.15),
        #                 self.state[4], (1.0, 0.0, 0.0))

        # draw single (current) poses
        draw_single_poses(self.state[4], (1.0, 1.0, 0.0))

        pangolin.FinishFrame()

    def put3D(self, optimization=True):
        ''' put 3D data in Queue '''
        if self.q3D is None:
            return
        predict_poses, poses, pts, cam_pts, color = [], [], [], [], []
        # get last element of list
        current_pose = [self.frames[-1].pose]
        # data from camera
        for f in self.frames:
            x = f.pose.ravel()[3]
            y = f.pose.ravel()[7]
            z = f.pose.ravel()[11]
            cam_pts.append([x, y, z])
            predict_poses.append(f.predict_position)
            poses.append(f.pose)
        # data from points
        for p in self.points:
            pts.append(p.pt)
            color.append(p.color)
        self.q3D.put((np.array(pts), np.array(color),
                    np.array(cam_pts), np.array(poses[:-1]),
                    np.array(current_pose), np.array(predict_poses)))

