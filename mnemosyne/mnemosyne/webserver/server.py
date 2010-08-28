#
# web_server.py <Peter.Bienstman@UGent.be>
#


#
# Playing around, throw-away code. Don't use for anything serious!
#

import cgi
import select
import time
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

class Widget(MainWidget):
    
    def set_progress_text(self, message):
        print message
        
    def information_box(self, info):
        print info
        
    def error_box(self, error):
        global last_error
        last_error = error
        # Activate this for debugging.
        sys.stderr.write(error)

    def question_box(self, question, option0, option1, option2):
        return answer
    

class Server(WSGIServer):

    def __init__(self, port, data_dir, filename):        
        WSGIServer.__init__(self, ("", port), WSGIRequestHandler)
        self.set_app(self.wsgi_app)
        self.stopped = False

        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(("mnemosyne.webserver.server", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.initialise(data_dir, filename, automatic_upgrades=False)

    def serve_until_stopped(self):
        while not self.stopped:
            # We time out every 0.25 seconds, so that we changing
            # self.stopped can have an effect.
            if select.select([self.socket], [], [], 0.25)[0]:
                self.handle_request()
        self.socket.close()

    def wsgi_app(self, environ, start_response):

        
        method = (environ["REQUEST_METHOD"] + \
                  environ["PATH_INFO"].replace("/", "_")).lower()
        args = cgi.parse_qs(environ["QUERY_STRING"])
        args = dict([(key, val[0]) for key, val in args.iteritems()])
        print method, args

        form = cgi.FieldStorage(fp=environ['wsgi.input'], 
                        environ=environ)
        print form

        status = "200 OK"
        response_headers = [("Content-type", "text/html")]
        start_response(status, response_headers)
        html = "<br/><br/><table><tr>"
        html += str(time.time())
        for i in range(6):
            html += """<td><form action="grade" method="post">"""
            html += """<input type="submit" name="grade" value="%d" accesskey="%d">""" % (i, i)
            html += "</form></td>"
        html += "</tr></table>"
        html += self.mnemosyne.review_controller().card.question(exporting=True).encode("utf-8")
        return html

    def stop(self):
        self.stopped = True

