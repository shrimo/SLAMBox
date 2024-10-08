![logo](doc/slambox_logo.png)
 
SLAMBOX is designed for use metod simultaneous localization and mapping ([SLAM][def]) in education, experiments, research and development by Node-based user interface. This is a box with tools that you can quickly and conveniently experiment with separate SLAM nodes.
<br>

![Screenshot01](doc/screenshot01.png)
<sup> [examples/slambox_base.json](examples/slambox_base.json) </sup>

> [!NOTE]  
> You can watch demo via Vimeo link here: [Demo video.](https://vimeo.com/881531969/eee24a6330)

## Introduction

In computing, a visual programming language (VPL) or block coding is a programming language that lets users create programs by manipulating program elements graphically rather than by specifying them textually. Visual programming allows programming with visual expressions, spatial arrangements of text and graphic symbols, used either as elements of syntax or secondary notation. For example, many VPLs (known as diagrammatic programming) are based on the idea of "boxes and arrows", where boxes or other screen objects are treated as entities, connected by arrows, lines or arcs which represent relations.

The development of robotics generates a request for recognition and control systems for data received from sensory devices. At present, development of Computer Vision systems requires developers to have knowledge of programming languages and a deep understanding of mathematics. It was like the development of computer graphics: at the beginning, only scientists and researchers were engaged in computer graphics, later applied tools ([Presented by such programs as Nuke, Houdini, Blender](https://en.wikipedia.org/wiki/Visual_programming_language)) were developed for use by less trained users. Over time, the development of computer vision systems should shift to the use of visual, graphical interfaces, such as Node-based UI, so that more ordinary users can access computer vision technologies.

The computer vision systems can be controlled not only by classical programming tools (write text code, which in itself narrows the scope of computer vision technologies), in the architecture of graph nodes it is possible to analyze and modify video streams, data from LIDAR, stereo cameras, acoustic sensors through visual programming, which expands the scope of technologies.

### Simultaneous localization and mapping

SLAM is the computational problem of constructing or updating a map of an unknown environment while simultaneously keeping track of an agent's location within it. While this initially appears to be a chicken or the egg problem, there are several algorithms known to solve it in, at least approximately, tractable time for certain environments. Popular approximate solution methods include the particle filter, extended Kalman filter, covariance intersection, and GraphSLAM. SLAM algorithms are based on concepts in computational geometry and computer vision, and are used in robot navigation, robotic mapping and odometry for virtual reality or augmented reality.

<br>

![Blender](doc/screenshot02.png)
<sup>[Blender](https://www.blender.org/)</sup> 

## Design and main components of SLAM pipeline
Feature-based visual SLAM typically tracks points of interest through successive camera frames to triangulate the 3D position of the camera, this information is then used to build a 3D map.

The basic graph for SLAM in SLAMBOX consists of the following nodes: **Camera, DetectorDescriptor, MatchPoints, Triangulate, Open3DMap.** There are also nodes for optimization and elimination of erroneous feature points: **DNNMask, GeneralGraphOptimization, LineModelOptimization, KalmanFilterOptimization.**

#### Camera
- This node, based on the parameters, calculates [Camera Intrinsic Matrix][CameraMatrix]. Intrinsic parameters are specific to a camera. They include information like focal length *(Fx, Fy)* and optical centers *(Cx, Cy)*. The focal length and optical centers can be used to create a camera matrix, which can be used to remove distortion due to the lenses of a specific camera. The camera matrix is unique to a specific camera, so once calculated, it can be reused on other images taken by the same camera. It is expressed as a 3x3 matrix:

#### DetectorDescriptor
- [ORB](https://docs.opencv.org/4.x/d1/d89/tutorial_py_orb.html) Oriented FAST and Rotated BRIEF
- [A-KAZE](http://www.robesafe.com/personal/pablo.alcantarilla/kaze.html)  Accelerated-KAZE Features uses a novel mathematical framework called Fast Explicit Diffusion embedded in a pyramidal framework to speed-up dramatically the nonlinear scale space computation. 

#### MatchPoints
- [Brute-Force](https://docs.opencv.org/4.8.0/dc/dc3/tutorial_py_matcher.html) matcher is simple. It takes the descriptor of one feature in first set and is matched with all other features in second set using some distance calculation. And the closest one is returned.
- [RANSAC](https://en.wikipedia.org/wiki/Random_sample_consensus) (Random sample consensus) is an iterative method to estimate parameters of a mathematical model from a set of observed data that contains outliers, when outliers are to be accorded no influence on the values of the estimates. 

#### Triangulate
- The descriptors of the remaining features are then matched to the next frame, [triangulated](https://www.diva-portal.org/smash/get/diva2:1635583/FULLTEXT02.pdf) and filtered by their re-projection error. Matches are added as candidate tracks. Candidate tracks are searched after in the next frames and added as proper tracks if they are found and pass the re-projection test.

#### Open3DMap
- Here we get a point cloud, a camera and visualize them in a separate process using the Open3D library, it is also possible to record points in the [PCD](https://pointclouds.org/documentation/tutorials/pcd_file_format.html) (Point Cloud Data) file format.

#### DNNMask
- This node creates a mask for a detector/descriptor to cut off moving objects using [Deep Neural Networks](https://learnopencv.com/deep-learning-with-opencvs-dnn-module-a-definitive-guide/).

#### GeneralGraphOptimization
- Optimize a pose graph based on the nodes and edge constraints. This node contains three different methods that solve PGO, GaussNewton Levenberg-Marquardt and Powell’s Dogleg. It is mainly used to solve the SLAM problem in robotics and the bundle adjustment problems in computer vision. ORB-SLAM uses [g2o][def2] as a back-end for camera pose optimization.

<br>

![Screenshot03](doc/screenshot03.png)
<sup> [examples/slambox_dnn.json](examples/slambox_dnn.json) <sup>

## The following libraries are used in development

- [**OpenCV**](https://opencv.org/) (Open Source Computer Vision Library) is a library of programming functions mainly aimed at real-time computer vision. Originally developed by Intel, it was later supported by Willow Garage then Itseez (which was later acquired by Intel). The library is cross-platform and free for use under the open-source Apache 2 License. Starting with 2011, OpenCV features GPU acceleration for real-time operations. 

- [**NumPy**](https://numpy.org/) is a library for the Python programming language, adding support for large, multi-dimensional arrays and matrices, along with a large collection of high-level mathematical functions to operate on these arrays.

- [**g2o**][def2] is an open-source C++ framework for optimizing graph-based nonlinear error functions. g2o has been designed to be easily extensible to a wide range of problems and a new problem typically can be specified in a few lines of code. The current implementation provides solutions to several variants of SLAM and BA.

- [**scikit-image**](https://scikit-image.org/) Image processing in Python is a collection of algorithms for image processing.

- [**SciPy**](https://scipy.org/) (pronounced “Sigh Pie”) is an open-source software for mathematics, science, and engineering.

- [**Open3D**](http://www.open3d.org/) is an open-source library that supports rapid development of software that deals with 3D data. The Open3D frontend exposes a set of carefully selected data structures and algorithms in both C++ and Python.

- [**Qt**](https://wiki.qt.io/Qt_for_Python) is cross-platform software for creating graphical user interfaces as well as cross-platform applications that run on various software and hardware platforms such as Linux, Windows, macOS, Android or embedded systems with little or no change in the underlying codebase while still being a native application with native capabilities and speed.

- [**NodeGraphQt**](http://chantonic.com/NodeGraphQt/api/index.html) a node graph UI framework written in python that can be implemented and re-purposed into applications supporting PySide2.

- [**FFmpeg**](https://ffmpeg.org/) is a free and open-source software project consisting of a suite of libraries and programs for handling video, audio, and other multimedia files and streams.

<br>
<br>


![Screenshot04](doc/screenshot04.png)
<sup> [examples/slambox_g2o.json](examples/slambox_g2o.json) <sup>

### Installing dependent libraries
Fedora
```bash
cd ~/your_fav_code_directory
git clone https://github.com/shrimo/SLAMBox.git
cd SLAMBox
pip install -r requirements.txt
dnf install ffmpeg
```

Ubuntu
```bash
...

sudo apt update
sudo apt install ffmpeg
```
<br>

> [!NOTE]  
> Please install latest opencv-python  
```bash
python3 -m pip install --upgrade opencv-python
```


**g2o** framework for Python can also be build from [source code](https://github.com/RainerKuemmerle/g2o/tree/pymem), also add path to the compiled library in file *config.py*, see the *g2opy_path* variable.
<br>

*SLAMBOX is distributed in the hope that it will be useful, but there is no guarantee that it will work perfectly. There are no warranty as to its quality or suitability for a particular purpose. Our primary development platform is Linux and Python 3.10 (Fedora Linux 36-39, Ubuntu 22). Has been tested on Mac OS X 10.15 (Only the AKAZE descriptor works; the ORB detector still works with errors.)*

### launch

```bash
cd SLAMBox
bash slambox.sh
```

Or you can specify a custom version of Python

```bash
bash slambox.sh 3.10
```

<br>

![Screenshot05](doc/screenshot05.png)
<sup> [examples/slambox_base_flask.json](examples/slambox_base.json) </sup>

#### Launch Flask version

```bash
python build_graph.py FlaskMS
python node_graph.py WebStreaming
```

<br>

## Custom node development

### Node for server part (backend)
Create a class named SimpleNode, which will inherit the properties and methods from the [RootNode](boxes/root_node/node.py) class.
Receives node parameters from the client side when the object is initialized.
#### Class Methods
- **color_reversed** - method reverses colors from RGB to BGR which is used by OpenCV library
- **out_frame** - called by the next node and returns a frame, here we write our code to work with the frame
- **get_input** - returns a list of all input nodes in a given node.
- **update** - updates the parameters
- **get_frame** - this method, common to all nodes, retrieves the frame from the previous connected node, this method is passed input number to the node

#### Class attributes
- **window_name** - contains the name of the root viewer
- **buffer** - contains a [DataBuffer](boxes/pipeline/graph_factory.py) datalass common to all nodes
- **disabled** - this attribute contains the state of the node: enabled or disabled.
- **param** - contains a dictionary with node parameters received from the client part

<br>

```python
"""Example of a simple node (backend)"""

import cv2
import numpy as np
from boxes import RootNode


class SimpleNode(RootNode):
    """A simple node that draws
    a circle with a specific color
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size = self.param["size"]
        self.color = self.color_reversed(self.param["picker"])

    def out_frame(self):
        frame = self.get_frame(0)
        if self.disabled:
            return frame
        height, width, channels = frame.shape
        cv2.circle(
            frame,
            (np.int32(width * 0.5), np.int32(height * 0.5)),
            self.size,
            self.color,
            -1,
        )
        return frame

    def update(self, param):
        self.disabled = param["disabled"]
        self.size = param["size"]
        self.color = self.color_reversed(param["picker"])
```
[boxes/plugins/simple_node.py](boxes/plugins/simple_node.py)

### Node for client part (frontend)

In the client part of the node, we describe the parameters that are passed to the server part. `__identifier__` attribute indicates whether the node belongs to a type, in this case it is **Draw**. Also the color of the node type is set in **set_color**

```python
"""Example of a simple node (frontend)"""

from Qt import QtCore, QtWidgets
from plugins_ui.main_gui_nodes import NodeColorStyle
from NodeGraphQt import BaseNode
from NodeGraphQt.constants import (
    NODE_PROP_QLABEL,
    NODE_PROP_COLORPICKER,
    NODE_PROP_SLIDER,
)

ncs = NodeColorStyle()
ncs.set_value(15)


class SimpleNode(BaseNode):
    __identifier__ = "nodes.Draw"
    NODE_NAME = "SimpleNode"

    def __init__(self):
        super().__init__()
        self.add_input("in", color=(180, 80, 180))
        self.add_output("out")
        self.create_property("label_color", "Color", widget_type=NODE_PROP_QLABEL)
        self.create_property("picker", (0, 255, 0), widget_type=NODE_PROP_COLORPICKER)
        self.create_property("label_size", "Size", widget_type=NODE_PROP_QLABEL)
        self.create_property("size", 100, range=(1, 300), widget_type=NODE_PROP_SLIDER)
        self.set_color(*ncs.Draw)
```
[plugins_ui/simple_gui_node.py](plugins_ui/simple_gui_node.py)

![Screenshot06](doc/screenshot06.png)
<sup>Example of a simple node working</sup>

Ready modules (nodes) must be placed in the following directories: **plugins_ui/** for the client part, **boxes/plugins/** for the server part. SLAMBOX will automatically upload them to existing nodes.

<br>

[Based on twitchslam by geohot](https://github.com/geohot/twitchslam)

:rocket:

[def]: https://en.wikipedia.org/wiki/Simultaneous_localization_and_mapping
[CameraMatrix]: https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
[def2]: https://github.com/RainerKuemmerle/g2o