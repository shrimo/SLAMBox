"""
Graph Factory.
A set of functions for building 
a node graph based on script.
"""
import sys
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import numpy as np
from cv2 import destroyAllWindows # pylint: disable=E0611

from boxes import RootNode, plugins

# Define data types for the node graph script and for the node itself.
NodeType = Dict[Any, Any]
ScriptType = List[NodeType]
ActionScriptType = Dict[str, Any]
RoiType = Tuple[Any, Any, Any, Any]  # type for region of interest

PLUGINS = plugins.PluginRegistration()


@dataclass
class DataBuffer:
    """Class, buffer for exchanging data between nodes"""

    switch: bool = False
    roi: RoiType = (np.int64(0), np.int64(0), np.int64(0), np.int64(0))
    metadata: Dict[Any, Any] = field(default_factory=dict)
    variable: Dict[Any, Any] = field(default_factory=dict)


class GraphBuilderTemplate:
    """General class for builders"""

    def __init__(self, script: ActionScriptType, root_node: str):
        """Attributes for an inherited class"""
        self.buffer = DataBuffer()
        self.script = script["script"]
        self.root_node = root_node
        self.graph = build_rooted_graph(self.script, self.root_node, self.buffer)
        self.controller_dict: ActionScriptType = {
            "action": self.action,
            "update": self.update,
            "stop": self.stop,
            "stop_flask": self.stop_flask,
        }

    def execution_controller(self, input_script: ActionScriptType) -> None:
        """Controller for building a graph of nodes and control parameter updates"""
        self.controller_dict[str(input_script["command"])](input_script)

    def graph_update(self, graph: RootNode, data_update: ScriptType) -> None:
        """Updating node graph in real time"""
        if graph.get_input():
            for node in graph.get_input():
                if node.get_input():
                    node_update = find_node_by_attr(data_update, node.id_, "id")
                    if node_update is None:
                        continue
                    node.update(node_update["custom"])
                self.graph_update(node, data_update)

    def action(self, input_script: ActionScriptType) -> None:
        """Method for initially starting the script"""
        self.script = input_script["script"]
        self.graph = build_rooted_graph(self.script, self.root_node, self.buffer)

    def update(self, input_script: ActionScriptType) -> None:
        """The method starts a comparison of the working
        script and the one received from the client;
        If the composition of nodes in the graph has not changed,
        we update the state of the node parameters.
        """
        if scripts_comparison(input_script["script"], self.script):
            self.graph_update(self.graph, input_script["script"])

    def stop(self, input_script: ActionScriptType):
        """Shutting down and exiting node graph execution"""
        if "stop" in input_script["command"]:
            destroyAllWindows()
            sys.exit(0)

    def stop_flask(self, input_script: ActionScriptType):
        """Shutting down and exiting node graph execution"""
        if "stop_flask" in input_script["command"]:
            sys.exit(0)


def find_node_by_attr(nodes: ScriptType, target: str, attribute: str) -> NodeType:
    """get node by id or type attribute"""
    return next(node for node in nodes if node[attribute] == target)


def get_object_by_script(
    node: NodeType, root_node: NodeType, buffer: DataBuffer
) -> RootNode:
    """Declare an object by type node"""
    node_object = PLUGINS.get_plugin(node["type"])
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


def build_node_dict(
    script: ScriptType, root_node: NodeType, buffer: DataBuffer
) -> NodeType:
    """Create dictionary and adding objects to the dictionary"""

    node_dict: NodeType = defaultdict(lambda: {"node": None, "in": []})
    for node in script:
        node_id = node["id"]
        node_dict[node_id]["node"] = get_object_by_script(node, root_node, buffer)
        node_dict[node_id]["in"] = node["in"]
    return node_dict


def connection_nodes(node_dict: NodeType, root_node: NodeType) -> RootNode:
    """We connect the inputs of nodes
    with their outputs of related nodes."""
    for host_node in node_dict.values():
        for input_node_id in host_node["in"]:
            host_node["node"].add_input(node_dict[input_node_id]["node"])
    return node_dict[root_node["id"]]["node"]


def build_rooted_graph(
    script: ScriptType, root_name: str, buffer: DataBuffer
) -> RootNode:
    """rooted graph is a graph in which one
    node has been distinguished as the root"""

    # Get root node from which graph execution begins
    root_node = find_node_by_attr(script, root_name, "type")
    clear_script = cleaning_unplugged_nodes(script, root_node, [root_node])
    nodes_dict = build_node_dict(clear_script, root_node, buffer)
    return connection_nodes(nodes_dict, root_node)


def scripts_comparison(script_a: ScriptType, script_b: ScriptType) -> bool:
    """comparison of a running script with an updated script"""
    return Counter([x["id"] for x in script_a]) == Counter([x["id"] for x in script_b])
