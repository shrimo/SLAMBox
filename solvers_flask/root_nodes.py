""" Common nodes for building a pipeline """

import cv2
import numpy as np

class SelectionTool:
    """ Frame selection tool """
    def __init__(self, win_name, callback):
        self.win_name = win_name
        self.callback = callback
        cv2.setMouseCallback(win_name, self.onmouse)
        self.drag_start = None
        self.drag_rect = None

    def onmouse(self, event, x, y, flags, param):
        """ Handling mouse events """
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
        if self.drag_start:
            if flags & cv2.EVENT_FLAG_LBUTTON:
                xo, yo = self.drag_start
                x0, y0 = np.minimum([xo, yo], [x, y])
                x1, y1 = np.maximum([xo, yo], [x, y])
                self.drag_rect = None
                if x1-x0 > 0 and y1-y0 > 0:
                    self.drag_rect = (x0, y0, x1, y1)
            else:
                rect = self.drag_rect
                self.drag_start = None
                self.drag_rect = None
                if rect:
                    self.callback(rect)

    def draw_selection(self, frame):
        """ Draw a selection area """
        if not self.drag_rect:
            return False
        x0, y0, x1, y1 = self.drag_rect
        cx = int(x1 * 0.5) + int(x0 * 0.5)
        cy = int(y1 * 0.5) + int(y0 * 0.5)
        cv2.drawMarker(frame, (cx, cy), (0, 0, 255), 0, 20, 1, 8)
        cv2.rectangle(frame, (x0, y0), (x1, y1), (0, 250, 250), 1)

class Node:
    """ Root node that all nodes """
    def __init__(self, type_, id_, param, window_name, buffer):
        self.buffer = buffer
        self.empty_roi = (np.int64(), np.int64(), np.int64(), np.int64())
        self.type_ = type_
        self.id_ = id_
        self.window_name = window_name
        self.input_nodes = []
        self.param = param
        self.disabled = param['disabled']
        # if self.type_ == 'Viewer':
        #     cv2.namedWindow(self.window_name, cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_AUTOSIZE)
        #     # cv2.namedWindow(self.window_name, cv2.WINDOW_GUI_EXPANDED | cv2.WINDOW_AUTOSIZE)
        #     cv2.moveWindow(self.window_name, 100,100)
        #     # Initialization to invoke the selection tool
        #     super().__init__(self.window_name, self.selection_callback)
        #     self.ROI_coordinates = None

    # def selection_callback(self, rect):
    #     self.ROI_coordinates = rect

    def add_input(self, node):
        self.input_nodes.append(node)

    def get_input(self):
        return self.input_nodes

    def get_frame(self, port_number):
        """ Port number - node input number """
        return self.input_nodes[port_number].out_frame()

    def color_reversed(self, x):
        return (x[2],x[1],x[0])

