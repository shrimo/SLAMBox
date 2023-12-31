"""
Building and execution of a node graph (OpenCV cv2.imshow()).

Main classes that describe the connection between the 
server and the graph editor and the construction and 
execution of a node graph. Software platform for accessing
video stream from camera or from video file, functions and methods
for processing and analyzing a optical stream.

Static type version.
"""
# import sys
from typing import List, Dict, Any
import socket
import pickle
import selectors
import numpy as np
import cv2
from boxes import pipeline

# Define data types for the node graph script and for the node itself.
NodeType = Dict[Any, Any]
ScriptType = List[NodeType]
ActionScriptType = Dict[str, Any]


class GraphCommunication:
    """Server for receiving data, non-blocking"""

    def __init__(
        self, host: str = "localhost", port: int = 50001, recv_size: int = 10240
    ) -> None:
        self.data_change: Dict[str, ScriptType] = {}
        self.recv_size = recv_size
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen()
        print(f"Listening on {host} {port}")
        sock.setblocking(False)
        # Selector for receiving data reception events
        self.selector = selectors.DefaultSelector()
        self.selector.register(sock, selectors.EVENT_READ, data=None)

    def accept_wrapper(self, sock) -> None:
        """Register an event"""
        conn, addr = sock.accept()
        print(f"Accepted connection from {addr}")
        conn.setblocking(False)
        events = selectors.EVENT_READ
        self.selector.register(conn, events, data=addr)

    def service_connection(self, key, mask) -> None:
        """Receive and unpack data"""
        sock = key.fileobj
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(self.recv_size)
            if recv_data:
                self.data_change = pickle.loads(recv_data)
            else:
                print("Closing connection")
                self.selector.unregister(sock)
                sock.close()


class GraphBuilder(pipeline.GraphBuilderTemplate):
    """Building and execution of a node graph.
    host: str = "localhost",
    port: int = 50001,
    recv_size: int = 10240,

    Attributes from template:
    self.script = script["script"]
    self.root_node = root_node
    """

    def __init__(
        self,
        script: ActionScriptType,
        host: str = "localhost",
        port: int = 50001,
        recv_size: int = 10240,
        root_node: str = "Viewer",
    ) -> None:
        super().__init__(script, root_node)
        self.com = GraphCommunication(host, port, recv_size)

    def run(self) -> None:
        """The main loop, processing the node execution script tree"""
        while True:
            if not self.graph.show_frame():
                break

            events = self.com.selector.select(timeout=0)
            for key, mask in events:
                if key.data is None:
                    self.com.accept_wrapper(key.fileobj)
                else:
                    self.com.service_connection(key, mask)
                    if self.com.data_change:
                        self.execution_controller(self.com.data_change)
                        self.com.data_change.clear()

            # Playback control
            p_key: int = cv2.waitKey(1)
            if p_key == ord("s"):
                self.graph.stop()
            elif p_key == ord("p"):
                cv2.waitKey(-1)
            elif p_key == ord("q") or p_key == 27:
                if self.graph.stop():
                    break

    def __del__(self) -> None:
        """Closing video capture and window"""
        self.com.selector.close()
        print("GraphBuilder close")
