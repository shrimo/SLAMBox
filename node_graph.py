#!/usr/bin/python3

"""
GUI for video or image analysis and processing
Based on the NodeGraphQt a node graph UI framework
written in python that can be implemented and re-purposed
into applications supporting PySide2.
"""

import sys
import socket
import pickle
from Qt import QtCore, QtWidgets
from PySide2.QtGui import QPixmap

# Loading configuration data
import config as cfg

if cfg.NodeGraphQt not in sys.path:
    sys.path.append(cfg.NodeGraphQt)

from NodeGraphQt import NodeGraph, PropertiesBinWidget
import gui_lib as gui

def get_nodes():
    """ Get list of nodes object """
    node_list = []
    for node in dir(gui):
        obj = getattr(gui, node)
        if hasattr(obj, '__identifier__'):
            node_list.append(getattr(gui, node))
    return node_list

class NodeBased(NodeGraph):
    """ Node Based User Interface """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.show_about = QtWidgets.QLabel()
        self.properties_bin = PropertiesBinWidget(node_graph=self)
        self.properties_bin.setWindowFlags(QtCore.Qt.Tool)
        self.register_nodes(get_nodes())
        self.menu = self.get_context_menu('nodes')
        self.menu.add_command('Action', func=self.execute_script,
            node_type=None, node_class=gui.Viewer)
        self.menu.add_command('Node Info', func=self.node_info,
            node_type=None, node_class=gui.Read)
        self.menu.add_command('Stop', func=self.stop_server,
            node_type=None, node_class=gui.Viewer)
        self.menu.add_command('Show image', func=self.show_image,
            node_type=None, node_class=gui.Image)
        self.context_menu = self.get_context_menu('graph')
        self.context_menu.add_separator()
        self.context_menu.add_command('About', func=self.about, shortcut=None)
        self.node_double_clicked.connect(self.display_properties_bin)
        self.property_changed.connect(self.node_property_changed)
        self.act = False
        self.image_show = []

    def node_info(self):
        """ print node info """
        for node in self.all_nodes():
            print(node.properties())

    def about(self):
        """ Show about """
        self.show_about.setWindowTitle('About')
        self.show_about.setAlignment(QtCore.Qt.AlignCenter)
        self.show_about.setStyleSheet(cfg.CSS_STYLE)
        self.show_about.setText(str(cfg.NAME+
                                ' '+cfg.VERSION+
                                '\n'+cfg.DATE+
                                '\n'+cfg.SYSTEM))
        self.show_about.setFixedSize(500, 300)
        self.show_about.setWordWrap(True)
        self.show_about.show()

    def create_nodes(self):
        """ Сreating default nodes """
        node_a = self.create_node('nodes.Read.Read', name='Read', pos=(320, -150))
        node_b = self.create_node('nodes.Draw.FPS', name='FPS', pos=(320, 730))
        node_c = self.create_node('nodes.Viewer.Viewer', name='Viewer', pos=(320, 850))
        node_b.set_input(0, node_a.output(0))
        node_c.set_input(0, node_b.output(0))
        # ...

    def display_properties_bin(self):
        """ Show properties bin """
        if not self.properties_bin.isVisible():
            self.properties_bin.show()

    def show_image(self):
        """ Show content node image """
        self.image_show.clear()
        for node in self.all_nodes():
            if node.type_ in 'nodes.Read.Image':
                image_node = node.properties()['custom']
                pixmap = QPixmap(image_node['file'])
                self.image_show.append((QtWidgets.QLabel(), pixmap, image_node['file']))
        for image in self.image_show:
            image[0].setWindowTitle(image[2])
            image[0].setFixedSize(image[1].size())
            image[0].setPixmap(image[1])
            image[0].show()

    def node_by_id(self, nid, nodes):
        """ Return node by id """
        for node in nodes:
            if nid == node['id']:
                return node
        return False

    def node_property_changed(self):
        """ Updating node settings """
        if self.act:
            out_script = {'command':'update', 'script':self.buld_script()}
            self.script_transfer(out_script)

    def execute_script(self):
        """ Executing or Reloading a Node Graph """
        if self.act is False:
            self.act = True
        out_script = {'command':'action', 'script':self.buld_script()}
        self.script_transfer(out_script)

    def stop_server(self):
        """ Stopping and shutting down """
        out_script = {'command':'stop', 'script':None}
        self.script_transfer(out_script)
        print ('- Send a stop to server')

    def script_transfer(self, script):
        """ Sending node script by socket"""
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            soc.connect((cfg.HOST, cfg.PORT))
            script_serialization = pickle.dumps(script)
            soc.send(script_serialization)
        except socket.error as err:
            msg = (cfg.HOST, cfg.PORT, err)
            print(f"Error {msg[0]}:{msg[1]}. Exception is {msg[2]}")
        finally:
            print ('- Send script')
            soc.close()

    def clean_script(self, script):
        """ Finding and deleting nodes with empty outputs, except for the Viewer node """
        parent_node = None
        for node in script:
            if not node['out'] and not node['type'] in 'Viewer':
                for in_node in node['in']:
                    parent_node = self.node_by_id(in_node, script)
                    script.remove(node)
                    if node['id'] in parent_node['out']:
                        script.remove(parent_node)
                        parent_node['out'].remove(node['id'])
                        script.append(parent_node)
                return self.clean_script(script)
        return script

    def clean_script2(self, script):
        """ Finding and removing nodes with empty outputs and empty inputs """
        for node in script:
            if not node['in'] and not node['out']:
                script.remove(node)
            elif not node['out'] and 'Viewer' not in node['type']:
                script.remove(node)
        return script

    def buld_script(self):
        """ Preparing data for sending in a video core """
        export_nodes = []
        for node in self.all_nodes():
            output_node_id = []
            input_node_id = []
            node_type = node.properties()['type_'].split('.')[2]
            # Copying the entire dictionary
            node_custom = node.properties()['custom'].copy()
            # Adding key 'disabled' in dictionary
            node_custom['disabled'] = node.disabled()
            if node.connected_output_nodes():
                for node_connected in node.connected_output_nodes().items():
                    for multi in node_connected[1]:
                        output_node_id.append(multi.properties()['id'])
            if node.connected_input_nodes():
                for node_connected in node.connected_input_nodes().items():
                    for multi in node_connected[1]:
                        input_node_id.append(multi.properties()['id'])
            export_nodes.append({'id':node.id, 'type':node_type, 'custom':node_custom,
                                'out':output_node_id, 'in':input_node_id})

        # Clean and sending to video core
        script = self.clean_script2(export_nodes)
        # script = self.clean_script(self.clean_script2(export_nodes))
        # for node in script:
        #     print('type:',node['type'],',id:',node['id'],',out:',node['out'],',in',node['in'])

        # Writing to a file, for debugging
        # pickle.dump(script, open("default.oc", "wb"))
        # print('write default.oc')

        return script


if __name__ == '__main__':
    print(cfg.NAME, cfg.GUI)
    app = QtWidgets.QApplication([])
    node_based = NodeBased()
    node_based.create_nodes()
    node_based.widget.resize(500, 800)
    node_based.widget.move(1300, 100)
    node_based.widget.show()
    sys.exit(app.exec_())
    # app.exec_()
