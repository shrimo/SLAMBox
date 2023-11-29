#!/usr/bin/python3.10
"""
Building and execution of a 
graph using a script from the graph editor
"""
import sys
from typing import List, Dict, Any
from solvers import pipeline, utility
from config import host, port, recv_size, version, date

NodeType = Dict[Any, Any]
ScriptType = List[NodeType]


def build() -> None:
    """Default script start"""
    print("SLAM box version: " + version + date)

    cc = utility.Color()
    graph_type: str = "OpenCV"
    if len(sys.argv) > 1:
        graph_type = sys.argv[1]

    # Settings for initializing the startup script
    start_dict: dict = {
        "OpenCV": {
            "type": "Viewer",
            "name": "Viewport",
            "version_color": str(cc.persimmon)[1:-1],
            "text_color": str(cc.white)[1:-1],
            "test_version_system": f"SLAM box. version: {version}",
            "graph": pipeline.GraphBuilder,
            "px": "220",
        },
        "Flask": {
            "type": "WebStreaming",
            "name": "Viewport",
            "version_color": str(cc.gray)[1:-1],
            "text_color": str(cc.white)[1:-1],
            "test_version_system": f"SLAMBOX (Flask) version: {version}",
            "graph": pipeline.GraphBuilderFlask,
            "px": "140",
        },
        "FlaskMS": {
            "type": "WebStreaming",
            "name": "Viewport",
            "version_color": str(cc.gray)[1:-1],
            "text_color": str(cc.white)[1:-1],
            "test_version_system": f"SLAMBOX (FlaskMS) version: {version}",
            "graph": pipeline.GraphStreaming,
            "px": "100",
        },
    }

    graph_dict = start_dict[graph_type]

    # default (startup script) node graph for example
    default: ScriptType = {
        "command": "action",
        "script": [
            {
                "id": "0x7f6520f69fc0",
                "type": graph_dict["type"],
                "custom": {"node_name": graph_dict["name"], "disabled": False},
                "out": [],
                "in": ["0x7f6520f6b310"],
            },
            {
                "id": "0x7f6520f6ad10",
                "type": "Constant",
                "custom": {
                    "constant_color": graph_dict["version_color"],
                    "width_": "1280",
                    "height_": "720",
                    "disabled": False,
                },
                "out": ["0x7f6520f6b310"],
                "in": [],
            },
            {
                "id": "0x7f6520f6b310",
                "type": "Text",
                "custom": {
                    "text": graph_dict["test_version_system"],
                    "text_color_": graph_dict["text_color"],
                    "px": graph_dict["px"],
                    "py": "370",
                    "size_": "2.0",
                    "disabled": False,
                },
                "out": ["0x7f6520f69fc0"],
                "in": ["0x7f6520f6ad10"],
            },
        ],
    }

    if "OpenCV" in graph_type:
        graph = graph_dict["graph"](default, host, port, recv_size)
    else:
        graph = graph_dict["graph"](default)

    try:
        graph.run()
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        print("Exit")


if __name__ == "__main__":
    build()
