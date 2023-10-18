""" GUI nodes for video or image analysis and processing """
from Qt import QtCore, QtWidgets
from NodeGraphQt import BaseNode
from NodeGraphQt.constants import (NODE_PROP_QLABEL,
                                   NODE_PROP_QLINEEDIT,
                                   NODE_PROP_QCOMBO,
                                   NODE_PROP_QSPINBOX,
                                   NODE_PROP_COLORPICKER,
                                   NODE_PROP_SLIDER,
                                   NODE_PROP_FILE,
                                   NODE_PROP_QCHECKBOX,
                                   NODE_PROP_FLOAT)

class NodeColorStyle:
    """ Node Colors Style """
    def __init__(self):
        self.Read = (110, 100, 50)
        self.Viewer = (150, 50, 50)
        self.Fusion = (50, 100, 100)
        self.Draw = (50, 100, 50)
        self.Transform = (100, 50, 20)
        self.Grade = (0, 30, 120)
        self.Filter = (100, 100, 100)
        self.Detection = (50, 30, 100)
        self.DNeuralNetworks = (30, 50, 100)
        self.Scene3D = (130, 70, 50)
        self.Controllers = (30, 30, 30)
        self.Tracking = (30, 70, 50)
        self.Time = (150, 120, 30)
        self.SLAMBox = (80, 100, 30)

    def set_value(self, value):
        """ Change all values in class elements """
        for key in self.__dict__:
            self.__dict__[key] = tuple(value + elem for elem in self.__dict__[key])

ncs = NodeColorStyle()
ncs.set_value(15)

class Read(BaseNode):
    __identifier__ = 'nodes.Read'
    NODE_NAME = 'Read'
    def __init__(self):
        super(Read, self).__init__()
        self.add_output('out')
        self.add_text_input('device', 'Device', text='0', tab='attributes')
        self.add_text_input('file', 'File/Stream', text='./video/road.mp4', tab='attributes')
        self.add_text_input('start', 'Start frame', text='0', tab='attributes')
        self.add_checkbox('camera', 'Camera', text='On/Off', state=False, tab='attributes')
        self.add_checkbox('loop', 'Loop', text='On/Off', state=True, tab='attributes')
        self.create_property('file_x', './video/road.mp4', widget_type=NODE_PROP_FILE)
        self.set_color(*ncs.Read)

class Image(BaseNode):
    __identifier__ = 'nodes.Read'
    NODE_NAME = 'Image'
    def __init__(self):
        super(Image, self).__init__()
        self.add_output('out')
        self.add_text_input('file', 'File name', text='image/target2.png', tab='attributes')
        self.add_checkbox('update', 'Update', text='On/Off', state=True, tab='attributes')
        self.set_color(*ncs.Read)

class Viewer(BaseNode):
    __identifier__ = 'nodes.Viewer'
    NODE_NAME = 'Viewer'
    def __init__(self):
        super(Viewer, self).__init__()
        self.add_input('in', color=(180, 80, 180))
        self.add_text_input('node_name', 'Name', text='Viewport', tab='attributes')
        self.set_color(*ncs.Viewer)

class VideoWriter(BaseNode):
    __identifier__ = 'nodes.Viewer'
    NODE_NAME = 'VideoWriter'
    def __init__(self):
        super(VideoWriter, self).__init__()
        self.add_input('in', color=(180, 80, 180))
        self.add_output('out', color=(80, 120, 120))
        self.add_text_input('file', 'File name', text='output.mov', tab='attributes')
        self.add_text_input('frame_size', 'Frame Size', text='1280,720', tab='attributes')
        self.add_text_input('fps', 'FPS', text='30.0', tab='attributes')
        self.set_color(*ncs.Viewer)

class Insert(BaseNode):
    __identifier__ = 'nodes.Fusion'
    NODE_NAME = 'Insert'
    def __init__(self):
        super(Insert, self).__init__()
        self.add_input('in_a', color=(80, 120, 120))
        self.add_input('in_b', color=(80, 120, 120))
        self.add_output('out', color=(80, 120, 120))
        self.add_text_input('position_x', 'Position X', text='50', tab='attributes')
        self.add_text_input('position_y', 'Position Y', text='50', tab='attributes')
        self.set_color(*ncs.Fusion)

class Merge(BaseNode):
    __identifier__ = 'nodes.Fusion'
    NODE_NAME = 'Merge'
    def __init__(self):
        super(Merge, self).__init__()
        self.add_input('in_a', color=(80, 120, 120))
        self.add_input('in_b', color=(80, 120, 120))
        self.add_output('out', color=(80, 120, 120))
        self.add_text_input('opacity_a', 'Opacity A', text='0.5', tab='attributes')
        self.add_text_input('opacity_b', 'Opacity B', text='0.5', tab='attributes')
        self.set_color(*ncs.Fusion)

class SwitchFrame(BaseNode):
    __identifier__ = 'nodes.Fusion'
    NODE_NAME = 'SwitchFrame'
    def __init__(self):
        super(SwitchFrame, self).__init__()
        self.add_input('in_a', color=(80, 120, 120))
        self.add_input('in_b', color=(80, 120, 120))
        self.add_output('out', color=(80, 120, 120))
        self.add_checkbox('switch_channel', 'Switch', text='On/Off', state=False, tab='attributes')
        self.set_color(*ncs.Fusion)

class FPS(BaseNode):
    __identifier__ = 'nodes.Draw'
    NODE_NAME = 'FPS'
    def __init__(self):
        super(FPS, self).__init__()
        self.add_input('in', color=(180, 80, 0))
        self.add_output('out')
        self.add_text_input('fps_color', 'Color', text='250,250,250', tab='attributes')
        self.set_color(*ncs.Draw)
        self.create_property('color_picker', (255, 255, 255), widget_type=NODE_PROP_COLORPICKER)

class Counter(BaseNode):
    __identifier__ = 'nodes.Draw'
    NODE_NAME = 'Counter'
    def __init__(self):
        super(Counter, self).__init__()
        self.add_input('in', color=(180, 80, 0))
        self.add_output('out')
        self.add_text_input('counter_color', 'Color', text='200,200,200', tab='attributes')
        self.set_color(*ncs.Draw)

class Constant(BaseNode):
    __identifier__ = 'nodes.Draw'
    NODE_NAME = 'Constant'
    def __init__(self):
        super(Constant, self).__init__()
        # self.add_input('in', color=(180, 80, 0))
        self.add_output('out')
        self.add_text_input('constant_color', 'Color', text='150,70,30', tab='attributes')
        self.add_text_input('width_', 'Width', text='1280', tab='attributes')
        self.add_text_input('height_', 'Height', text='720', tab='attributes')
        self.set_color(*ncs.Draw)

class Text(BaseNode):
    __identifier__ = 'nodes.Draw'
    NODE_NAME = 'Text'
    def __init__(self):
        super(Text, self).__init__()
        self.add_input('in', color=(180, 80, 0))
        self.add_output('out')
        self.add_text_input('text', 'Text', text='Optical core', tab='attributes')
        self.add_text_input('text_color_', 'Color', text='230,230,230', tab='attributes')
        self.add_text_input('px', 'Px', text='450', tab='attributes')
        self.add_text_input('py', 'Py', text='360', tab='attributes')
        self.add_text_input('size_', 'Size', text='2.0', tab='attributes')
        self.set_color(*ncs.Draw)

class Trajectory(BaseNode):
    __identifier__ = 'nodes.Draw'
    NODE_NAME = 'Trajectory'
    def __init__(self):
        super(Trajectory, self).__init__()
        self.add_input('in', color=(180, 80, 0))
        self.add_output('out')
        self.add_text_input('track_color', 'Color', text='10,20,220', tab='attributes')
        self.add_text_input('variable', 'Variable', text='track1', tab='attributes')
        self.add_text_input('length', 'Length', text='150', tab='attributes')
        self.add_text_input('size', 'Size', text='2', tab='attributes')
        self.set_color(*ncs.Draw)

class SelectionBuffer(BaseNode):
    __identifier__ = 'nodes.Draw'
    NODE_NAME = 'SelectionBuffer'
    def __init__(self):
        super(SelectionBuffer, self).__init__()
        self.add_input('in', color=(180, 80, 0))
        self.add_output('out')
        self.add_text_input('node_name', 'Name', text='Oflow Buffer', tab='attributes')
        # self.add_checkbox('lock', 'Lock', text='On/Off', state=False, tab='attributes')
        self.set_color(*ncs.Draw)

class Blur(BaseNode):
    __identifier__ = 'nodes.Filter'
    NODE_NAME = 'Blur'
    def __init__(self):
        super(Blur, self).__init__()
        self.add_input('in', color=(180, 80, 0))
        self.add_output('out')
        self.add_text_input('blur_size', 'Size', text='10', tab='attributes')
        self.set_color(*ncs.Filter)

class Sharpen(BaseNode):
    __identifier__ = 'nodes.Filter'
    NODE_NAME = 'Sharpen'
    def __init__(self):
        super(Sharpen, self).__init__()
        self.add_input('in', color=(180, 80, 0))
        self.add_output('out')
        self.add_text_input('size', 'Size', text='5', tab='attributes')
        self.set_color(*ncs.Filter)

class EdgeDetection(BaseNode):
    __identifier__ = 'nodes.Filter'
    NODE_NAME = 'EdgeDetection'
    def __init__(self):
        super(EdgeDetection, self).__init__()
        self.add_input('in', color=(180, 80, 0))
        self.add_output('out')
        self.add_text_input('minVal', 'Min Val', text='100', tab='attributes')
        self.add_text_input('maxVal', 'Max Val', text='200', tab='attributes')
        self.set_color(*ncs.Filter)

class Move(BaseNode):
    __identifier__ = 'nodes.Transform'
    NODE_NAME = 'Move'
    def __init__(self):
        super(Move, self).__init__()
        self.add_input('in', color=(180, 80, 0))
        self.add_output('out')
        self.add_text_input('movex', 'Move X', text='0', tab='attributes')
        self.add_text_input('movey', 'Move Y', text='0', tab='attributes')
        self.add_text_input('variable', 'Variable', text='track1', tab='attributes')
        self.set_color(*ncs.Transform)

class Resize(BaseNode):
    __identifier__ = 'nodes.Transform'
    NODE_NAME = 'Resize'
    def __init__(self):
        super(Resize, self).__init__()
        self.add_input('in', color=(180, 80, 0))
        self.add_output('out')
        self.add_text_input('resize', 'Size', text='75', tab='attributes')
        self.create_property('label_resize', 'Resize', widget_type=NODE_PROP_QLABEL)
        self.create_property('resize_x', 75, range=(10, 200), widget_type=NODE_PROP_SLIDER)
        self.set_color(*ncs.Transform)

class Gamma(BaseNode):
    __identifier__ = 'nodes.Grade'
    NODE_NAME = 'Gamma'
    def __init__(self):
        super(Gamma, self).__init__()
        self.add_input('in', color=(180, 80, 0))
        self.add_output('out')
        self.add_text_input('gamma', 'Gamma', text='0.5', tab='attributes')
        self.set_color(*ncs.Grade)

class Brightness(BaseNode):
    __identifier__ = 'nodes.Grade'
    NODE_NAME = 'Brightness'
    def __init__(self):
        super(Brightness, self).__init__()
        self.add_input('in', color=(180, 80, 0))
        self.add_output('out')
        self.add_text_input('brightness', 'Brightness', text='50', tab='attributes')
        self.set_color(*ncs.Grade)

class Saturation(BaseNode):
    __identifier__ = 'nodes.Grade'
    NODE_NAME = 'Saturation'
    def __init__(self):
        super(Saturation, self).__init__()
        self.add_input('in', color=(180, 80, 0))
        self.add_output('out')
        self.add_text_input('saturation', 'Saturation', text='1.2', tab='attributes')
        self.set_color(*ncs.Grade)

class GRAY2BGR(BaseNode):
    __identifier__ = 'nodes.Grade'
    NODE_NAME = 'GRAY2BGR'
    def __init__(self):
        super(GRAY2BGR, self).__init__()
        self.add_checkbox('invert', 'Invert', text='BGR2GRAY', state=False, tab='attributes')
        self.add_input('in', color=(180, 80, 0))
        self.add_output('out')
        self.set_color(*ncs.Grade)

