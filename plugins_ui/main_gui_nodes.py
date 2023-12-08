""" GUI nodes for video or image analysis and processing """
from Qt import QtCore, QtWidgets
from NodeGraphQt import BaseNode
from NodeGraphQt.constants import (
    NODE_PROP_QLABEL,
    NODE_PROP_QLINEEDIT,
    NODE_PROP_QCOMBO,
    NODE_PROP_QSPINBOX,
    NODE_PROP_COLORPICKER,
    NODE_PROP_SLIDER,
    NODE_PROP_FILE,
    NODE_PROP_QCHECKBOX,
    NODE_PROP_INT,
)


class NodeColorStyle:
    """Node Colors Style"""

    def __init__(self):
        self.Read = (110, 100, 50)
        self.Viewer = (150, 50, 50)
        self.Fusion = (50, 100, 100)
        self.Draw = (50, 100, 50)
        self.Transform = (100, 50, 20)
        self.Grade = (10, 50, 100)
        self.Filter = (100, 100, 100)
        self.Detection = (50, 30, 100)
        self.DNeuralNetworks = (30, 50, 100)
        self.Scene3D = (130, 70, 50)
        self.Controllers = (30, 30, 30)
        self.Tracking = (30, 70, 50)
        self.Time = (150, 120, 30)
        self.SLAMBox = (80, 100, 30)
        self.slam_optimization = (30, 50, 100)

    def set_value(self, value):
        """Change all values in class elements"""
        for key in self.__dict__:
            self.__dict__[key] = tuple(value + elem for elem in self.__dict__[key])


ncs = NodeColorStyle()
ncs.set_value(15)


class Read(BaseNode):
    __identifier__ = "nodes.Read"
    NODE_NAME = "Read"

    def __init__(self):
        super(Read, self).__init__()
        self.add_output("out")
        self.add_text_input("device", "Device", text="0", tab="attributes")
        # self.add_text_input('file', 'File/Stream', text='../../video/road.mp4', tab='attributes')
        self.add_text_input("start", "Start frame", text="0", tab="attributes")
        self.add_checkbox(
            "camera", "Camera", text="On/Off", state=False, tab="attributes"
        )
        self.add_checkbox("loop", "Loop", text="On/Off", state=True, tab="attributes")
        self.create_property("label_file", "File path", widget_type=NODE_PROP_QLABEL)
        self.create_property("file", "./video/road.mp4", widget_type=NODE_PROP_FILE)
        self.set_color(*ncs.Read)


class Image(BaseNode):
    __identifier__ = "nodes.Read"
    NODE_NAME = "Image"

    def __init__(self):
        super(Image, self).__init__()
        self.add_output("out")
        self.add_text_input(
            "file", "File name", text="image/target2.png", tab="attributes"
        )
        self.add_checkbox(
            "update", "Update", text="On/Off", state=True, tab="attributes"
        )
        self.set_color(*ncs.Read)


class Viewer(BaseNode):
    __identifier__ = "nodes.Viewer"
    NODE_NAME = "Viewer"

    def __init__(self):
        super(Viewer, self).__init__()
        self.add_input("in", color=(180, 80, 180))
        self.add_text_input("node_name", "Name", text="Viewport", tab="attributes")
        self.set_color(*ncs.Viewer)


class SelectionBuffer(BaseNode):
    __identifier__ = "nodes.Viewer"
    NODE_NAME = "SelectionBuffer"

    def __init__(self):
        super(SelectionBuffer, self).__init__()
        self.add_input("in", color=(180, 80, 0))
        self.add_output("out")
        self.set_color(*ncs.Viewer)
        self.add_text_input("node_name", "Name", text="Oflow Buffer", tab="attributes")


class VideoWriter(BaseNode):
    __identifier__ = "nodes.Viewer"
    NODE_NAME = "VideoWriter"

    def __init__(self):
        super(VideoWriter, self).__init__()
        self.add_input("in", color=(180, 80, 180))
        self.add_output("out", color=(80, 120, 120))
        self.add_text_input("file", "File name", text="output.mov", tab="attributes")
        self.add_text_input(
            "frame_size", "Frame Size", text="1280,720", tab="attributes"
        )
        self.add_text_input("fps", "FPS", text="30.0", tab="attributes")
        self.set_color(*ncs.Viewer)


class Insert(BaseNode):
    __identifier__ = "nodes.Fusion"
    NODE_NAME = "Insert"

    def __init__(self):
        super(Insert, self).__init__()
        self.add_input("in_a", color=(80, 120, 120))
        self.add_input("in_b", color=(80, 120, 120))
        self.add_output("out", color=(80, 120, 120))
        self.create_property("label_offset_x", "offset x", widget_type=NODE_PROP_QLABEL)
        self.create_property("offset_x", 10, range=(0, 1920), widget_type=NODE_PROP_INT)
        self.create_property("label_offset_y", "offset y", widget_type=NODE_PROP_QLABEL)
        self.create_property("offset_y", 10, range=(0, 1080), widget_type=NODE_PROP_INT)
        self.set_color(*ncs.Fusion)


class Merge(BaseNode):
    __identifier__ = "nodes.Fusion"
    NODE_NAME = "Merge"

    def __init__(self):
        super(Merge, self).__init__()
        self.add_input("in_a", color=(80, 120, 120))
        self.add_input("in_b", color=(80, 120, 120))
        self.add_output("out", color=(80, 120, 120))
        self.add_text_input("opacity_a", "Opacity A", text="0.5", tab="attributes")
        self.add_text_input("opacity_b", "Opacity B", text="0.5", tab="attributes")
        self.set_color(*ncs.Fusion)


class SwitchFrame(BaseNode):
    __identifier__ = "nodes.Fusion"
    NODE_NAME = "SwitchFrame"

    def __init__(self):
        super(SwitchFrame, self).__init__()
        self.add_input("in_a", color=(80, 120, 120))
        self.add_input("in_b", color=(80, 120, 120))
        self.add_output("out", color=(80, 120, 120))
        self.add_checkbox(
            "switch_channel", "Switch", text="On/Off", state=False, tab="attributes"
        )
        self.set_color(*ncs.Fusion)


class Move(BaseNode):
    __identifier__ = "nodes.Transform"
    NODE_NAME = "Move"

    def __init__(self):
        super(Move, self).__init__()
        self.add_input("in", color=(180, 80, 0))
        self.add_output("out")
        self.add_text_input("movex", "Move X", text="0", tab="attributes")
        self.add_text_input("movey", "Move Y", text="0", tab="attributes")
        self.add_text_input("variable", "Variable", text="track1", tab="attributes")
        self.set_color(*ncs.Transform)


class Resize(BaseNode):
    __identifier__ = "nodes.Transform"
    NODE_NAME = "Resize"

    def __init__(self):
        super(Resize, self).__init__()
        self.add_input("in", color=(180, 80, 0))
        self.add_output("out")
        self.create_property("label_resize", "Resize", widget_type=NODE_PROP_QLABEL)
        self.create_property(
            "resize", 50, range=(10, 200), widget_type=NODE_PROP_SLIDER
        )
        self.set_color(*ncs.Transform)


class Reformat(BaseNode):
    __identifier__ = "nodes.Transform"
    NODE_NAME = "Reformat"

    def __init__(self):
        super(Reformat, self).__init__()
        self.add_input("in", color=(180, 80, 0))
        self.add_output("out")
        self.create_property("label_width", "Width", widget_type=NODE_PROP_QLABEL)
        self.create_property(
            "width_", 1024, range=(10, 1920), widget_type=NODE_PROP_SLIDER
        )
        self.create_property("label_height", "Height", widget_type=NODE_PROP_QLABEL)
        self.create_property(
            "height_", 576, range=(10, 1080), widget_type=NODE_PROP_SLIDER
        )
        self.set_color(*ncs.Transform)


class Gamma(BaseNode):
    __identifier__ = "nodes.Grade"
    NODE_NAME = "Gamma"

    def __init__(self):
        super(Gamma, self).__init__()
        self.add_input("in", color=(180, 80, 0))
        self.add_output("out")
        self.add_text_input("gamma", "Gamma", text="0.5", tab="attributes")
        self.set_color(*ncs.Grade)


class Brightness(BaseNode):
    __identifier__ = "nodes.Grade"
    NODE_NAME = "Brightness"

    def __init__(self):
        super(Brightness, self).__init__()
        self.add_input("in", color=(180, 80, 0))
        self.add_output("out")
        self.add_text_input("brightness", "Brightness", text="50", tab="attributes")
        self.set_color(*ncs.Grade)


class Saturation(BaseNode):
    __identifier__ = "nodes.Grade"
    NODE_NAME = "Saturation"

    def __init__(self):
        super(Saturation, self).__init__()
        self.add_input("in", color=(180, 80, 0))
        self.add_output("out")
        self.add_text_input("saturation", "Saturation", text="1.2", tab="attributes")
        self.set_color(*ncs.Grade)


class GRAY2BGR(BaseNode):
    __identifier__ = "nodes.Grade"
    NODE_NAME = "GRAY2BGR"

    def __init__(self):
        super(GRAY2BGR, self).__init__()
        self.add_checkbox(
            "invert", "Invert", text="BGR2GRAY", state=False, tab="attributes"
        )
        self.add_input("in", color=(180, 80, 0))
        self.add_output("out")
        self.set_color(*ncs.Grade)


class CLAHE(BaseNode):
    __identifier__ = "nodes.Grade"
    NODE_NAME = "CLAHE"

    def __init__(self):
        super(CLAHE, self).__init__()
        self.add_input("in", color=(180, 80, 0))
        self.add_output("out")
        self.add_text_input("clipLimit", "Clip limits", text="2.0", tab="attributes")
        self.add_text_input(
            "tileGridSize", "Tile grid size", text="8,8", tab="attributes"
        )
        self.set_color(*ncs.Grade)
