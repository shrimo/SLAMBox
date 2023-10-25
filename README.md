# SLAMBox
This application is designed for training, research, development using Simultaneous localization and mapping (SLAM) method

![Screenshot01](screenshot01.png)

### Simultaneous localization and mapping

Simultaneous localization and mapping **(SLAM)** is the computational problem of constructing or updating a map of an unknown environment while simultaneously keeping track of an agent's location within it. While this initially appears to be a chicken or the egg problem, there are several algorithms known to solve it in, at least approximately, tractable time for certain environments. Popular approximate solution methods include the particle filter, extended Kalman filter, covariance intersection, and GraphSLAM. SLAM algorithms are based on concepts in computational geometry and computer vision, and are used in robot navigation, robotic mapping and odometry for virtual reality or augmented reality.

https://en.wikipedia.org/wiki/Simultaneous_localization_and_mapping

![Screenshot02](screenshot02.png)

### The following libraries are used in development:

**OpenCV** (Open Source Computer Vision Library) is a library of programming functions mainly aimed at real-time computer vision. Originally developed by Intel, it was later supported by Willow Garage then Itseez (which was later acquired by Intel). The library is cross-platform and free for use under the open-source Apache 2 License. Starting with 2011, OpenCV features GPU acceleration for real-time operations.

Some of the nodes presented in the program are made according to the lessons of the documentation for this library. Excellent documentation.
https://opencv.org/

**NumPy** is a library for the Python programming language, adding support for large, multi-dimensional arrays and matrices, along with a large collection of high-level mathematical functions to operate on these arrays.
https://numpy.org/

Image processing in Python **scikit-image** is a 
collection of algorithms for image processing.
https://scikit-image.org/

**Open3D** is an open-source library that supports rapid development of software that deals with 3D data. The Open3D frontend exposes a set of carefully selected data structures and algorithms in both C++ and Python. 
http://www.open3d.org/

**Qt** is cross-platform software for creating graphical user interfaces as well as cross-platform applications that run on various software and hardware platforms such as Linux, Windows, macOS, Android or embedded systems with little or no change in the underlying codebase while still being a native application with native capabilities and speed.
https://en.wikipedia.org/wiki/Qt_(software)

**NodeGraphQt** a node graph UI framework written in python that can be implemented and re-purposed into applications supporting PySide2.
http://chantonic.com/NodeGraphQt/api/index.html

**FFmpeg** is a free and open-source software project consisting of a suite of libraries and programs for handling video, audio, and other multimedia files and streams.
https://ffmpeg.org/

![Screenshot03](screenshot03.png)

### Dependent libraries (Fedora Linux 36 (x86-64), Ubuntu 22.04.2 LTS)

```
pip install numpy

pip install opencv-python

pip install opencv-contrib-python

pip install open3d

pip install scikit-image

pip install PySide2

pip install Qt.py

pip install -U g2o-python

dnf install ffmpeg (apt install ffmpeg) for Ubuntu

```

Based on twitchslam by geohot (https://github.com/geohot/twitchslam)

