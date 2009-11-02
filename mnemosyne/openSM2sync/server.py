#
# server.py - Max Usachev <maxusachev@gmail.com>
#             Ed Bartosh <bartosh@gmail.com>
#             Peter Bienstman <Peter.Bienstman@UGent.be>

import os
import cgi
import base64
import select
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

import mnemosyne.version

from sync import EventManager
from sync import PROTOCOL_VERSION


class Server(WSGIServer):

    """Note that the current implementation of the server can only handle one
    sync request at the time. it is *NOT* yet suited to deploy in a multiuser
    context over the internet, as simultaneous requests from different users
    could get mixed up.

    """
    
    program_name = "unknown-SRS-app"
    program_version = "unknown"
    capabilities = None  # TODO: list possibilies.

    def __init__(self, host, port, ui):
        WSGIServer.__init__(self, (host, port), WSGIRequestHandler)
        self.set_app(self.wsgi_app)
        self.ui = ui
        self.eman = EventManager("mediadir_TODO", None, ui)
        self.stopped = False
        self.logged_in = False
        self.id = "TODO"

    def wsgi_app(self, environ, start_response):
        status, mime, method, args = self.get_method(environ)
        response_headers = [("Content-type", mime)]
        start_response(status, response_headers)
        if method:
            return getattr(self, method)(environ, **args)
        else:
            return status

    def serve_forever(self):
        self.ui.status_bar_message("Waiting for client connection...")
        timeout = 1
        while not self.stopped:
            if select.select([self.socket], [], [], timeout)[0]:
                self.handle_request()
        self.socket.close()

    def stop(self):
        self.stopped = True
        self.eman.stop()

    def get_method(self, environ):

        """Checks for method existence in service and checks for right request
        params.

        """

        def compare_args(list1, list2):
            
            """Compares two lists or tuples."""
            
            for item in list1:
                if not item in list2:
                    return False
            return True

        if environ.has_key("HTTP_AUTHORIZATION"):
            login, password = base64.decodestring(\
                environ["HTTP_AUTHORIZATION"].split(" ")[-1]).split(":")
            if self.authorise(login, password):
                self.logged_in = True
                status = "200 OK"
            else:
                self.logged_in = False
                status = "403 Forbidden"
            return status, "text/plain", None, None
        else:
            if not self.logged_in:
                return "403 Forbidden", "text/plain", None, None
            method = (environ["REQUEST_METHOD"] + \
                "_".join(environ["PATH_INFO"].split("/"))).lower()
            if hasattr(self, method) and callable(getattr(self, method)):
                args = cgi.parse_qs(environ["QUERY_STRING"])
                args = dict([(key, val[0]) for key, val in args.iteritems()])
                if getattr(self, method).func_code.co_argcount-2 == len(args) \
                    and compare_args(args.keys(), getattr(self, method). \
                        func_code.co_varnames):                
                    return "200 OK", "xml/text", method, args
                else:
                    return "400 Bad Request", "text/plain", None, None
            else:
                return "404 Not Found", "text/plain", None, None

    def authorise(self, login, password):

        """Returns true if password correct for login."""

        raise NotImplementedError

    def open_database(self, database_name):

        """Sets self.database to a database object for the database named
        'database_name'.

        """

        raise NotImplementedError        

    # The following are methods that are supported by the server through GET
    # and PUT calls. 'get_foo_bar' gets executed after a 'GET /foo/bar'
    # request. Similarly, 'put_foo_bar' gets executed after a 'PUT /foo/bar'
    # request.

    def get_sync_server_params(self, environ):
        self.ui.status_bar_message("Sending server info to the client...")
        return ("<server id='%s' program_name='%s' " + \
            "program_version='%s' protocol_version='%s' capabilities='%s' " + \
            "server_deck_read_only='false' " + \
            "server_allows_media_upload='true'></server>") % (self.id,
            self.program_name, self.program_version, PROTOCOL_VERSION,
            self.capabilities)        

    def put_sync_client_params(self, environ):
        self.ui.status_bar_message("Receiving client info...")
        try:
            socket = environ["wsgi.input"]
            client_params = socket.readline()
        except:
            return "CANCEL"
        else:
            self.eman.set_partner_params(client_params)
            self.open_database(self.eman.partner["database_name"])
            self.eman.database = self.database
            self.eman.create_partnership_if_needed()
            return "OK"

    def get_sync_server_history_media_count(self, environ):
        return str(self.eman.get_media_count())

    def get_sync_server_history_length(self, environ):
        return str(self.eman.get_history_length())

    def get_sync_server_history(self, environ):
        self.ui.status_bar_message("Sending history to the client...")
        count = 0
        hsize = float(self.eman.get_history_length() + 2)
        self.ui.show_progressbar()
        for chunk in self.eman.get_history():
            count += 1
            fraction = count / hsize
            self.ui.update_progressbar(fraction)
            if fraction == 1.0:
                self.ui.hide_progressbar()
                self.ui.status_bar_message("Waiting for client to complete...")
            yield (chunk + "\n")

    def get_sync_server_mediahistory(self, environ):
        self.ui.status_bar_message("Sending media history to client...")
        return self.eman.get_media_history()

    def put_sync_client_history(self, environ):
        socket = environ["wsgi.input"]

        count = 0
        # Gets client history size.
        hsize = float(socket.readline()) + 2

        self.eman.make_backup()
        self.ui.status_bar_message("Applying client history...")

        socket.readline()  # get "<history>".
        chunk = socket.readline()  # get first xml-event.
        self.ui.show_progressbar()
        while chunk != "</history>\r\n":
            self.eman.apply_event(chunk)
            chunk = socket.readline()
            count += 1
            self.ui.update_progressbar(count / hsize)

        self.ui.hide_progressbar()
        self.ui.status_bar_message("Waiting for client to finish...")
        return "OK"

    def get_sync_finish(self, environ):
        self.ui.status_bar_message("Waiting for client to finish...")
        self.eman.update_last_sync_event()
        self.logged_in = False
        self.stop()
        return "OK"

    def get_sync_server_media(self, environ, fname):
        self.ui.status_bar_message("Sending media to the client...")
        try:
            mediafile = open(os.path.join(self.config.mediadir(), fname))
            data = mediafile.read()
            mediafile.close()
        except IOError:
            return "CANCEL"
        else:
            return data

    def put_sync_client_media(self, environ, fname):
        self.ui.status_bar_message("Receiving client media...")
        try:
            socket = environ["wsgi.input"]
            size = int(environ["CONTENT_LENGTH"])
            data = socket.read(size)
        except:
            return "CANCEL"
        else:
            mfile = open(os.path.join(self.config.mediadir(), fname), "w")
            mfile.write(data)
            mfile.close()
            return "OK"

