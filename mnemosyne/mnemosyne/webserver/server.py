#
# server.py <Peter.Bienstman@UGent.be>
#

import os
import cgi
import socket
import select
import mimetypes

from cherrypy import wsgiserver

from mnemosyne.libmnemosyne import Mnemosyne


# Avoid delays caused by Nagle's algorithm.
# http://www.cmlenz.net/archives/2008/03/python-httplib-performance-problems

realsocket = socket.socket
def socketwrap(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0):
    sockobj = realsocket(family, type, proto)
    sockobj.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    return sockobj
socket.socket = socketwrap



class Server(wsgiserver.CherryPyWSGIServer):

    def __init__(self, port, data_dir, filename):
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
        self.mnemosyne.initialise(data_dir, filename, automatic_upgrades=False)
        self.mnemosyne.review_controller().set_render_chain("webserver")
        self.save_after_n_reps = self.mnemosyne.config()["save_after_n_reps"]
        self.mnemosyne.config()["save_after_n_reps"] = 1
        self.mnemosyne.start_review()
        self.mnemosyne.database().release_connection()
        # When restarting the server, make sure we discard info from the
        # browser resending the form from the previous session.
        self.just_started = True
        wsgiserver.CherryPyWSGIServer.__init__(self,
            ("0.0.0.0", port), self.wsgi_app, server_name="localhost",
            numthreads=1, timeout=1000)

    def serve_until_stopped(self):
        try:
            self.start() # Sets self.wsgi_server.ready
        except KeyboardInterrupt:
            self.stop()
            self.mnemosyne.config()["save_after_n_reps"] = \
                self.save_after_n_reps
            self.mnemosyne.finalise()

    def wsgi_app(self, environ, start_response):
        # Make sure we claim the connection, otherwise checks like
        # 'is_database_loaded' will fail.
        self.mnemosyne.database().claim_connection()
        # All our request return to the root page, so if the path is '/', return
        # the html of the review widget.
        filename = environ["PATH_INFO"]
        if filename == "/":
            # Process clicked buttons in the form.
            form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ)
            if "show_answer" in form and not self.just_started:
                self.mnemosyne.review_widget().show_answer()
            elif "grade" in form and not self.just_started:
                grade = int(form["grade"].value)
                self.mnemosyne.review_widget().grade_answer(grade)
            if self.just_started:
                self.just_started = False
            # Serve the web page.
            response_headers = [("Content-type", "text/html")]
            start_response("200 OK", response_headers)
            return [self.mnemosyne.review_widget().to_html()]
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
