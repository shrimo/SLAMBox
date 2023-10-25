#!/usr/bin/python3
"""
Optical core is a software platform for accessing video stream
from camera or from video file, functions and methods
for processing and analyzing a optical stream.
"""
import sys
from typing import List, Dict, Any
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import socket
import pickle
import selectors
import cv2
import solvers
from config import HOST, PORT, RECV_SIZE, VERSION

# Define data types for the node graph script and for the node itself.
NodeType = Dict[Any, Any]
ScriptType = List[NodeType]

# Selector for communication with clients
sel = selectors.DefaultSelector()

@dataclass
class DataBuffer:
    """ Common data exchange buffer """
    switch = False
    roi = None
    metadata = None
    variable: Dict[Any, Any] = field(default_factory=dict)

def move_node_to_end(script: ScriptType, node_type: str) -> ScriptType:
    """ Move node to end of list """
    matching_nodes = [node for node in script if node_type in node['type']]
    non_matching_nodes = [node for node in script if node_type not in node['type']]
    return non_matching_nodes + matching_nodes

def find_node_by_attr(nodes: ScriptType, target: str, attribute: str) -> NodeType:
    """ get node by id or type attribute """
    return next(node for node in nodes if node[attribute] == target)

def get_object_by_script(node: NodeType, root_node: NodeType, buffer: DataBuffer) -> solvers.Node:
    """ Declare an object by type node """
    node_object = getattr(solvers, node['type'])
    return node_object(node['type'], node['id'],
        node['custom'], root_node['custom']['node_name'], buffer)

def build_node_graph(script:ScriptType, root_node:NodeType,
    buffer: DataBuffer)-> solvers.base_nodes.Viewer:
    """ Create dictionary and Adding objects to the dictionary"""
    node_dict: NodeType = defaultdict(lambda: {'node': None, 'in': []})
    for node in script:
        node_id = node['id']
        node_dict[node_id]['node'] = get_object_by_script(node, root_node, buffer)
        node_dict[node_id]['in'] = node['in']
    # Nodes connection
    for host_node in node_dict.values():
        for input_node_id in host_node['in']:
            host_node['node'].add_input(node_dict[input_node_id]['node'])
    # Getting Viewer node from dictionary and return
    out = node_dict[root_node['id']]['node']
    return out

def build_rooted_graph(script: ScriptType, buffer: DataBuffer) -> solvers.base_nodes.Viewer:
    """rooted graph is a graph in which one
    node has been distinguished as the root"""
    aligned_script = move_node_to_end(script, 'Viewer')
    root_node = find_node_by_attr(aligned_script, 'Viewer', 'type')
    out = build_node_graph(aligned_script, root_node, buffer)
    return out

class Communication:
    """ Server for receiving data, non-blocking """
    def __init__(self, host:str, port:int) -> None:
        self.data_change = None
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen()
        print('Listening on', host, port)
        sock.setblocking(False)
        sel.register(sock, selectors.EVENT_READ, data=None)

    def accept_wrapper(self, sock) -> None:
        """ Register an event """
        conn, addr = sock.accept()
        print('Accepted connection from ', addr)
        conn.setblocking(False)
        events = selectors.EVENT_READ
        sel.register(conn, events, data=addr)

    def service_connection(self, key, mask) -> None:
        """ Receive and unpack data """
        sock = key.fileobj
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(RECV_SIZE)
            if recv_data:
                self.data_change = pickle.loads(recv_data)
            else:
                print("Closing connection")
                sel.unregister(sock)
                sock.close()

class OpticalCore:
    """ Running the Main Loop ('run' method) Filling the Node script with objects """
    def __init__(self, script: ScriptType) -> None:
        self.buffer = DataBuffer()
        self.script = script
        self.graph = build_rooted_graph(script, self.buffer)
        self.com = Communication(HOST, PORT)

    def run(self) -> None:
        """ The main loop, processing the node execution script tree """
        while True:
            if not self.graph.show_frame():
                break

            events = sel.select(timeout=0)
            for key, mask in events:
                if key.data is None:
                    self.com.accept_wrapper(key.fileobj)
                else:
                    self.com.service_connection(key, mask)
                    if self.com.data_change:
                        self.execution_controller(self.com.data_change)
                        self.com.data_change = None

            # Playback control
            p_key:int = cv2.waitKey(1)
            if p_key == ord('s'):
                self.graph.stop()
            elif p_key == ord('p'):
                cv2.waitKey(-1)
            elif p_key == ord('q') or p_key == 27:
                if self.graph.stop():
                    break

    def scripts_comparison(self, script: ScriptType) -> bool:
        """ comparison of a running script with an updated script """
        return Counter([x['id'] for x in script]) == Counter([x['id'] for x in self.script])

    def execution_controller(self, input_script:NodeType) -> None:
        """ Controller for building a graph of nodes and control parameter updates """
        match input_script['command']:
            case 'action':
                self.script = input_script['script']
                self.graph = build_rooted_graph(self.script, self.buffer)
            case 'update':
                if self.scripts_comparison(input_script['script']):
                    self.graph_update(self.graph, input_script['script'])
            case 'stop':
                cv2.destroyAllWindows()
                sys.exit(0)

    def graph_update(self, graph:solvers.base_nodes.Viewer, data_update:ScriptType) -> None:
        """ Updating node graph in real time """
        if graph.get_input():
            for node in graph.get_input():
                if node.get_input():
                    node_update = find_node_by_attr(data_update, node.id_, 'id')
                    if node_update is None:
                        return False
                    node.update(node_update['custom'])
                self.graph_update(node, data_update)
        return None

    def __del__(self) -> None:
        """ Closing video capture and window """
        print('Optical Core Close')
        # cv2.destroyAllWindows()


if __name__ == '__main__':
    print('opencv: '+solvers.cv2.__version__)
    print('open3d: '+solvers.slam_box.o3d.__version__)
    print('numpy: '+solvers.np.__version__)
    cc = solvers.Color()
    VERSION_COLOR = str(cc.burnt_sienna)[1:-1]
    TEXT_COLOR = str(cc.white)[1:-1]
    TEST_VERSION_SYSTEM = 'SLAM box. Version: ' + VERSION

    default: ScriptType = [{'id': '0x7f6520f69fc0', 'type': 'Viewer', 'custom':
    {'node_name': 'Viewport', 'disabled': False},
    'out': [], 'in': ['0x7f6520f6b310']},
    {'id': '0x7f6520f6ad10', 'type': 'Constant', 'custom':
    {'constant_color': VERSION_COLOR, 'width_': '1280', 'height_': '720', 'disabled': False},
    'out': ['0x7f6520f6b310'], 'in': []}, {'id': '0x7f6520f6b310', 'type': 'Text', 'custom':
    {'text': TEST_VERSION_SYSTEM, 'text_color_': TEXT_COLOR,
    'px': '230', 'py': '370', 'size_': '2.0', 'disabled': False},
    'out': ['0x7f6520f69fc0'], 'in': ['0x7f6520f6ad10']}]

    ocore = OpticalCore(default)
    try:
        ocore.run()
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()
        print('Exit')
