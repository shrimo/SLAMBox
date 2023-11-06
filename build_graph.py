#!/usr/bin/python3.10
"""
Building and execution of a 
graph using a script from the graph editor
"""
import solvers
from config import HOST, PORT, RECV_SIZE, VERSION, DATE


def build() -> None:
    print("SLAM box. Version: " + VERSION + DATE)

    cc = solvers.Color()
    VERSION_COLOR = str(cc.viva_magenta)[1:-1]
    TEXT_COLOR = str(cc.white)[1:-1]
    TEST_VERSION_SYSTEM = "SLAM box. Version: " + VERSION

    # default node graph for example
    default: ScriptType = [
        {
            "id": "0x7f6520f69fc0",
            "type": "Viewer",
            "custom": {"node_name": "Viewport", "disabled": False},
            "out": [],
            "in": ["0x7f6520f6b310"],
        },
        {
            "id": "0x7f6520f6ad10",
            "type": "Constant",
            "custom": {
                "constant_color": VERSION_COLOR,
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
                "text": TEST_VERSION_SYSTEM,
                "text_color_": TEXT_COLOR,
                "px": "220",
                "py": "370",
                "size_": "2.0",
                "disabled": False,
            },
            "out": ["0x7f6520f69fc0"],
            "in": ["0x7f6520f6ad10"],
        },
    ]

    graph = solvers.GraphBuilder(default, HOST, PORT, RECV_SIZE)

    try:
        graph.run()
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        print("Exit")


if __name__ == "__main__":
    build()
