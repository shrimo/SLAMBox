"""
Video Streaming in Web Browsers with OpenCV & Flask
"""
from solvers_flask.root_nodes import Node


class WebStreaming(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node_name = self.param["node_name"]

    def show_frame(self):
        frame = self.get_frame(0)
        if frame is None:
            print("WebStreaming stop")
            return None
        return frame

    def get_roi_from_flask(self, roi):
        print(f"roi: {roi}")
        self.buffer.roi = roi
