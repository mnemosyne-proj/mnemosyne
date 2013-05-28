#
# webserver.py <Peter.Bienstman@UGent.be>
#

import os
import cgi
import time
import socket
import select
import httplib
import threading
import mimetypes

from cherrypy import wsgiserver
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.utils import localhost_IP


class TimerClass(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.ping()

    def ping(self):
        self.last_ping = time.time()

    def run(self):
        while time.time() < self.last_ping + 5*60:
            time.sleep(1)
        con = httplib.HTTPConnection("127.0.0.1", self.port)
        con.request("GET", "/release_database")
        response = con.getresponse()


class WebServer(object):

    def __init__(self, port, data_dir, filename):
        self.port = port
        self.data_dir = data_dir
        self.filename = filename
        # When restarting the server, make sure we discard info from the
        # browser resending the form from the previous session.
        self.is_just_started = True
        self.is_mnemosyne_loaded = False
        self.wsgi_server = wsgiserver.CherryPyWSGIServer(\
            ("0.0.0.0", port), self.wsgi_app, server_name="localhost",
            numthreads=1, timeout=1000)

    def serve_until_stopped(self):
        try:
            self.wsgi_server.start() # Sets self.wsgi_server.ready
        except KeyboardInterrupt:
            self.wsgi_server.stop()
            if self.is_mnemosyne_loaded:
                self.unload_mnemosyne()

    def load_mnemosyne(self):
        self.mnemosyne = Mnemosyne(upload_science_logs=True,
            interested_in_old_reps=True)
        self.mnemosyne.components.insert(0, (
            ("mnemosyne.libmnemosyne.translators.gettext_translator",
             "GetTextTranslator")))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.main_widget",
             "MainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.webserver.review_wdgt",
             "ReviewWdgt"))
        self.mnemosyne.components.append(\
            ("mnemosyne.webserver.webserver_render_chain",
             "WebserverRenderChain"))
        self.mnemosyne.initialise(self.data_dir, self.filename,
            automatic_upgrades=False)
        self.mnemosyne.review_controller().set_render_chain("webserver")
        self.save_after_n_reps = self.mnemosyne.config()["save_after_n_reps"]
        self.mnemosyne.config()["save_after_n_reps"] = 1
        self.mnemosyne.start_review()
        self.is_mnemosyne_loaded = True
        self.timer = TimerClass(self.port)
        self.timer.start()

    def unload_mnemosyne(self):
        self.mnemosyne.config()["save_after_n_reps"] = self.save_after_n_reps
        self.mnemosyne.finalise()
        self.is_mnemosyne_loaded = False

    def wsgi_app(self, environ, start_response):
        if not self.is_mnemosyne_loaded:
            self.load_mnemosyne()
        self.timer.ping()
        # All our request return to the root page, so if the path is '/', return
        # the html of the review widget.
        filename = environ["PATH_INFO"]
        if filename == "/":
            # Process clicked buttons in the form.
            form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ)
            if "show_answer" in form and not self.is_just_started:
                self.mnemosyne.review_widget().show_answer()
            elif "grade" in form and not self.is_just_started:
                grade = int(form["grade"].value)
                self.mnemosyne.review_widget().grade_answer(grade)
            if self.is_just_started:
                self.is_just_started = False
            # Serve the web page.
            response_headers = [("Content-type", "text/html")]
            start_response("200 OK", response_headers)
            return [self.mnemosyne.review_widget().to_html()]
        elif filename == "/release_database":
            self.unload_mnemosyne()
            print 'unload'
        # We need to serve a media file.
        else:
            if filename == "/favicon.ico":
                # No need to do spend time on a disk access here.
                return ["404 File not found"]
            media_file = self.open_media_file(filename)
            if media_file is None:
                response_headers = [("Content-type", "text/html")]
                start_response("404 File not found", response_headers)
                return ["404 File not found"]
            else:
                response_headers = [("Content-type", self.guess_type(filename))]
                start_response("200 OK", response_headers)
                return [media_file.read()]

    def open_media_file(self, path):
        full_path = self.mnemosyne.database().media_dir()
        for word in path.split("/"):
            full_path = os.path.join(full_path, word)
        try:
            return file(full_path, "rb")
        except IOError:
            return None

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


class WebServerThread(threading.Thread, WebServer):

    """Basic threading implementation of the sync server, suitable for text-
    based UIs. A GUI-based client will want to override several functions
    in Server and ServerThread in view of the interaction between multiple
    threads and the GUI event loop.

    """

    def __init__(self, component_manager):
        threading.Thread.__init__(self)
        self.config = component_manager.current("config")
        WebServer.__init__(self, self.config["webserver_port"],
            self.config.data_dir, self.config["last_database"])

    def run(self):
        print "Web server listening on http://" + \
            localhost_IP() + ":" + str(self.config["webserver_port"])
        self.serve_until_stopped()


