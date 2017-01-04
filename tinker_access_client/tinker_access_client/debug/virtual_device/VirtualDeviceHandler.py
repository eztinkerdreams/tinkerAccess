import os
import cgi
import json
from BaseHTTPServer import BaseHTTPRequestHandler

pins = [
    [
        {'pin': 2, 'desc': '5v Power', 'status': False},
        {'pin': 4, 'desc': '5v Power', 'status': False},
        {'pin': 6, 'desc': 'Ground', 'status': False},
        {'pin': 8, 'desc': 'BCM 14', 'status': True},
        {'pin': 10, 'desc': 'BCM 15', 'status': True},
        {'pin': 12, 'desc': 'BCM 18', 'status': True},
        {'pin': 14, 'desc': 'Ground', 'status': False},
        {'pin': 16, 'desc': 'BCM 23', 'status': True},
        {'pin': 18, 'desc': 'BCM 24', 'status': True},
        {'pin': 20, 'desc': 'Ground', 'status': False},
        {'pin': 22, 'desc': 'BCM 25', 'status': True},
        {'pin': 24, 'desc': 'BCM 8', 'status': True},
        {'pin': 26, 'desc': 'BCM 7', 'status': True},
        {'pin': 28, 'desc': 'BCM 1', 'status': True},
        {'pin': 30, 'desc': 'Ground', 'status': False},
        {'pin': 32, 'desc': 'BCM 12', 'status': True},
        {'pin': 34, 'desc': 'Ground', 'status': False},
        {'pin': 36, 'desc': 'BCM 16', 'status': True},
        {'pin': 38, 'desc': 'BCM 20', 'status': True},
        {'pin': 40, 'desc': 'BCM 21', 'status': True}],
    [
        {'pin': 1, 'desc': '3v3 Power', 'status': False},
        {'pin': 3, 'desc': 'BCM 2', 'status': False},
        {'pin': 5, 'desc': 'BCM 3', 'status': False},
        {'pin': 7, 'desc': 'BCM 4', 'status': False},
        {'pin': 9, 'desc': 'Ground', 'status': False},
        {'pin': 11, 'desc': 'BCM 17', 'status': True},
        {'pin': 13, 'desc': 'BCM 27', 'status': True},
        {'pin': 15, 'desc': 'BCM 22', 'status': True},
        {'pin': 17, 'desc': '3v3 Power', 'status': False},
        {'pin': 19, 'desc': 'BCM 10', 'status': True},
        {'pin': 21, 'desc': 'BCM 9', 'status': True},
        {'pin': 23, 'desc': 'BCM 11', 'status': True},
        {'pin': 25, 'desc': 'Ground', 'status': False},
        {'pin': 27, 'desc': 'BCM 0', 'status': True},
        {'pin': 29, 'desc': 'BCM 5', 'status': True},
        {'pin': 31, 'desc': 'BCM 6', 'status': True},
        {'pin': 33, 'desc': 'BCM 13', 'status': True},
        {'pin': 35, 'desc': 'BCM 19', 'status': True},
        {'pin': 37, 'desc': 'BCM 26', 'status': True},
        {'pin': 39, 'desc': 'Ground', 'status': False}
    ]
]


class VirtualDeviceHandler(BaseHTTPRequestHandler):
    # noinspection PyPep8Naming
    def do_GET(self):
        path = '/VirtualDevice.html' if self.path == '/' else self.path

        try:
            sendReply = False
            if path.endswith(".html"):
                mimetype = 'text/html'
                sendReply = True
            if path.endswith(".jpg"):
                mimetype = 'image/jpg'
                sendReply = True
            if path.endswith(".gif"):
                mimetype = 'image/gif'
                sendReply = True
            if path.endswith(".js"):
                mimetype = 'application/javascript'
                sendReply = True
            if path.endswith(".css"):
                mimetype = 'text/css'
                sendReply = True
            if path.endswith(".json"):
                mimetype = 'application/javascript'
                self.send_response(200)
                self.send_header('Content-type', mimetype)
                self.end_headers()
                self.wfile.write(json.dumps(pins))
                return

            if sendReply:
                f = open('{0}{1}'.format(os.path.dirname(os.path.realpath(__file__)), path))
                self.send_response(200)
                self.send_header('Content-type', mimetype)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
            return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    # noinspection PyPep8Naming
    def do_POST(self):
        if self.path == "/send":
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': self.headers['Content-Type'],
            })

            pin_number = form['pin'].value
            pin_status = form['status'].value == 'false'
            self.update_status(pin_number, pin_status)
            self.send_response(200)
            self.end_headers()
            return

    def update_status(self, pin_number, pin_status):
        for rows in pins:
            for pin in rows:
                if pin['pin'] == int(pin_number):
                    pin['status'] = pin_status
                    break
