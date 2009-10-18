#
# server.py - Max Usachev <maxusachev@gmail.com>
#             Ed Bartosh <bartosh@gmail.com>
#            <Peter.Bienstman@UGent.be>

import os
import cgi
import uuid
import base64
import select
import mnemosyne.version
from urlparse import urlparse
from sync import EventManager
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
from sync import PROTOCOL_VERSION
from sync import N_SIDED_CARD_TYPE


class MyWSGIServer(WSGIServer):

    def __init__(self, host, port, app, handler_class=WSGIRequestHandler):
        WSGIServer.__init__(self, (host, port), handler_class)
        self.set_app(app)
        self.stopped = False
        self.update_events = None
        self.timeout = 1

    def stop(self):
        self.stopped = True
        
    def serve_forever(self):
        while not self.stopped:
            self.update_events()
            if select.select([self.socket], [], [], self.timeout)[0]:
                self.handle_request()
        self.socket.close()
            
       

class Server:

    DEFAULT_MIME = "xml/text"

    def __init__(self, uri, database, config, log, ui_controller):
        params = urlparse(uri)
        self.host = params[0]
        self.port = int(params[2])
        self.config = config
        self.log = log
        self.ui_controller = ui_controller
        self.eman = EventManager(database, self.log, None, \
            self.config.mediadir(), None, self.ui_controller)
        self.httpd = MyWSGIServer(self.host, self.port, self.wsgi_app)
        self.httpd.update_events = self.ui_controller.update_events
        self.login = None
        self.passwd = None
        self.logged = False
        self.machine_id = hex(uuid.getnode())
        self.name = 'Mnemosyne'
        self.version = mnemosyne.version.version
        self.protocol = PROTOCOL_VERSION
        self.cardtypes = N_SIDED_CARD_TYPE
        self.upload_media = True
        self.read_only = False

    def set_user(self, login, passwd):
        self.login = login
        self.passwd = passwd

    def get_method(self, environ):

        """Checks for method existence in service and checks for right request
        params. """

        def compare_args(list1, list2):
            """Compares two lists or tuples."""
            for item in list1:
                if not item in list2:
                    return False
            return True

        if environ.has_key('HTTP_AUTHORIZATION'):
            clogin, cpasswd = base64.decodestring(\
                environ['HTTP_AUTHORIZATION'].split(' ')[-1]).split(':')
            if clogin == self.login and cpasswd == self.passwd:
                self.logged = True
                status = '200 OK'
            else:
                status = '403 Forbidden'
            return status, "text/plain", None, None
        else:
            if not self.logged:
                return '403 Forbidden', "text/plain", None, None
            method = (environ['REQUEST_METHOD'] + \
                '_'.join(environ['PATH_INFO'].split('/'))).lower()
            if hasattr(self, method) and callable(getattr(self, method)):
                args = cgi.parse_qs(environ['QUERY_STRING'])
                args = dict([(key, val[0]) for key, val in args.iteritems()])
                if getattr(self, method).func_code.co_argcount-2 == len(args) \
                    and compare_args(args.keys(), getattr(self, method). \
                        func_code.co_varnames):                
                    return '200 OK', self.DEFAULT_MIME, method, args
                else:
                    return '400 Bad Request', "text/plain", None, None
            else:
                return '404 Not Found', "text/plain", None, None

    def wsgi_app(self, environ, start_response):
        status, mime, method, args = self.get_method(environ)
        headers = [('Content-type', mime)]
        start_response(status, headers)
        if method:
            return getattr(self, method)(environ, **args)
        else:
            return status
    
    def start(self):
        self.ui_controller.update_status("Waiting for client connection...")
        print "Server started at HOST:%s, PORT:%s" % (self.host, self.port)
        self.httpd.serve_forever()

    def stop(self):
        self.httpd.stop()
        self.eman.stop()

    def set_params(self, params):
        for key in params.keys():
            setattr(self, key, params[key])

    def get_sync_server_params(self, environ):
        self.ui_controller.update_status(\
            "Sending server params to the client. Please, wait...")
        return "<params><server id='%s' name='%s' ver='%s' protocol='%s' " \
            "cardtypes='%s' upload='%s' readonly='%s'/></params>" % (\
            self.machine_id, self.name, self.version, self.protocol, \
            self.cardtypes, self.upload_media, self.read_only)

    def put_sync_client_params(self, environ):
        self.ui_controller.update_status(\
            "Receiving client params. Please, wait...")
        try:
            socket = environ['wsgi.input']
            client_params = socket.readline()
        except:
            return "CANCEL"
        else:
            self.eman.set_sync_params(client_params)
            self.eman.update_partnerships_table()
            return "OK"

    def get_sync_server_history_media_count(self, environ):
        return str(self.eman.get_media_count())

    def get_sync_server_history_length(self, environ):
        return str(self.eman.get_history_length())

    def get_sync_server_history(self, environ):
        self.ui_controller.update_status(\
            "Sending history to the client. Please, wait...")
        count = 0
        hsize = float(self.eman.get_history_length() + 2)
        self.ui_controller.show_progressbar()
        for chunk in self.eman.get_history():
            count += 1
            fraction = count / hsize
            self.ui_controller.update_progressbar(fraction)
            if fraction == 1.0:
                self.ui_controller.hide_progressbar()
                self.ui_controller.update_status(\
                    "Waiting for the client complete. Please, wait...")
            yield (chunk + '\n')

    def get_sync_server_mediahistory(self, environ):
        self.ui_controller.update_status(\
            "Sending media history to client. Please, wait...")
        return self.eman.get_media_history()

    def put_sync_client_history(self, environ):
        socket = environ['wsgi.input']

        count = 0
        # Gets client history size.
        hsize = float(socket.readline()) + 2

        self.eman.make_backup()
        self.ui_controller.update_status(\
            "Applying client history. Please, wait...")

        socket.readline()  #get "<history>"
        chunk = socket.readline()  #get first xml-event
        self.ui_controller.show_progressbar()
        while chunk != "</history>\r\n":
            self.eman.apply_event(chunk)
            chunk = socket.readline()
            count += 1
            self.ui_controller.update_progressbar(count / hsize)

        self.ui_controller.hide_progressbar()
        self.ui_controller.update_status(\
            "Waiting for the client complete. Please, wait...")
        return "OK"

    def get_sync_finish(self, environ):
        self.eman.remove_backup()
        self.ui_controller.update_status(\
            "Waiting for the client complete. Please, wait...")
        self.eman.update_last_sync_event()
        self.logged = False
        self.stop()
        return "OK"

    def get_sync_server_media(self, environ, fname):
        self.ui_controller.update_status(\
            "Sending media to the client. Please, wait...")
        try:
            mediafile = open(os.path.join(self.config.mediadir(), fname))
            data = mediafile.read()
            mediafile.close()
        except IOError:
            return "CANCEL"
        else:
            return data

    def put_sync_client_media(self, environ, fname):
        self.ui_controller.update_status(\
            "Receiving client media. Please, wait...")
        try:
            socket = environ['wsgi.input']
            size = int(environ['CONTENT_LENGTH'])
            data = socket.read(size)
        except:
            return "CANCEL"
        else:
            mfile = open(os.path.join(self.config.mediadir(), fname), 'w')
            mfile.write(data)
            mfile.close()
            return "OK"

