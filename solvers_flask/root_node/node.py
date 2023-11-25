""" Common nodes for building a pipeline """

import numpy as np


class Node:
    """Root node that all nodes"""

    def __init__(self, type_, id_, param, window_name, buffer):
        self.buffer = buffer
        self.empty_roi = (np.int64(), np.int64(), np.int64(), np.int64())
        self.type_ = type_
        self.id_ = id_
        self.window_name = window_name
        self.input_nodes = []
        self.param = param
        self.disabled = param["disabled"]

    def add_input(self, node):
        self.input_nodes.append(node)

    def get_input(self):
        return self.input_nodes

    def get_frame(self, port_number):
        """Port number - node input number"""
        return self.input_nodes[port_number].out_frame()

    def color_reversed(self, x):
        return (x[2], x[1], x[0])
