""" GUI for SLAM Box nodes """
from Qt import QtCore, QtWidgets
from plugins_ui.main_gui_nodes import NodeColorStyle
from NodeGraphQt import BaseNode
from NodeGraphQt.constants import (
    NODE_PROP_QLABEL,
    NODE_PROP_QLINEEDIT,
    NODE_PROP_QCOMBO,
    NODE_PROP_QSPINBOX,
    NODE_PROP_COLORPICKER,
    NODE_PROP_FILE,
    NODE_PROP_SLIDER,
    NODE_PROP_FILE,
    NODE_PROP_FILE_SAVE,
    NODE_PROP_QCHECKBOX,
    NODE_PROP_FLOAT,
    NODE_PROP_INT,
    NODE_PROP_VECTOR2,
)

ncs = NodeColorStyle()
ncs.set_value(15)


class Camera(BaseNode):
    __identifier__ = "nodes.SLAMBox"
    NODE_NAME = "Camera"

    def __init__(self):
        super().__init__()
        self.add_input("in", color=(180, 80, 180))
        self.add_output("out")
        self.create_property(
            "label_focal_length", "Focal length", widget_type=NODE_PROP_QLABEL
        )
        self.create_property("focal_length", 525, widget_type=NODE_PROP_INT)
        self.create_property(
            "label_frame_width", "Frame width (pix)", widget_type=NODE_PROP_QLABEL
        )
        self.create_property("frame_width", 1920, widget_type=NODE_PROP_INT)
        self.create_property(
            "label_frame_height", "Frame height (pix)", widget_type=NODE_PROP_QLABEL
        )
        self.create_property("frame_height", 1080, widget_type=NODE_PROP_INT)
        self.create_property(
            "label_calibration_data",
            "calibration data path",
            widget_type=NODE_PROP_QLABEL,
        )
        self.create_property(
            "calibration_data", "data/calibration_data.npz", widget_type=NODE_PROP_FILE
        )
        self.set_color(*ncs.SLAMBox)


class DetectorDescriptor(BaseNode):
    __identifier__ = "nodes.SLAMBox"
    NODE_NAME = "DetectorDescriptor"

    def __init__(self):
        super().__init__()
        self.add_input("ina", color=(180, 80, 180))
        self.add_input("inb", color=(180, 80, 180))
        self.add_output("out")
        self.create_property(
            "label_nfeatures", "Number of features", widget_type=NODE_PROP_QLABEL
        )
        self.create_property("nfeatures", 1000, widget_type=NODE_PROP_INT)
        self.add_checkbox(
            "show_points", "Show points", text="On/Off", state=False, tab="attributes"
        )
        descriptors_items = ["ORB", "AKAZE"]
        self.create_property(
            "label_algorithm", "Algorithm", widget_type=NODE_PROP_QLABEL
        )
        self.create_property(
            "algorithm", "ORB", items=descriptors_items, widget_type=NODE_PROP_QCOMBO
        )
        self.set_color(*ncs.SLAMBox)


class MatchPoints(BaseNode):
    __identifier__ = "nodes.SLAMBox"
    NODE_NAME = "MatchPoints"

    def __init__(self):
        super().__init__()
        self.add_input("in", color=(180, 80, 180))
        self.add_output("out")
        self.create_property(
            "label_m_samples", "m_samples", widget_type=NODE_PROP_QLABEL
        )
        self.create_property("m_samples", 8, widget_type=NODE_PROP_INT)
        self.create_property(
            "label_r_threshold", "r_threshold", widget_type=NODE_PROP_QLABEL
        )
        self.create_property("r_threshold", 0.02, widget_type=NODE_PROP_FLOAT)
        self.create_property("label_m_trials", "m_trials", widget_type=NODE_PROP_QLABEL)
        self.create_property("m_trials", 300, widget_type=NODE_PROP_INT)
        self.create_property(
            "label_size_marker", "Marker size", widget_type=NODE_PROP_QLABEL
        )
        self.create_property("marker_size", 5, widget_type=NODE_PROP_INT)
        self.add_checkbox(
            "show_marker", "Show marker", text="On/Off", state=False, tab="attributes"
        )
        self.set_color(*ncs.SLAMBox)


class Triangulate(BaseNode):
    __identifier__ = "nodes.SLAMBox"
    NODE_NAME = "Triangulate"

    def __init__(self):
        super().__init__()
        self.add_input("in", color=(180, 80, 180))
        self.add_output("out")
        self.create_property(
            "label_m_orb_distance", "ORB distance", widget_type=NODE_PROP_QLABEL
        )
        self.create_property(
            "orb_distance", 64.0, range=(1.0, 100.0), widget_type=NODE_PROP_FLOAT
        )
        self.create_property(
            "label_show_marker", "Show marker", widget_type=NODE_PROP_QLABEL
        )
        self.create_property("show_marker", False, widget_type=NODE_PROP_QCHECKBOX)

        self.set_color(*ncs.SLAMBox)


class Show2DMap(BaseNode):
    __identifier__ = "nodes.SLAMBox"
    NODE_NAME = "Show2DMap"

    def __init__(self):
        super().__init__()
        self.add_input("in", color=(180, 80, 180))
        self.add_output("out")
        self.create_property(
            "label_point_size", "point size", widget_type=NODE_PROP_QLABEL
        )
        self.create_property("point_size", 2, widget_type=NODE_PROP_INT)
        self.create_property(
            "label_point_color", "Point color", widget_type=NODE_PROP_QLABEL
        )
        self.create_property(
            "point_color", (1, 0, 0), widget_type=NODE_PROP_COLORPICKER
        )
        self.create_property("label_offsetx", "offset x", widget_type=NODE_PROP_QLABEL)
        self.create_property("offsetx", 500, widget_type=NODE_PROP_INT)
        self.create_property("label_offsety", "offset y", widget_type=NODE_PROP_QLABEL)
        self.create_property("offsety", 0, widget_type=NODE_PROP_INT)
        self.set_color(*ncs.SLAMBox)


class Open3DMap(BaseNode):
    __identifier__ = "nodes.SLAMBox"
    NODE_NAME = "Open3DMap"

    def __init__(self):
        super().__init__()
        self.add_input("in", color=(180, 80, 180))
        self.add_output("out")
        self.create_property(
            "label_point_size", "point size", widget_type=NODE_PROP_QLABEL
        )
        self.create_property("point_size", 2.0, widget_type=NODE_PROP_FLOAT)
        self.create_property(
            "label_point_color", "Point color", widget_type=NODE_PROP_QLABEL
        )
        self.create_property(
            "point_color", (1, 0, 0), widget_type=NODE_PROP_COLORPICKER
        )
        self.create_property(
            "label_windiw_size", "Windiw size", widget_type=NODE_PROP_QLABEL
        )
        self.create_property("window_size", [1024, 576], widget_type=NODE_PROP_VECTOR2)
        self.create_property(
            "label_write_pcd", "Write point clouds", widget_type=NODE_PROP_QLABEL
        )
        self.create_property("write_pcd", False, widget_type=NODE_PROP_QCHECKBOX)
        self.create_property("label_file", "File path", widget_type=NODE_PROP_QLABEL)
        self.create_property(
            "file", "./data/pcd/slam_map_", widget_type=NODE_PROP_FILE_SAVE
        )
        self.set_color(*ncs.SLAMBox)


class LineModelOptimization(BaseNode):
    __identifier__ = "nodes.SLAMBox"
    NODE_NAME = "LineModelOptimization"

    def __init__(self):
        super().__init__()
        self.add_input("in", color=(180, 80, 180))
        self.add_output("out")
        self.create_property(
            "label_m_samples", "m_samples", widget_type=NODE_PROP_QLABEL
        )
        self.create_property("m_samples", 8, widget_type=NODE_PROP_INT)
        self.create_property(
            "label_r_threshold", "r_threshold", widget_type=NODE_PROP_QLABEL
        )
        self.create_property("r_threshold", 50, widget_type=NODE_PROP_INT)
        self.create_property("label_m_trials", "m_trials", widget_type=NODE_PROP_QLABEL)
        self.create_property("m_trials", 100, widget_type=NODE_PROP_INT)
        self.add_checkbox(
            "delete_points",
            "Delete pointst",
            text="On/Off",
            state=True,
            tab="attributes",
        )
        self.set_color(*ncs.slam_optimization)


class GeneralGraphOptimization(BaseNode):
    __identifier__ = "nodes.SLAMBox"
    NODE_NAME = "GeneralGraphOptimization"

    def __init__(self):
        super().__init__()
        self.add_input("in", color=(180, 80, 180))
        self.add_output("out")
        # Pymem version Dictionary containing solvers
        # https://github.com/RainerKuemmerle/g2o/tree/pymem
        SolverSE3 = ["CSparseSE3", "EigenSE3", "CholmodSE3", "DenseSE3", "PCGSE3"]
        # version by https://github.com/miquelmassot/g2o-python
        # SolverSE3 = [
        #     "SolverEigenSE3",
        #     "SolverDenseSE3"
        # ]
        self.create_property(
            "label_solverSE3", "SolverSE3", widget_type=NODE_PROP_QLABEL
        )
        self.create_property(
            "solverSE3", "EigenSE3", items=SolverSE3, widget_type=NODE_PROP_QCOMBO
        )
        self.create_property(
            "label_step_frame", "Step frame", widget_type=NODE_PROP_QLABEL
        )
        self.create_property("step_frame", 4, widget_type=NODE_PROP_INT)
        self.set_color(*ncs.slam_optimization)


class KalmanFilterOptimization(BaseNode):
    __identifier__ = "nodes.SLAMBox"
    NODE_NAME = "KalmanFilterOptimization"

    def __init__(self):
        super().__init__()
        self.add_input("in", color=(180, 80, 180))
        self.add_output("out")
        self.create_property("label_m_fps", "fps", widget_type=NODE_PROP_QLABEL)
        self.create_property("fps", 30.0, widget_type=NODE_PROP_FLOAT)
        self.create_property("label_r_drag", "drag", widget_type=NODE_PROP_QLABEL)
        self.create_property("drag", 0.8, widget_type=NODE_PROP_FLOAT)
        self.create_property("label_m_grav", "gravity", widget_type=NODE_PROP_QLABEL)
        self.create_property("grav", 0.0, widget_type=NODE_PROP_FLOAT)
        self.create_property(
            "label_m_procNoise", "procNoise", widget_type=NODE_PROP_QLABEL
        )
        self.create_property("procNoise", 0.1, widget_type=NODE_PROP_FLOAT)
        self.create_property(
            "label_m_measNoise", "measNoise", widget_type=NODE_PROP_QLABEL
        )
        self.create_property("measNoise", 0.1, widget_type=NODE_PROP_FLOAT)
        self.set_color(*ncs.slam_optimization)


class DNNMask(BaseNode):
    __identifier__ = "nodes.SLAMBox"
    NODE_NAME = "DNNMask"

    def __init__(self):
        super(DNNMask, self).__init__()
        self.add_input("in", color=(180, 80, 180))
        self.add_output("out")
        self.create_property(
            "label_class_names", "Class names file path", widget_type=NODE_PROP_QLABEL
        )
        self.create_property(
            "class_names", "data/coco.names", widget_type=NODE_PROP_FILE
        )
        self.create_property(
            "label_config", "Config file path", widget_type=NODE_PROP_QLABEL
        )
        self.create_property(
            "config",
            "data/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt",
            widget_type=NODE_PROP_FILE,
        )
        self.create_property(
            "label_weights", "Weights file path", widget_type=NODE_PROP_QLABEL
        )
        self.create_property(
            "weights", "data/frozen_inference_graph.pb", widget_type=NODE_PROP_FILE
        )
        self.add_text_input("threshold", "Threshold", text="0.5", tab="attributes")
        self.add_text_input(
            "nms_threshold", "NMS Threshold", text="0.2", tab="attributes"
        )
        self.add_checkbox(
            "show_mask", "Show mask", text="On/Off", state=True, tab="attributes"
        )
        self.set_color(*ncs.DNeuralNetworks)
