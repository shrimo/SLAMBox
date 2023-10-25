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
        self.add_input('ina', color=(180, 80, 180))
        self.add_input('inb', color=(180, 80, 180))
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
        self.create_property('label_m_samples', 'm_samples', widget_type=NODE_PROP_QLABEL)
        self.create_property('m_samples', 8, widget_type=NODE_PROP_INT)
        self.create_property('label_r_threshold', 'r_threshold', widget_type=NODE_PROP_QLABEL)
        self.create_property('r_threshold', 0.02, widget_type=NODE_PROP_FLOAT)
        self.create_property('label_m_trials', 'm_trials', widget_type=NODE_PROP_QLABEL)
        self.create_property('m_trials', 300, widget_type=NODE_PROP_INT)
        self.create_property('label_size_marker', 'Marker size', widget_type=NODE_PROP_QLABEL)
        self.create_property('marker_size', 5, widget_type=NODE_PROP_INT)
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

class Open3DMap(BaseNode):
    __identifier__ = 'nodes.SLAMBox'
    NODE_NAME = 'Open3DMap'
    def __init__(self):
        super().__init__()
        self.add_input('in', color=(180, 80, 180))
        self.add_output('out')
        self.create_property('label_point_size', 'point size', widget_type=NODE_PROP_QLABEL)
        self.create_property('point_size', 2.0, widget_type=NODE_PROP_FLOAT)
        self.create_property('label_point_color', 'Point color', widget_type=NODE_PROP_QLABEL)
        self.create_property('point_color', (1, 0, 0), widget_type=NODE_PROP_COLORPICKER)
        self.set_color(*ncs.SLAMBox)

class LineModelOptimization(BaseNode):
    __identifier__ = 'nodes.SLAMBox'
    NODE_NAME = 'LineModelOptimization'
    def __init__(self):
        super().__init__()
        self.add_input('in', color=(180, 80, 180))
        self.add_output('out')
        self.create_property('label_m_samples', 'm_samples', widget_type=NODE_PROP_QLABEL)
        self.create_property('m_samples', 8, widget_type=NODE_PROP_INT)
        self.create_property('label_r_threshold', 'r_threshold', widget_type=NODE_PROP_QLABEL)
        self.create_property('r_threshold', 50, widget_type=NODE_PROP_INT)
        self.create_property('label_m_trials', 'm_trials', widget_type=NODE_PROP_QLABEL)
        self.create_property('m_trials', 100, widget_type=NODE_PROP_INT)
        self.add_checkbox('delete_points', 'Delete pointst', text='On/Off', state=False, tab='attributes')
        self.set_color(*ncs.SLAMBox)

class GeneralGraphOptimization(BaseNode):
    __identifier__ = 'nodes.SLAMBox'
    NODE_NAME = 'GeneralGraphOptimization'
    def __init__(self):
        super().__init__()
        self.add_input('in', color=(180, 80, 180))
        self.add_output('out')
        self.create_property('label_step_frame', 'Step frame', widget_type=NODE_PROP_QLABEL)
        self.create_property('step_frame', 4, widget_type=NODE_PROP_INT)
        self.add_checkbox('delete_points', 'Delete pointst', text='On/Off', state=False, tab='attributes')
        self.set_color(*ncs.SLAMBox)

class DNNMask(BaseNode):
    __identifier__ = 'nodes.SLAMBox'
    NODE_NAME = 'DNNMask'
    def __init__(self):
        super(DNNMask, self).__init__()
        self.add_input('in', color=(180, 80, 180))
        self.add_output('out')
        self.add_text_input('coco_names', 'Coco names', text='data/coco.names', tab='attributes')
        self.add_text_input('config', 'Config', text='data/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt', tab='attributes')
        self.add_text_input('weights', 'Weights', text='data/frozen_inference_graph.pb', tab='attributes')
        self.add_text_input('threshold', 'Threshold', text='0.5', tab='attributes')
        self.add_text_input('nms_threshold', 'NMS Threshold', text='0.2', tab='attributes')
        self.add_checkbox('show_mask', 'Show mask', text='On/Off', state=False, tab='attributes')
        self.set_color(*ncs.DNeuralNetworks)

