"""
Basic nodes for common video stream operations
"""

import cv2
import numpy as np
from solvers_flask.root_nodes import Node, SelectionTool
from solvers_flask.misc import get_tuple, frame_error


class Viewer(Node):
    """Displays frames. End node for nodes graph."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cv2.namedWindow(self.window_name, cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_AUTOSIZE)
        # cv2.namedWindow(self.window_name, cv2.WINDOW_GUI_EXPANDED | cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow(self.window_name, 100,100)
        # Initialization to invoke the selection tool
        self.selection_tool= SelectionTool(self.window_name, self.selection_callback)
        self.ROI_coordinates = None

    def show_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("ViewerNode stop")
            return None
        # Add switch on/off selection tool (draw_selection - metod from class SelectionTool)
        self.selection_tool.draw_selection(frame)
        if self.ROI_coordinates:
            # Save the ROI coordinates to the buffer
            self.buffer.roi = self.ROI_coordinates
            self.buffer.switch = True  # old metod
            self.ROI_coordinates = self.empty_roi
        cv2.imshow(self.window_name, frame)
        return True

    def selection_callback(self, rect):
        self.ROI_coordinates = rect

    def stop(self):
        print("Stop Viewer")
        # self.buffer.variable['STOPSLAM'] = True
        cv2.waitKey(10)
        return True


class SelectionBuffer(Node):
    """Frame selection tool"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Image = None

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("SelectionTools stop")
            return None
        if self.buffer.roi:
            self.calculations_for_ROI(frame, self.buffer.roi)
            self.buffer.roi = self.empty_roi
            # self.buffer.switch = True
        return self.Image

    def calculations_for_ROI(self, frame, coord):
        """
        Set region of interest (ROI)
        develop a template for transferring the area
        as a target for object recognition
        """
        frame = frame[coord[1] : coord[3], coord[0] : coord[2]]
        self.Image = frame.copy()

    def update(self, param):
        pass


class Read(Node):
    """Node Read for receive video data"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.param["camera"]:
            self.cap = cv2.VideoCapture(int(self.param["device"]))
            if not self.cap.isOpened():
                print("Cannot open camera")
                exit()
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        else:
            self.loop = self.param["loop"]
            self.start_frame = int(self.param["start"])
            self.cap = cv2.VideoCapture(self.param["file"])
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        width = np.int32(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = np.int32(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # Storing metadata in a buffer. Additional tmp buffer to save the reference value.
        self.buffer.metadata = {
            "fps": fps,
            "width": width,
            "height": height,
            "frame_size": [width, height]
        }

    def out_frame(self):
        success, frame = self.cap.read()
        if success:
            return frame
        elif self.loop:
            """If it's a loop, set the counter to start frame and return current frame"""
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
            return self.out_frame()
        self.cap.release()
        print("ReadNode a stop")
        return None


class VideoWriter(Node):
    """Write stream to file"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file = self.param["file"]
        self.frame_size = get_tuple(self.param["frame_size"])
        self.fps = float(self.param["fps"])
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.video_out = cv2.VideoWriter(self.file, fourcc, self.fps, self.frame_size)

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            self.video_out.release()
            print("VideoWriter stop")
            return None
        frame = cv2.resize(frame, self.frame_size)
        self.video_out.write(frame)
        return frame

    def update(self, param):
        pass


class Image(Node):
    """Node Read for receive image data"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file = self.param["file"]
        self.image_update = self.param["update"]
        self.image = cv2.imread(self.file, cv2.IMREAD_COLOR)
        self.buffer.switch = True

    def out_frame(self):
        if self.image_update:
            return cv2.imread(self.file, cv2.IMREAD_COLOR)
        return self.image

    def update(self, param):
        self.file = param["file"]
        self.image_update = param["update"]
        self.image = cv2.imread(self.file, cv2.IMREAD_COLOR)


class SwitchFrame(Node):
    """Switch two streams"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_number = self.param["switch_channel"]
        self.buffer.switch = True

    def out_frame(self):
        if self.channel_number:
            return self.get_frame(1)
        else:
            return self.get_frame(0)

    def update(self, param):
        self.buffer.switch = True
        self.channel_number = param["switch_channel"]


class Merge(Node):
    """Node to merge two streams"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.op_a = float(self.param["opacity_a"])
        self.op_b = float(self.param["opacity_b"])

    def out_frame(self):
        frame_a = self.get_frame(0)
        frame_b = self.get_frame(1)
        if frame_a is None:
            print("MergeNode a stop")
            return None
        elif frame_b is None:
            print("MergeNode b stop")
            return frame_a
        height_a, width_a, channels_a = frame_a.shape
        height_b, width_b, channels_b = frame_b.shape
        h_max = max(height_a, height_b)
        w_max = max(width_a, width_b)
        frame_b = cv2.resize(frame_b, (w_max, h_max))
        frame_a = cv2.resize(frame_a, (w_max, h_max))
        return cv2.addWeighted(frame_a, self.op_a, frame_b, self.op_b, 0)

    def update(self, param):
        self.op_a = float(param["opacity_a"])
        self.op_b = float(param["opacity_b"])


class Insert(Node):
    """Inserting one video stream into another"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pos_x = int(self.param["offset_x"])
        self.pos_y = int(self.param["offset_y"])
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.msg = "Inserted frame B - out of bounds"

    def out_frame(self):
        frame_a = self.get_frame(0)
        frame_b = self.get_frame(1)
        if frame_a is None:
            print("InsertNode a stop")
            return None
        elif frame_b is None:
            print("InsertNode b stop")
            return frame_a
        height_a, width_a, channels_a = frame_a.shape
        height_b, width_b, channels_b = frame_b.shape
        """ Check out of the border """
        if width_b + self.pos_x > width_a or height_b + self.pos_y > height_a:
            return frame_error(frame_a, 'Inserted frame B - out of bounds')
            # cv2.putText(frame_a, self.msg, (30, height_a-30), self.font , 1, (0,0,255), 1)
            return frame_a
        frame_a[
            self.pos_y : self.pos_y + height_b, self.pos_x : self.pos_x + width_b
        ] = frame_b
        return frame_a

    def update(self, param):
        self.pos_x = int(param["offset_x"])
        self.pos_y = int(param["offset_y"])


class Move(Node):
    """Move frame along the axes"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.variable = self.param["variable"]
        self.movex = int(self.param["movex"])
        self.movey = int(self.param["movex"])

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("Move stop")
            return None
        if self.disabled:
            return frame
        if self.variable in self.buffer.variable:
            # tracker coordinates
            tx, ty = self.buffer.variable[self.variable]
            # frame center from buffer
            cx = self.buffer.metadata["frame_size"][0] * 0.5
            cy = self.buffer.metadata["frame_size"][1] * 0.5
            # cx = self.buffer.metadata['width_tmp']/2
            # cy = self.buffer.metadata['height_tmp']/2
            # shifts frame along tracker point to center of frame
            M = np.float32([[1, 0, -(tx - cx)], [0, 1, -(ty - cy)]])
            return cv2.warpAffine(
                frame, M, (frame.shape[1], frame.shape[0]), cv2.WARP_FILL_OUTLIERS
            )
        M = np.float32([[1, 0, self.movex], [0, 1, self.movey]])
        return cv2.warpAffine(frame, M, (frame.shape[1], frame.shape[0]))

    def update(self, param):
        self.disabled = param["disabled"]
        self.variable = param["variable"]
        self.movex = int(param["movex"])
        self.movey = int(param["movey"])


class Resize(Node):
    """Rescale frame in percents"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize = int(self.param["resize"])

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("Resize stop")
            return None
        if self.disabled:
            # restore original value
            self.buffer.metadata["frame_size"] = [
                self.buffer.metadata["width"],
                self.buffer.metadata["height"],
            ]
            return frame
        width = int(frame.shape[1] * self.resize * 0.01)
        height = int(frame.shape[0] * self.resize * 0.01)
        # save temporary values
        self.buffer.metadata["frame_size"] = [width, height]
        return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

    def update(self, param):
        self.disabled = param["disabled"]
        self.resize = int(param["resize"])


class Reformat(Node):
    """Reformat lets you resize and reposition your image
    sequences to a different format (width and height)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.width = self.param["width_"]
        self.height = self.param["height_"]

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("Resize stop")
            return None
        if self.disabled:
            # restore original value
            self.buffer.metadata["frame_size"] = [
                self.buffer.metadata["width"],
                self.buffer.metadata["height"],
            ]
            return frame
        # save temporary values
        self.buffer.metadata["frame_size"] = [self.width, self.height]
        return cv2.resize(
            frame, (self.width, self.height), interpolation=cv2.INTER_AREA
        )

    def update(self, param):
        self.disabled = param["disabled"]
        self.width = param["width_"]
        self.height = param["height_"]
