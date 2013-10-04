#
# web_server.py <Peter.Bienstman@UGent.be>
#

import os
import cgi
import time
import httplib
import threading

from webob import Request
from webob.static import FileApp

from cherrypy import wsgiserver

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.utils import localhost_IP


class ReleaseDatabaseAfterTimeout(threading.Thread):

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


class StopServerAfterTimeout(threading.Thread):

    def __init__(self, wsgi_server):
        threading.Thread.__init__(self)
        self.wsgi_server = wsgi_server

    def run(self):
        time.sleep(3)
        self.wsgi_server.stop()


class WebServer(object):

    def __init__(self, port, data_dir, filename, is_server_local=False):
        self.port = port
        self.data_dir = data_dir
        self.filename = filename
        self.is_server_local = is_server_local
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
            ("mnemosyne.web_server.review_wdgt",
             "ReviewWdgt"))
        self.mnemosyne.components.append(\
            ("mnemosyne.web_server.web_server_render_chain",
             "WebServerRenderChain"))
        self.mnemosyne.initialise(self.data_dir, self.filename,
            automatic_upgrades=False)
        self.mnemosyne.review_controller().set_render_chain("web_server")
        self.save_after_n_reps = self.mnemosyne.config()["save_after_n_reps"]
        self.mnemosyne.config()["save_after_n_reps"] = 1
        self.mnemosyne.start_review()
        self.mnemosyne.review_widget().set_is_server_local(self.is_server_local)
        self.is_mnemosyne_loaded = True
        if not self.is_server_local:
            self.release_database_after_timeout = \
                ReleaseDatabaseAfterTimeout(self.port)
            self.release_database_after_timeout.start()

    def unload_mnemosyne(self):
        if not self.is_mnemosyne_loaded:
            return
        self.mnemosyne.config()["save_after_n_reps"] = self.save_after_n_reps
        self.mnemosyne.finalise()
        self.is_mnemosyne_loaded = False

    def wsgi_app(self, environ, start_response):
        filename = environ["PATH_INFO"]
        if not self.is_mnemosyne_loaded and filename != "/release_database":
            self.load_mnemosyne()
        if not self.is_server_local:
            self.release_database_after_timeout.ping()
        # All our request return to the root page, so if the path is '/',
        # return the html of the review widget.
        if filename == "/":
            # Process clicked buttons in the form.
            form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ)
            if "show_answer" in form and not self.is_just_started:
                self.mnemosyne.review_widget().show_answer()
                page = self.mnemosyne.review_widget().to_html()
            elif "grade" in form and not self.is_just_started:
                grade = int(form["grade"].value)
                self.mnemosyne.review_widget().grade_answer(grade)
                page = self.mnemosyne.review_widget().to_html()
            elif "star" in form:
                self.mnemosyne.controller().star_current_card()
                page = self.mnemosyne.review_widget().to_html()
            elif "exit" in form:
                self.unload_mnemosyne()
                page = "Server stopped"
                self.wsgi_server.stop()
                self.stop_server_after_timeout = \
                    StopServerAfterTimeout(self.wsgi_server)
                self.stop_server_after_timeout.start()
            else:
                page = self.mnemosyne.review_widget().to_html()
            if self.is_just_started:
                self.is_just_started = False
            # Serve the web page.
            response_headers = [("Content-type", "text/html")]
            start_response("200 OK", response_headers)
            return [page]
        elif filename == "/release_database":
            self.unload_mnemosyne()
            response_headers = [("Content-type", "text/html")]
            start_response("200 OK", response_headers)
            return ["200 OK"]
        # We need to serve a media file.
        else:
            full_path = self.mnemosyne.database().media_dir()
            for word in filename.split("/"):
                full_path = os.path.join(full_path, word)
            request = Request(environ)
            if os.path.exists(full_path):
                etag = "%s-%s-%s" % (os.path.getmtime(full_path),
                    os.path.getsize(full_path), hash(full_path))
            else:
                etag = "none"
            app = FileApp(full_path, etag=etag)
            return app(request)(environ, start_response)


class WebServerThread(threading.Thread, WebServer):

    """Basic threading implementation of the sync server, suitable for text-
    based UIs. A GUI-based client will want to override several functions
    in Server and ServerThread in view of the interaction between multiple
    threads and the GUI event loop.

    """

    def __init__(self, component_manager, is_server_local=False):
        self.is_server_local = is_server_local
        threading.Thread.__init__(self)
        self.config = component_manager.current("config")
        WebServer.__init__(self, self.config["web_server_port"],
            self.config.data_dir, self.config["last_database"], 
            self.is_server_local)

    def run(self):
        if not self.is_server_local:  # Could fail if we are offline.
            print "Web server listening on http://" + \
                localhost_IP() + ":" + str(self.config["web_server_port"])
        self.serve_until_stopped()
