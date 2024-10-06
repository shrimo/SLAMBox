""" GUI for tracking nodes """
from Qt import QtCore, QtWidgets
from plugins_ui.main_gui_nodes import NodeColorStyle
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
    NODE_PROP_FLOAT,
)

ncs = NodeColorStyle()
ncs.set_value(15)


class VitTrack(BaseNode):
    __identifier__ = "nodes.Tracking"
    NODE_NAME = "VitTrack"

    def __init__(self):
        super().__init__()
        self.add_input("in", color=(180, 80, 180))
        self.add_output("out")
        self.create_property(
            "label_model_path", "Model path", widget_type=NODE_PROP_QLABEL
        )
        self.create_property(
            "model_path",
            "data/object_tracking_vittrack_2023sep.onnx",
            widget_type=NODE_PROP_FILE,
        )
        self.create_property("label_variable", "Variable", widget_type=NODE_PROP_QLABEL)
        self.create_property("variable", "track1", widget_type=NODE_PROP_QLINEEDIT)
        self.add_checkbox(
            "show_ROI", "Show ROI", text="On/Off", state=False, tab="attributes"
        )
        self.set_color(*ncs.Tracking)
