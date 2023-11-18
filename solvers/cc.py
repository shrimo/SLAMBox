""" Color correction nodes for work with color and light """

import cv2
import numpy as np
from solvers.root_nodes import Node
from solvers.misc import get_tuple

class GRAY2BGR(Node):
    """ Gray to color """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invert = self.param['invert']

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print('GRAY2BGR stop')
            return None
        if self.invert:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            return cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    def update(self, param):
        self.invert = param['invert']

class Gamma(Node):
    """ Gamma correction """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gamma = 1/float(self.param['gamma'])
        self.lookUpTable = np.empty((1,256), np.uint8)

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print('Gamma stop')
            return None
        if self.disabled: return frame
        for i in range(256):
            self.lookUpTable[0,i] = np.clip(pow(i / 255.0, self.gamma) * 255.0, 0, 255)
        return cv2.LUT(frame, self.lookUpTable)

    def update(self, param):
        self.disabled = param['disabled']
        self.gamma = 1/float(param['gamma'])

class Brightness(Node):
    """ Brightness """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.brightness = int(self.param['brightness'])

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print('Brightness stop')
            return None
        if self.disabled: return frame
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.add(v, self.brightness)
        v[v > 255] = 255
        v[v < 0] = 0
        final_hsv = cv2.merge((h, s, v))
        return cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

    def update(self, param):
        self.disabled = param['disabled']
        self.brightness = int(param['brightness'])

class CLAHE(Node):
    """ CLAHE (Contrast Limited Adaptive Histogram Equalization) """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clipLimit = float(self.param['clipLimit'])
        self.tileGridSize = get_tuple(self.param['tileGridSize'])
        self.clahe = cv2.createCLAHE(self.clipLimit, self.tileGridSize)

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print('CLAHE stop')
            return None
        if self.disabled: return frame
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l2 = self.clahe.apply(l)
        lab = cv2.merge((l2,a,b))
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    def update(self, param):
        self.disabled = param['disabled']
        self.clipLimit = float(param['clipLimit'])
        self.tileGridSize = get_tuple(param['tileGridSize'])
        self.clahe = cv2.createCLAHE(self.clipLimit, self.tileGridSize)

class Saturation(Node):
    """ Color Saturation Control """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.saturation = float(self.param['saturation'])

    def out_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print('Saturation stop')
            return None
        if self.disabled: return frame
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)        
        hsv[...,1] = hsv[...,1]*self.saturation
        return cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)

    def update(self, param):
        self.disabled = param['disabled']
        self.saturation = float(param['saturation'])
