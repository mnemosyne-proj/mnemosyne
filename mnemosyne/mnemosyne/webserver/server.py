#
# server.py <Peter.Bienstman@UGent.be>
#

import os
import cgi
import socket
import select
import mimetypes
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from mnemosyne.libmnemosyne import Mnemosyne


# Avoid delays caused by Nagle's algorithm.
# http://www.cmlenz.net/archives/2008/03/python-httplib-performance-problems

realsocket = socket.socket
def socketwrap(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0):
    sockobj = realsocket(family, type, proto)
    sockobj.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    return sockobj
socket.socket = socketwrap


# Work around http://bugs.python.org/issue6085.

def not_insane_address_string(self):
    host, port = self.client_address[:2]
    return "%s (no getfqdn)" % host

WSGIRequestHandler.address_string = not_insane_address_string


# Don't log (saves time on an embedded server).

def dont_log(*kwargs):
    pass

WSGIRequestHandler.log_message = dont_log


class Server(WSGIServer):

    def __init__(self, port, data_dir, filename):        
        WSGIServer.__init__(self, ("", port), WSGIRequestHandler)
        self.set_app(self.wsgi_app)
        self.stopped = False
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0,
            ("mnemosyne.libmnemosyne.translator", "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.main_widget", "MainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.webserver.html_review_widget", "HtmlReviewWidget"))
        self.mnemosyne.initialise(data_dir, filename, automatic_upgrades=False)
        self.widget = self.mnemosyne.review_controller().widget

    def serve_until_stopped(self):
        while not self.stopped:
            # We time out every 0.25 seconds, so that we changing
            # self.stopped can have an effect.
            if select.select([self.socket], [], [], 0.25)[0]:
                self.handle_request()
        self.socket.close()
    
    def stop(self):
        self.stopped = True

    def wsgi_app(self, environ, start_response):        
        # All our request return to the root page, so if the path is '/', return
        # the html of the review widget.        
        filename = environ["PATH_INFO"]
        if filename == "/":
            # Process clicked buttons in the form.
            form = cgi.FieldStorage(fp=environ["wsgi.input"],  environ=environ)
            if "show_answer" in form:
                self.widget.show_answer()
            if "grade" in form:
                grade = int(form["grade"].value)
                self.widget.grade_answer(grade)
            # Serve the web page.
            response_headers = [("Content-type", "text/html")]
            start_response("200 OK", response_headers)        
            return [self.widget.to_html()]
        # We need to serve a media file.
        else:
            media_file = self.open_media_file(filename)
            if media_file is None:
                response_headers = [("Content-type", "text/html")]
                start_response("404 File not found", response_headers)  
                return ["404 File not found"]
            else:
                response_headers = [("Content-type", self.guess_type(filename))]
                start_response("200 OK", response_headers)
                return self.serve_media_file(media_file)

    def open_media_file(self, path):
        full_path = self.mnemosyne.database().media_dir()
        for word in path.split("/"):
            full_path = os.path.join(full_path, word)
        try:
            return file(full_path, "rb")
        except IOError:
            return None
        
    def serve_media_file(self, media_file):        
        BUFFER_SIZE = 8192
        buffer = media_file.read(BUFFER_SIZE)
        while buffer:
            yield buffer
            buffer = media_file.read(BUFFER_SIZE)

    # Adapted from SimpleHTTPServer:

    def guess_type(self, path):
        base, ext = os.path.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map[""]

    # Try to read system mimetypes.
    if not mimetypes.inited:
        mimetypes.init() 
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({"": "application/octet-stream"})  # Default.
