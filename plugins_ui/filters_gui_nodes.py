"""Filters nodes GUI"""
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

from plugins_ui.main_gui_nodes import NodeColorStyle

ncs = NodeColorStyle()
ncs.set_value(15)


class Blur(BaseNode):
    __identifier__ = "nodes.Filter"
    NODE_NAME = "Blur"

    def __init__(self):
        super(Blur, self).__init__()
        self.add_input("in", color=(180, 80, 0))
        self.add_output("out")
        self.create_property("label_size", "Size", widget_type=NODE_PROP_QLABEL)
        self.create_property("blur_size", 10, range=(1, 100), widget_type=NODE_PROP_INT)
        self.set_color(*ncs.Filter)


class Sharpen(BaseNode):
    __identifier__ = "nodes.Filter"
    NODE_NAME = "Sharpen"

    def __init__(self):
        super(Sharpen, self).__init__()
        self.add_input("in", color=(180, 80, 0))
        self.add_output("out")
        self.create_property("label_size", "Size", widget_type=NODE_PROP_QLABEL)
        self.create_property("size", 5, range=(1, 10), widget_type=NODE_PROP_INT)
        self.set_color(*ncs.Filter)


class EdgeDetection(BaseNode):
    __identifier__ = "nodes.Filter"
    NODE_NAME = "EdgeDetection"

    def __init__(self):
        super(EdgeDetection, self).__init__()
        self.add_input("in", color=(180, 80, 0))
        self.add_output("out")
        self.create_property("label_minVal", "Min Val", widget_type=NODE_PROP_QLABEL)
        self.create_property("minVal", 100, range=(1, 255), widget_type=NODE_PROP_INT)
        self.create_property("label_maxVal", "Max Val", widget_type=NODE_PROP_QLABEL)
        self.create_property("maxVal", 200, range=(1, 255), widget_type=NODE_PROP_INT)
        self.set_color(*ncs.Filter)
