import io
import picamera
import picamera.array
import logging
import socketserver
from threading import Condition
from http import server
import cv2
import numpy as np
import time

PAGE="""\
<html>
<head>
<title>picamera MJPEG streaming demo</title>
</head>
<body>
<h1>PiCamera MJPEG Streaming Demo</h1>
<img src="stream.mjpg"/>
<img src="stream2.mjpg"/>
</body>
</html>
"""
#<img src="stream.mjpg" width="640" height="480" />

class StreamingOutput(object):
    def __init__(self, im):
        self.frame1 = None
        self.frame2 = None
        self.buffer = io.BytesIO()
        self.condition = Condition()
        self.im = im

    def write(self, buf):
        self.buffer.truncate()
        with self.condition:
            self.im = np.frombuffer(buf, dtype=np.uint8)
            im1 = self.im.reshape((1200, 1600, 3))[300:750, 0:1100]
            im2 = self.im.reshape((1200, 1600, 3))[500:750, 1150:1600]
            is_success1, im_buf_arr1 = cv2.imencode(".jpg", im1)
            is_success2, im_buf_arr2 = cv2.imencode(".jpg", im2)
            self.frame1 = im_buf_arr1.tobytes()
            self.frame2 = im_buf_arr2.tobytes()
            self.condition.notify_all()
        self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame1 = output.frame1
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame1))
                    self.end_headers()
                    self.wfile.write(frame1)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        elif self.path == '/stream2.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame2 = output.frame2
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame2))
                    self.end_headers()
                    self.wfile.write(frame2)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


with picamera.PiCamera(resolution='1600x1200', framerate=24) as camera:
    # with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    time.sleep(2)
    im = np.empty((1200 * 1600 * 3,), dtype=np.uint8)
    output = StreamingOutput(im)
    camera.start_recording(output, format='bgr')
#    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8081)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
#        pass

