import os
import cv2
import numpy as np
from math import isnan, sqrt


class DatasetReaderKITTI:
    def __init__(self, datasetPath, scaling=1.0):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__))
        )
        self._datasetPath = os.path.join(__location__, datasetPath)
        self._imagesPath = os.path.join(self._datasetPath, "image_0")
        self._numFrames = len(
            [x for x in os.listdir(self._imagesPath) if x.endswith(".png")]
        )
        self._scaling = scaling

        if self._numFrames < 2:
            raise Exception(
                "Not enough images ({}) found, aborting.".format(
                    frameReader.getFramesCount()
                )
            )
        else:
            print("Found {} images in {}".format(self._numFrames, self._imagesPath))

    def readFrame(self, index=0):
        if index >= self._numFrames:
            raise Exception(
                "Cannot read frame number {} from {}".format(index, self._imagesPath)
            )

        img = cv2.imread(os.path.join(self._imagesPath, "{:06d}.png".format(index)))
        img = cv2.resize(
            img, (int(img.shape[1] * self._scaling), int(img.shape[0] * self._scaling))
        )
        return img

    def readCameraMatrix(self):
        cameraFile = os.path.join(self._datasetPath, "calib.txt")
        with open(cameraFile) as f:
            firstLine = f.readlines()[0][4:]
            focal, _, cx, _, _, _, cy, _, _, _, _, _ = list(
                map(float, firstLine.rstrip().split(" "))
            )

            K = np.zeros((3, 3))
            K[0, 0] = focal
            K[0, 2] = cx
            K[1, 1] = focal
            K[1, 2] = cy
            K[2, 2] = 1
            return K

    def readGroundtuthPosition(self, frameId):
        groundtruthFile = os.path.join(self._datasetPath, "poses.txt")
        with open(groundtruthFile) as f:
            lines = f.readlines()

            _, _, _, tx, _, _, _, ty, _, _, _, tz = list(
                map(float, lines[frameId].rstrip().split(" "))
            )
            _, _, _, tx_prev, _, _, _, ty_prev, _, _, _, tz_prev = list(
                map(float, lines[frameId - 1].rstrip().split(" "))
            )

            position = (tx, ty, tz)
            scale = sqrt(
                (tx - tx_prev) ** 2 + (ty - ty_prev) ** 2 + (tz - tz_prev) ** 2
            )

            return position, scale

    def getFramesCount(self):
        return self._numFrames

    def getDatasetPath(self):
        return self._datasetPath
