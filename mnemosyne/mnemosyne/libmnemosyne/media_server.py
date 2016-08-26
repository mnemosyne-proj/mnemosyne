#
# media_server.py <Peter.Bienstman@UGent.be>
#

import os
import cgi
import sys
import time
import locale
import http.client
import threading

from webob import Request
from webob.static import FileApp

from cherrypy import wsgiserver

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.component import Component


class MediaServer(Component, threading.Thread):
    
    """For some version of the webwidget a front end uses, it is not
    permitted to directly access local files, even though file:\\\.
    
    To work around this, we have a lightweight server to serve media
    files.
    
    """
    
    component_type = "media_server"
    
    PORT = 12354

    def __init__(self, component_manager):
        Component.__init__(self, component_manager)
        threading.Thread.__init__(self)

    def run(self):
        self.wsgi_server = wsgiserver.CherryPyWSGIServer(\
            ("0.0.0.0", self.PORT), self.wsgi_app, server_name="localhost",
            numthreads=1, timeout=5)
        self.wsgi_server.start()

    def wsgi_app(self, environ, start_response):
        filename = environ["PATH_INFO"]
        full_path = self.database().media_dir()
        request = Request(environ)
        for word in filename.split("/"):
            full_path = os.path.join(full_path, word)
        app = FileApp(full_path)
        return app(request)(environ, start_response)
        
    def activate(self):
        try:
            self.start()
        except socket.error as exception:
            (errno, e) = exception.args
            if errno == 98:
                self.main_widget().show_error(\
                    _("Unable to start media server.") + " " + \
_("There still seems to be an old server running on the requested port.")\
                    + " " + _("Terminate that process and try again."))
                return
            elif errno == 13:
                self.main_widget().show_error(\
                    _("Unable to start media server.") + " " + \
_("You don't have the permission to use the requested port."))
                return
            else:
                raise e    
        
    def deactivate(self):
        self.wsgi_server.stop()
     
