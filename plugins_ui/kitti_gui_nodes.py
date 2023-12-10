""" GUI for for KITTI Vision Benchmark nodes """
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


class KITTICamera(BaseNode):
    __identifier__ = "nodes.SLAMBox"
    NODE_NAME = "KITTICamera"

    def __init__(self):
        super().__init__()
        self.add_input("in", color=(180, 80, 180))
        self.add_output("out")
        self.create_property(
            "label_calibration_file",
            "Calibration file",
            widget_type=NODE_PROP_QLABEL,
        )
        self.create_property("file_name", "calib.txt", widget_type=NODE_PROP_FILE)
        self.set_color(*ncs.SLAMBox)
