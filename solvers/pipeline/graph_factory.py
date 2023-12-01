"""
Graph Factory.
A set of functions for building 
a node graph based on script.
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import numpy as np
from solvers import RootNode, solver_nodes

# Define data types for the node graph script and for the node itself.
NodeType = Dict[Any, Any]
ScriptType = List[NodeType]
ActionScriptType = Dict[str, Any]
RoiType = Tuple[Any, Any, Any, Any]  # type for region of interest


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
        self.buffer = DataBuffer()
        self.script = script["script"]
        self.root_node = root_node
        self.graph = build_rooted_graph(self.script, self.root_node, self.buffer)

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
        return None

    def execution_controller(
        self, root_name: str, input_script: ActionScriptType
    ) -> None:
        """Controller for building a graph of nodes and control parameter updates"""
        match input_script["command"]:
            case "action":
                self.script = input_script["script"]
                self.graph = build_rooted_graph(self.script, root_name, self.buffer)
            case "update":
                if scripts_comparison(input_script["script"], self.script):
                    self.graph_update(self.graph, input_script["script"])
            case "stop":
                cv2.destroyAllWindows()
                sys.exit(0)


def find_node_by_attr(nodes: ScriptType, target: str, attribute: str) -> NodeType:
    """get node by id or type attribute"""
    return next(node for node in nodes if node[attribute] == target)


def get_object_by_script(
    node: NodeType, root_node: NodeType, buffer: DataBuffer
) -> RootNode:
    """Declare an object by type node"""
    node_object = getattr(solver_nodes, node["type"])
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
) -> RootNode:
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


def build_rooted_graph(
    script: ScriptType, root_name: str, buffer: DataBuffer
) -> RootNode:
    """rooted graph is a graph in which one
    node has been distinguished as the root"""

    # Get root node from which graph execution begins
    root_node = find_node_by_attr(script, root_name, "type")
    # Clearing the script of unlinked nodes
    clear_script = cleaning_unplugged_nodes(script, root_node, [root_node])
    return build_node_graph(clear_script, root_node, buffer)


def scripts_comparison(script_a: ScriptType, script_b: ScriptType) -> bool:
    """comparison of a running script with an updated script"""
    return Counter([x["id"] for x in script_a]) == Counter([x["id"] for x in script_b])
