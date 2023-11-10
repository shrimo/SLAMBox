import cv2
import numpy as np

midnight_blue = (110, 50, 30)
white = (255, 255, 255)
font = cv2.FONT_HERSHEY_SIMPLEX


def show_attributes(frame, list_attributes, x_offset=0, color=midnight_blue):
    """
    Display object attributes
    a list can have a number of string attributes
    """
    step = 30
    ssize = len(max(list_attributes, key=len))
    for ns, attribut in enumerate(list_attributes):
        ns = (ns + 1) * step
        cv2.rectangle(
            frame,
            (30 + x_offset, ns - step),
            (ssize * 13 + x_offset, ns + (step // 2) - 10),
            color,
            -1,
        )
        cv2.putText(frame, attribut, (45 + x_offset, ns - 10), font, 0.5, white, 1)
    return frame


def drawFrameFeatures(frame, prevPts, currPts, frameIdx):
    """Draws detected and tracked features on a frame
    motion vector is drawn as a line.
    """
    currFrameRGB = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
    for i in range(len(currPts) - 1):
        cv2.circle(
            currFrameRGB,
            (np.int32(currPts[i][0]), np.int32(currPts[i][1])),
            radius=3,
            color=(0, 255, 0),
        )
        cv2.line(
            currFrameRGB,
            (np.int32(currPts[i][0]), np.int32(currPts[i][1])),
            (np.int32(prevPts[i][0]), np.int32(prevPts[i][1])),
            color=(0, 0, 255),
        )
        attr = [f"Frame: {frameIdx}", f"Features: {len(currPts)}"]
        show_attributes(currFrameRGB, attr, x_offset=10)
    cv2.imshow("2D Viewer", currFrameRGB)
