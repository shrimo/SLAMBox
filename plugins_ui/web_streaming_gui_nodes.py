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
    NODE_PROP_QCHECKBOX,
    NODE_PROP_FLOAT,
    NODE_PROP_INT,
    NODE_PROP_VECTOR2
)

ncs = NodeColorStyle()
ncs.set_value(15)

class WebStreaming(BaseNode):
    __identifier__ = 'nodes.Viewer'
    NODE_NAME = 'WebStreaming'
    def __init__(self):
        super(WebStreaming, self).__init__()
        self.add_input('in', color=(180, 80, 180))
        self.add_text_input('node_name', 'Name', text='WebStreaming', tab='attributes')
        self.set_color(*ncs.Viewer)