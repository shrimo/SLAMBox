#!/usr/bin/env python3.10
"""
Video Streaming in Web Browsers with OpenCV & Flask
"""
from flask import Flask, render_template, request, Response, jsonify
from flask_cors import CORS
import cv2

app = Flask(__name__)
CORS(app)

camera = cv2.VideoCapture('..//video/road.mp4')

def video_stream():
    global camera
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/selected_area', methods=['POST'])
def selected_area():
    data = request.get_json()
    start_x = data['start_x']
    start_y = data['start_y']
    end_x = data['end_x']
    end_y = data['end_y']
    print(f'-> get data: {data}')
    return jsonify({'message': 'data received'})

if __name__ == '__main__':
    app.run(debug=True)
