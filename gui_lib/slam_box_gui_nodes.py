""" GUI for SLAM Box nodes """
from Qt import QtCore, QtWidgets
from gui_lib import NodeColorStyle
from NodeGraphQt import BaseNode
from NodeGraphQt.constants import (NODE_PROP_QLABEL,
                                   NODE_PROP_QLINEEDIT,
                                   NODE_PROP_QCOMBO,
                                   NODE_PROP_QSPINBOX,
                                   NODE_PROP_COLORPICKER,
                                   NODE_PROP_SLIDER,
                                   NODE_PROP_FILE,
                                   NODE_PROP_QCHECKBOX,
                                   NODE_PROP_FLOAT,
                                   NODE_PROP_INT)

ncs = NodeColorStyle()
ncs.set_value(15)

class DetectorDescriptor(BaseNode):
    __identifier__ = 'nodes.SLAMBox'
    NODE_NAME = 'DetectorDescriptor'
    def __init__(self):
        super().__init__()
        self.add_input('in', color=(180, 80, 180))
        self.add_output('out')
        self.create_property('label_nfeatures', 'Number of features', widget_type=NODE_PROP_QLABEL)
        self.create_property('nfeatures', 1000, widget_type=NODE_PROP_INT)
        self.add_checkbox('show_points', 'Show points', text='On/Off', state=False, tab='attributes')
        descriptors_items = ['SIFT', 'ORB', 'AKAZE']
        self.create_property('label_algorithm', 'Algorithm', widget_type=NODE_PROP_QLABEL)
        self.create_property('algorithm', 'ORB', items=descriptors_items, widget_type=NODE_PROP_QCOMBO)        
        self.set_color(*ncs.SLAMBox)

class MatchPoints(BaseNode):
    __identifier__ = 'nodes.SLAMBox'
    NODE_NAME = 'MatchPoints'
    def __init__(self):
        super().__init__()
        self.add_input('in', color=(180, 80, 180))
        self.add_output('out')
        self.create_property('label_size_marker', 'Marker size', widget_type=NODE_PROP_QLABEL)
        self.create_property('marker_size', 15, widget_type=NODE_PROP_INT)
        self.add_checkbox('show_marker', 'Show marker', text='On/Off', state=False, tab='attributes')
        self.set_color(*ncs.SLAMBox)

class Show3DMap(BaseNode):
    __identifier__ = 'nodes.SLAMBox'
    NODE_NAME = 'Show3DMap'
    def __init__(self):
        super().__init__()
        self.add_input('in', color=(180, 80, 180))
        self.add_output('out')
        self.create_property('label_size_marker', 'Marker size', widget_type=NODE_PROP_QLABEL)
        self.create_property('marker_size', 15, widget_type=NODE_PROP_INT)
        self.create_property('marker_color', (255, 0, 0), widget_type=NODE_PROP_COLORPICKER)
        self.add_checkbox('show_marker', 'Show marker', text='On/Off', state=False, tab='attributes')
        self.set_color(*ncs.SLAMBox)


