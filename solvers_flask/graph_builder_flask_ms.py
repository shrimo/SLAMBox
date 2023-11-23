"""
Building and execution of a node graph(isolated streaming).

Main classes that describe the connection between the 
server and the graph editor and the construction and 
execution of a node graph. Software platform for accessing
video stream from camera or from video file, functions and methods
for processing and analyzing a optical stream.

Static type version.
"""
import sys
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from flask import Flask, Response, request, jsonify, render_template
import numpy as np
import cv2
import solvers_flask as solvers

# from base_camera import BaseCamera

# Define data types for the node graph script and for the node itself.
NodeType = Dict[Any, Any]
ScriptType = List[NodeType]
ActionScriptType = Dict[str, Any]
RoiType = Tuple[Any, Any, Any, Any]  # type for region of interest


@dataclass
class DataBuffer:
    """Common data exchange buffer"""

    switch: bool = False
    roi: RoiType = (np.int64(0), np.int64(0), np.int64(0), np.int64(0))
    metadata: Dict[Any, Any] = field(default_factory=dict)
    variable: Dict[Any, Any] = field(default_factory=dict)


def find_node_by_attr(nodes: ScriptType, target: str, attribute: str) -> NodeType:
    """get node by id or type attribute"""
    return next(node for node in nodes if node[attribute] == target)


def get_object_by_script(
    node: NodeType, root_node: NodeType, buffer: DataBuffer
) -> solvers.Node:
    """Declare an object by type node"""
    node_object = getattr(solvers, node["type"])
    return node_object(
        node["type"],
        node["id"],
        node["custom"],
        root_node["custom"]["node_name"],
        buffer,
    )


def cleaning_unplugged_nodes(
    script: ScriptType, processed_node: NodeType, clear_script: ScriptType
) -> ScriptType:
    """Clearing the script of unlinked nodes:
    if a node does not have an incoming node attribute,
    this node is not included in the script.
    """
    for in_node_id in processed_node["in"]:
        in_node = find_node_by_attr(script, in_node_id, "id")
        clear_script.append(in_node)
        if in_node["in"]:
            cleaning_unplugged_nodes(script, in_node, clear_script)
    return clear_script


def build_node_graph(
    script: ScriptType, root_node: NodeType, buffer: DataBuffer
) -> solvers.WebStreaming:
    """Create dictionary and adding objects to the dictionary"""

    node_dict: NodeType = defaultdict(lambda: {"node": None, "in": []})
    for node in script:
        node_id = node["id"]
        node_dict[node_id]["node"] = get_object_by_script(node, root_node, buffer)
        node_dict[node_id]["in"] = node["in"]
    # Nodes connection
    for host_node in node_dict.values():
        for input_node_id in host_node["in"]:
            host_node["node"].add_input(node_dict[input_node_id]["node"])
    # Getting Viewer node from dictionary and return
    out = node_dict[root_node["id"]]["node"]
    return out


def build_rooted_graph(script: ScriptType, buffer: DataBuffer) -> solvers.WebStreaming:
    """rooted graph is a graph in which one
    node has been distinguished as the root"""

    # Get root node from which graph execution begins
    root_node = find_node_by_attr(script, "WebStreaming", "type")
    # Clearing the script of unlinked nodes
    clear_script = cleaning_unplugged_nodes(script, root_node, [root_node])
    return build_node_graph(clear_script, root_node, buffer)


class GraphBuilderFlaskMS:
    """Building and execution of a node graph"""

    def __init__(self, script: ActionScriptType) -> None:
        self.buffer = DataBuffer()
        self.script = script["script"]
        self.graph = build_rooted_graph(script["script"], self.buffer)

    def scripts_comparison(self, script: ScriptType) -> bool:
        """comparison of a running script with an updated script"""
        return Counter([x["id"] for x in script]) == Counter(
            [x["id"] for x in self.script]
        )

    def execution_controller(self, input_script: NodeType) -> None:
        """Controller for building a graph of nodes and control parameter updates"""
        match input_script["command"]:
            case "action":
                self.script = input_script["script"]
                self.graph = build_rooted_graph(self.script, self.buffer)
            case "update":
                if self.scripts_comparison(input_script["script"]):
                    self.graph_update(self.graph, input_script["script"])
            case "stop":
                #     cv2.destroyAllWindows()
                sys.exit(0)

    def graph_update(
        self, graph: solvers.WebStreaming, data_update: ScriptType
    ) -> None:
        """Updating node graph in real time"""
        if graph.get_input():
            for node in graph.get_input():
                if node.get_input():
                    node_update = find_node_by_attr(data_update, node.id_, "id")
                    if node_update is None:
                        return False
                    node.update(node_update["custom"])
                self.graph_update(node, data_update)
        return None


class GraphStreaming:
    """Launching and updating streaming graph"""

    def __init__(self, script: ScriptType) -> None:
        self.script = script
        self.app = Flask(__name__)
        self.update = False

        @self.app.route("/")
        def index():
            return render_template("index.html")

        @self.app.route("/video_feed")
        def video_feed():
            return Response(
                self.generate_frames(solvers.GraphBuilderFlaskMS(self.script)),
                mimetype="multipart/x-mixed-replace; boundary=frame",
            )

        @self.app.route("/json", methods=["POST"])
        def receive_json():
            self.script = request.get_json()
            self.update = True
            return f"Video server received script"

        @self.app.route("/selected_area", methods=["POST"])
        def selected_area():
            data = request.get_json()
            start_x = int(data["start_x"])
            start_y = int(data["start_y"])
            end_x = int(data["end_x"])
            end_y = int(data["end_y"])
            print(f"-> get roi: {data}")
            return jsonify({"message": "data received"})

    def generate_frames(self, graph_builder):
        while True:
            frame = graph_builder.graph.show_frame()
            if self.update:
                graph_builder.execution_controller(self.script)
                self.update = False
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    def run(self) -> None:
        """The main loop, processing the node execution script tree"""
        # self.app.run(host='192.168.88.253', debug=True)
        self.app.run(debug=True)

    def __del__(self) -> None:
        """Closing video capture and window"""
        print("GraphBuilder close")
