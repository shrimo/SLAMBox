"""
Building and execution of a node graph(single-stream broadcasting).

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

# Define data types for the node graph script and for the node itself.
NodeType = Dict[Any, Any]
ScriptType = List[NodeType]
RoiType = Tuple[Any, Any, Any, Any]  # type for region of interest


class GraphBuilderFlask:
    """Building and execution of a node graph."""

    def __init__(self, script: ScriptType) -> None:
        self.buffer = solvers.DataBuffer()
        self.graph = solvers.build_rooted_graph(script, self.buffer)
        self.app = Flask(__name__)

        @self.app.route("/")
        def index():
            return render_template("index.html")

        @self.app.route("/video_feed")
        def video_feed():
            return self.get_video()

        @self.app.route("/json", methods=["POST"])
        def receive_json():
            data = request.get_json()
            self.execution_controller(data)
            return f"Video server received script"

        @self.app.route("/selected_area", methods=["POST"])
        def selected_area():
            data = request.get_json()
            start_x = int(data["start_x"])
            start_y = int(data["start_y"])
            end_x = int(data["end_x"])
            end_y = int(data["end_y"])
            print(f"-> get roi: {data}")
            # self.graph.get_roi_from_flask((start_x, start_y, end_x, end_y))
            return jsonify({"message": "data received"})

    def get_video(self):
        def generate_frames():
            while True:
                frame = self.graph.show_frame()
                ret, buffer = cv2.imencode(".jpg", frame)
                frame = buffer.tobytes()
                yield (
                    b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )

        return Response(
            generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
        )

    def run(self) -> None:
        """The main loop, processing the node execution script tree"""
        # self.app.run(host='192.168.88.253', debug=True)
        self.app.run(debug=True)

    def execution_controller(self, input_script: NodeType) -> None:
        """Controller for building a graph of nodes and control parameter updates"""
        match input_script["command"]:
            case "action":
                self.script = input_script["script"]
                self.graph = solvers.build_rooted_graph(self.script, self.buffer)
            case "update":
                if solvers.scripts_comparison(input_script["script"], self.script):
                    self.graph_update(self.graph, input_script["script"])
            case "stop":
                # cv2.destroyAllWindows()
                sys.exit(0)

    def graph_update(
        self, graph: solvers.WebStreaming, data_update: ScriptType
    ) -> None:
        """Updating node graph in real time"""
        if graph.get_input():
            for node in graph.get_input():
                if node.get_input():
                    node_update = solvers.find_node_by_attr(data_update, node.id_, "id")
                    if node_update is None:
                        return False
                    node.update(node_update["custom"])
                self.graph_update(node, data_update)
        return None

    def __del__(self) -> None:
        """Closing video capture and window"""
        print("GraphBuilder close")
