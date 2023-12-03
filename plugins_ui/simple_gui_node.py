"""Example of a simple node (frontend)"""

from Qt import QtCore, QtWidgets
from plugins_ui.main_gui_nodes import NodeColorStyle
from NodeGraphQt import BaseNode
from NodeGraphQt.constants import (
    NODE_PROP_QLABEL,
    NODE_PROP_COLORPICKER,
    NODE_PROP_SLIDER,
)

ncs = NodeColorStyle()
ncs.set_value(15)


class SimpleNode(BaseNode):
    __identifier__ = "nodes.Draw"
    NODE_NAME = "SimpleNode"

    def __init__(self):
        super().__init__()
        self.add_input("in", color=(180, 80, 180))
        self.add_output("out")
        self.create_property("label_color", "Color", widget_type=NODE_PROP_QLABEL)
        self.create_property("picker", (0, 255, 0), widget_type=NODE_PROP_COLORPICKER)
        self.create_property("label_size", "Size", widget_type=NODE_PROP_QLABEL)
        self.create_property("size", 100, range=(1, 300), widget_type=NODE_PROP_SLIDER)
        self.set_color(*ncs.Draw)
