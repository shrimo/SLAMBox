#!/usr/bin/python3.10
"""
Building and execution of a 
graph using a script from the graph editor
"""
import sys
from typing import List, Dict, Any
from boxes import pipeline, utility
from config import host, port, recv_size, version, date

NodeType = Dict[Any, Any]
ScriptType = List[NodeType]
ActionScriptType = Dict[str, str | ScriptType]


def build() -> None:
    """Default script setup (OpenCV, Flask, FlaskMS)"""

    cc = utility.Color()

    # Settings for initializing the startup script
    settings_dict: dict = {
        "OpenCV": {
            "type": "Viewer",
            "name": "Viewport",
            "version_color": utility.rgb2bgr(cc.mocha_mousse),
            "text_color": cc.white,
            "title_text": f"SLAM box. version: {version}",
            "builder": pipeline.GraphBuilder,
            "px": "220"
        },
        "Flask": {
            "type": "WebStreaming",
            "name": "Viewport",
            "version_color": cc.gray,
            "text_color": cc.white,
            "title_text": f"SLAMBOX (Flask) version: {version}",
            "builder": pipeline.GraphBuilderFlask,
            "px": "140"
        },
        "FlaskMS": {
            "type": "WebStreaming",
            "name": "Viewport",
            "version_color": cc.gray,
            "text_color": cc.white,
            "title_text": f"SLAMBOX (FlaskMS) version: {version}",
            "builder": pipeline.GraphBuilderFlaskMS,
            "px": "100"
        },
    }

    graph_type: str = "OpenCV"
    if (
        len(sys.argv) > 1
        and sys.argv[1] in list(settings_dict.keys())
    ):
        graph_type = sys.argv[1]

    graph_dict = settings_dict[graph_type]

    # default (startup script) node graph for example
    default: ActionScriptType = {
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
                    "text": graph_dict["title_text"],
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

    print(f'SLAM box version: {version} {graph_type} {date}')
    graph = graph_dict["builder"](default)
    try:
        graph.run()
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        print("Exit")


if __name__ == "__main__":
    build()
