#
# web_server.py <Peter.Bienstman@gmail.com>
#

import os
import cgi
import time
import urllib
import http.client
import threading

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.utils import localhost_IP
from mnemosyne.libmnemosyne.component import Component


class ReleaseDatabaseAfterTimeout(threading.Thread):

    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port
        self.ping()

    def ping(self):
        self.last_ping = time.time()

    def run(self):
        while time.time() < self.last_ping + 2*60:
            time.sleep(1)
        con = http.client.HTTPConnection("localhost", self.port)
        con.request("GET", "/release_database")
        response = con.getresponse()


class StopServerAfterTimeout(threading.Thread):

    """Stop server after a certain timeout, so that it has
    enough time to serve the final page.

    """

    def __init__(self, wsgi_server):
        threading.Thread.__init__(self)
        self.wsgi_server = wsgi_server

    def run(self):
        time.sleep(3)
        self.wsgi_server.stop()


class WebServer(Component):

    def __init__(self, port, data_dir, config_dir, filename, **kwds):
        if "client_on_same_machine_as_server" in kwds:
            self.client_on_same_machine_as_server = \
                kwds["client_on_same_machine_as_server"]
            del kwds["client_on_same_machine_as_server"]
        else:
            self.client_on_same_machine_as_server = False
        super().__init__(**kwds)
        self.wsgi_server = None
        self.port = port
        self.data_dir = data_dir
        self.config_dir = config_dir
        self.filename = filename
        # When restarting the server, make sure we discard info from the
        # browser resending the form from the previous session.
        self.is_just_started = True
        self.is_mnemosyne_loaded = False
        self.is_shutting_down = False

    def activate(self):
        Component.activate(self)
        # Late import to speed up application startup.
        from cheroot import wsgi
        self.wsgi_server = wsgi.Server(\
            ("0.0.0.0", self.port), self.wsgi_app, server_name="localhost",
            numthreads=1, timeout=5)
        # We need to set the timeout relatively low, otherwise it will take
        # too long for the server to process a 'stop' request.

    def serve_until_stopped(self):
        try:
            self.wsgi_server.start() # Sets self.wsgi_server.ready
        except KeyboardInterrupt:
            self.wsgi_server.stop()
            self.unload_mnemosyne()

    def stop(self):
        if self.wsgi_server:
            self.wsgi_server.stop()
        self.unload_mnemosyne()

    def load_mnemosyne(self):
        self.mnemosyne = Mnemosyne(upload_science_logs=True,
            interested_in_old_reps=True)
        self.mnemosyne.components.insert(0, (
            ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator",
             "GetTextGuiTranslator")))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.main_widget",
             "MainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.web_server.web_server_render_chain",
             "WebServerRenderChain"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = [\
            ("mnemosyne.web_server.review_wdgt",
             "ReviewWdgt")]
        self.mnemosyne.gui_for_component["NewOnly"] = [\
            ("mnemosyne.web_server.review_wdgt",
             "ReviewWdgt")]
        self.mnemosyne.gui_for_component["CramAll"] = [\
            ("mnemosyne.web_server.review_wdgt",
             "ReviewWdgt")]
        self.mnemosyne.gui_for_component["CramRecent"] = [\
            ("mnemosyne.web_server.review_wdgt",
             "ReviewWdgt")]
        self.mnemosyne.initialise(self.data_dir, config_dir=self.config_dir,
            filename=self.filename, automatic_upgrades=False)
        self.save_after_n_reps = self.mnemosyne.config()["save_after_n_reps"]
        self.mnemosyne.config()["save_after_n_reps"] = 1
        self.mnemosyne.config()["study_mode"] = "ScheduledForgottenNew"
        self.mnemosyne.config()["QA_split"] = "fixed"
        self.mnemosyne.review_widget().set_client_on_same_machine_as_server(\
            self.client_on_same_machine_as_server)
        self.mnemosyne.controller().reset_study_mode()
        self.is_mnemosyne_loaded = True
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
        if filename == "/status":
            response_headers = [("Content-type", "text/html")]
            start_response("200 OK", response_headers)
            return [b"200 OK"]
        # Sometimes, even after the user has clicked 'exit' in the page,
        # a browser sends a request for e.g. an audio file.
        if self.is_shutting_down and filename != "/release_database":
            response_headers = [("Content-type", "text/html")]
            start_response("503 Service Unavailable", response_headers)
            return [b"Server stopped"]
        # Load database if needed.
        if not self.is_mnemosyne_loaded and filename != "/release_database":
            self.load_mnemosyne()
        if self.is_mnemosyne_loaded:
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
                self.is_shutting_down = True
            else:
                page = self.mnemosyne.review_widget().to_html()
            if self.is_just_started:
                self.is_just_started = False
            # Serve the web page.
            response_headers = [("Content-type", "text/html")]
            start_response("200 OK", response_headers)
            return [page]
        elif filename == "/api/scheduled":
            scheduled_count, _, _ = \
                self.mnemosyne.review_widget().review_controller().counters()
            response_headers = [("Content-type", "text/plain")]
            start_response("200 OK", response_headers)
            return [str(scheduled_count).encode(encoding='UTF-8')]
        elif filename == "/api/non_memorized":
            _, non_memorised_count, _ = \
                self.mnemosyne.review_widget().review_controller().counters()
            response_headers = [("Content-type", "text/plain")]
            start_response("200 OK", response_headers)
            return [str(non_memorised_count).encode(encoding='UTF-8')]
        elif filename == "/api/active":
            _, _, active_count = \
                self.mnemosyne.review_widget().review_controller().counters()
            response_headers = [("Content-type", "text/plain")]
            start_response("200 OK", response_headers)
            return [str(active_count).encode(encoding='UTF-8')]
        elif filename == "/release_database":
            self.unload_mnemosyne()
            response_headers = [("Content-type", "text/html")]
            start_response("200 OK", response_headers)
            return [b"200 OK"]
        # We need to serve a media file.
        else:
            # Late import to speed up application startup.
            from webob import Request
            from webob.static import FileApp
            # Prevent wsgi from decoding this as as non-unicode behind
            # our back ( https://bugs.python.org/issue16679).
            filename = filename.replace("___-___", "%")
            filename = urllib.parse.unquote(filename)
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

    def __init__(self, component_manager, client_on_same_machine_as_server=False):
        self.client_on_same_machine_as_server = client_on_same_machine_as_server
        threading.Thread.__init__(self)
        self.config = component_manager.current("config")
        WebServer.__init__(self,
            self.config["web_server_port"], self.config.data_dir,
            self.config.config_dir, self.config["last_database"],
            component_manager=component_manager,
            client_on_same_machine_as_server=self.client_on_same_machine_as_server)

    def run(self):
        self.activate()
        if not self.client_on_same_machine_as_server:  # Could fail if we are offline.
            print(("Web server listening on http://" + \
                localhost_IP() + ":" + str(self.config["web_server_port"])))
        self.serve_until_stopped()
