echo "python$1"
echo Start node graph core and GUI
python$1 build_graph.py & python$1 node_graph.py
wait