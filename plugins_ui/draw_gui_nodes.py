"""Сlass for generating images and displaying information or attributes (GUI)"""
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


class ColorSet(BaseNode):
    __identifier__ = "nodes.Draw"
    NODE_NAME = "ColorSet"

    def __init__(self):
        super(ColorSet, self).__init__()
        self.add_input("in", color=(180, 80, 0))
        self.create_property("label_num_rows", "Num rows", widget_type=NODE_PROP_QLABEL)
        self.create_property("num_rows", 6, widget_type=NODE_PROP_INT)
        self.create_property("label_num_cols", "Num cols", widget_type=NODE_PROP_QLABEL)
        self.create_property("num_cols", 6, widget_type=NODE_PROP_INT)
        self.add_output("out")
        self.set_color(*ncs.Draw)


class FPS(BaseNode):
    __identifier__ = "nodes.Draw"
    NODE_NAME = "FPS"

    def __init__(self):
        super(FPS, self).__init__()
        self.add_input("in", color=(180, 80, 0))
        self.add_output("out")
        self.set_color(*ncs.Draw)
        self.create_property("label_color", "Color", widget_type=NODE_PROP_QLABEL)
        self.create_property(
            "color_picker", (255, 255, 255), widget_type=NODE_PROP_COLORPICKER
        )


class Counter(BaseNode):
    __identifier__ = "nodes.Draw"
    NODE_NAME = "Counter"

    def __init__(self):
        super(Counter, self).__init__()
        self.add_input("in", color=(180, 80, 0))
        self.add_output("out")
        self.set_color(*ncs.Draw)
        self.create_property("label_color", "Color", widget_type=NODE_PROP_QLABEL)
        self.create_property(
            "counter_color", (255, 255, 255), widget_type=NODE_PROP_COLORPICKER
        )


class Constant(BaseNode):
    __identifier__ = "nodes.Draw"
    NODE_NAME = "Constant"

    def __init__(self):
        super(Constant, self).__init__()
        self.add_output("out")
        self.set_color(*ncs.Draw)
        self.create_property("label_color", "Color", widget_type=NODE_PROP_QLABEL)
        self.create_property(
            "constant_color", (150, 70, 30), widget_type=NODE_PROP_COLORPICKER
        )
        self.add_text_input("width_", "Width", text="1280", tab="attributes")
        self.add_text_input("height_", "Height", text="720", tab="attributes")


class Text(BaseNode):
    __identifier__ = "nodes.Draw"
    NODE_NAME = "Text"

    def __init__(self):
        super(Text, self).__init__()
        self.add_input("in", color=(180, 80, 0))
        self.add_output("out")
        self.set_color(*ncs.Draw)
        self.add_text_input("text", "Text", text="Optical core", tab="attributes")
        self.create_property("label_color", "Color", widget_type=NODE_PROP_QLABEL)
        self.create_property(
            "text_color_", (160, 93, 31), widget_type=NODE_PROP_COLORPICKER
        )
        self.add_text_input("px", "Px", text="450", tab="attributes")
        self.add_text_input("py", "Py", text="360", tab="attributes")
        self.add_text_input("size_", "Size", text="2.0", tab="attributes")


class Trajectory(BaseNode):
    __identifier__ = "nodes.Draw"
    NODE_NAME = "Trajectory"

    def __init__(self):
        super(Trajectory, self).__init__()
        self.add_input("in", color=(180, 80, 0))
        self.add_output("out")
        self.set_color(*ncs.Draw)
        self.create_property("label_color", "Color", widget_type=NODE_PROP_QLABEL)
        self.create_property(
            "track_color", (10, 20, 220), widget_type=NODE_PROP_COLORPICKER
        )
        self.add_text_input("variable", "Variable", text="track1", tab="attributes")
        self.add_text_input("length", "Length", text="150", tab="attributes")
        self.add_text_input("size", "Size", text="2", tab="attributes")
