# General settings for launching the program
import platform

host: str = "localhost"
port: int = 50001
recv_size: int = 10240
name: str = "SLAM Box"
version: str = "0.6.9"
system: str = platform.system()
gui: str = "Node-based UI"
description: str = "Computer Vision Node Graph Editor"
date: str = " (Wed Nov 29 05:12:21 PM EET 2023)"
nodegraphqt: str = "./NodeGraphQt/"
css_style: str = "QLabel {background-color: #363636; color: white; font-size: 11pt;}"
g2opy_path: str = "/home/cds/github/g2o-pymem/build/lib"
