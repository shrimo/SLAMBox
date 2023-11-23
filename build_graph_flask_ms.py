#!/usr/bin/python3.10
"""
Building and execution of a 
graph using a script from the graph editor
"""
from typing import List, Dict, Any
from solvers_flask import GraphStreaming, Color
from config import version, date

NodeType = Dict[Any, Any]
ScriptType = List[NodeType]


def build() -> None:
    """Default script start"""
    print("SLAMBOX (flask) version: " + version + date)

    cc = Color()
    version_color = str(cc.gray)[1:-1]
    text_color = str(cc.white)[1:-1]
    test_version_system = "SLAMBOX (flask) version: " + version

    # default node graph for example
    default: ScriptType = {
        "command": "action",
        "script": [
            {
                "id": "0x7f6520f69fc0",
                "type": "WebStreaming",
                "custom": {"node_name": "WebStreaming", "disabled": False},
                "out": [],
                "in": ["0x7f6520f6b310"],
            },
            {
                "id": "0x7f6520f6ad10",
                "type": "Constant",
                "custom": {
                    "constant_color": version_color,
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
                    "text": test_version_system,
                    "text_color_": text_color,
                    "px": "140",
                    "py": "370",
                    "size_": "2.0",
                    "disabled": False,
                },
                "out": ["0x7f6520f69fc0"],
                "in": ["0x7f6520f6ad10"],
            },
        ],
    }

    graph = GraphStreaming(default)

    try:
        graph.run()
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        print("Exit")


if __name__ == "__main__":
    build()