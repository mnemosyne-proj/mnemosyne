#
# client.py - Max Usachev <maxusachev@gmail.com>
#             Ed Bartosh <bartosh@gmail.com>
#             Peter Bienstman <Peter.Bienstman@UGent.be>
#

import mnemosyne.version
import base64
import urllib2
import uuid
import os
from sync import SyncError
from sync import EventManager
from sync import PROTOCOL_VERSION, N_SIDED_CARD_TYPE
from xml.etree import cElementTree


# Overrides get_method method for using PUT request in urllib2.

class PutRequest(urllib2.Request):
    def get_method(self):
        return "PUT"


class Client:

    def __init__(self, host, port, uri, database, controller, config, log, \
        ui_controller):
        self.config = config
        self.log = log
        self.host = host
        self.port = port
        self.uri = uri
        self.ui_controller = ui_controller
        self.eman = EventManager(database, log, controller, \
            self.config.mediadir(), self.get_media_file, self.ui_controller)
        self.login = ''
        self.passwd = ''
        self.id = hex(uuid.getnode())
        self.name = 'Mnemosyne'
        self.version = mnemosyne.version.version
        self.deck = 'default'
        self.protocol = PROTOCOL_VERSION
        self.cardtypes = N_SIDED_CARD_TYPE
        self.extra = ''
        self.stopped = False

    def set_user(self, login, passwd):
        self.login, self.passwd = login, passwd

    def start(self):       
        try:
            self.ui_controller.update_status("Authorization. Please, wait...")
            self.login_()

            self.ui_controller.update_status("Handshaking. Please, wait...")
            self.handshake()

            self.ui_controller.update_status("Creating backup. Please, wait...")
            backup_file = self.eman.make_backup()

            server_media_count = self.get_server_media_count()
            if server_media_count:
                self.ui_controller.update_status(\
                    "Applying server media. Please, wait...")
                self.eman.apply_media(self.get_media_history(), \
                    server_media_count)

            client_media_count = self.eman.get_media_count()
            if client_media_count:
                self.ui_controller.update_status(\
                    "Sending client media to the server. Please, wait...")
                self.send_client_media(self.eman.get_media_history(), \
                    client_media_count)

            server_history_length = self.get_server_history_length()
            if server_history_length:
                self.ui_controller.update_status(\
                    "Applying server history. Please, wait...")
                self.get_server_history(server_history_length)

            # Save current database and open backuped database
            # to get history for server.
            self.eman.replace_database(backup_file)
            
            client_history_length = self.eman.get_history_length()
            if client_history_length:
                self.ui_controller.update_status(\
                    "Sending client history to the server. Please, wait...")
                self.send_client_history(self.eman.get_history(), \
                    client_history_length)

            # Close temp database and return worked database.
            self.eman.return_databases()

            self.ui_controller.update_status(\
                "Waiting for the server complete. Please, wait...")
    
            self.send_finish_request()

            if self.stopped:
                raise SyncError("Aborted!")
        except SyncError, exception:
            self.eman.restore_backup()
            self.ui_controller.show_message("Error: " + str(exception))
        else:
            self.eman.remove_backup()
            self.ui_controller.show_message("Sync finished!")

    def stop(self):
        self.stopped = True
        self.eman.stop()

    def login_(self):
        self.ui_controller.update_events()
        base64string = base64.encodestring("%s:%s" % \
            (self.login, self.passwd))[:-1]
        authheader =  "Basic %s" % base64string
        request = urllib2.Request(self.uri)
        request.add_header("AUTHORIZATION", authheader)
        try:
            urllib2.urlopen(request).read()
        except urllib2.URLError, error:
            if hasattr(error, 'code'):
                if error.code == 403:
                    raise SyncError(\
                        "Authentification failed: wrong login or password!")
            else:
                raise SyncError(str(error.reason))

    def handshake(self):
        if self.stopped:
            return
        self.ui_controller.update_events()
        cparams = "<params><client id='%s' name='%s' ver='%s' protocol='%s'" \
            " deck='%s' cardtypes='%s' extra='%s'/></params>\n" % (self.id, \
            self.name, self.version, self.protocol, self.deck, self.cardtypes, \
            self.extra)
        try:
            sparams = urllib2.urlopen(self.uri + '/sync/server/params').read()
            response = urllib2.urlopen(PutRequest(\
                self.uri + '/sync/client/params', cparams))
            if response.read() != "OK":
                raise SyncError("Handshaking: error on server side.")
        except urllib2.URLError, error:
            raise SyncError("Handshaking: " + str(error))
        else:
            self.eman.set_sync_params(sparams)
            self.eman.update_partnerships_table()

    def set_params(self, params):
        for key in params.keys():
            setattr(self, key, params[key])

    def get_server_media_count(self):
        if self.stopped:
            return
        self.ui_controller.update_events()
        try:
            return int(urllib2.urlopen(\
                self.uri + '/sync/server/history/media/count').read())
        except urllib2.URLError, error:
            raise SyncError("Getting server media count: " + str(error))

    def get_server_history_length(self):
        if self.stopped:
            return
        self.ui_controller.update_events()
        try:
            return int(urllib2.urlopen(\
                self.uri + '/sync/server/history/length').read())
        except urllib2.URLError, error:
            raise SyncError("Getting server history length: " + str(error))

    def get_server_history(self, history_length):
        if self.stopped:
            return
        self.ui_controller.update_events()
        count = 0
        hsize = float(history_length)
        try:
            #return urllib2.urlopen(self.uri + '/sync/server/history')
            response = urllib2.urlopen(self.uri + '/sync/server/history')
            response.readline() # get "<history>"
            chunk = response.readline() #get the first item
            self.ui_controller.show_progressbar()
            while chunk != "</history>\n":
                if self.stopped:
                    return
                self.eman.apply_event(chunk)
                chunk = response.readline()
                count += 1
                self.ui_controller.update_progressbar(count / hsize)
            self.ui_controller.hide_progressbar()
        except urllib2.URLError, error:
            raise SyncError("Getting server history: " + str(error))

    def get_media_history(self):
        if self.stopped:
            return
        self.ui_controller.update_events()
        try:
            return urllib2.urlopen(self.uri + '/sync/server/mediahistory'). \
                readline()
        except urllib2.URLError, error:
            raise SyncError("Getting server media history: " + str(error))
       
    def send_client_history(self, history, history_length):
        #if self.stopped:
        #    return
        #self.update_events()
        #chistory = ''
        #for chunk in history:
        #    chistory += chunk
        #data = str(history_length) + '\n' + chistory + '\n'
        #try:
        #    response = urllib2.urlopen(PutRequest(\
        #        self.uri + '/sync/client/history', data))
        #    if response.read() != "OK":
        #        raise SyncError("Sending client history: error on server side.")
        #except urllib2.URLError, error:
        #    raise SyncError("Sending client history: " + str(error))
        import httplib
        conn = httplib.HTTPConnection(self.host, self.port)
        conn.putrequest('PUT', '/sync/client/history')
        conn.putheader('User-Agent', 'gzip')
        conn.putheader('Accept-Encoding', 'gzip')
        conn.putheader('Connection', 'keep-alive')
        conn.putheader('Content-Type', 'text/plain')
        conn.putheader('Transfer-Encoding', 'chunked')
        conn.putheader('Expect', '100-continue')
        conn.putheader('Accept', '*/*')
        conn.endheaders()
       
        count = 0
        hsize = float(history_length + 2)

        # Send client history length.
        conn.send(str(history_length) + '\r\n')
        self.ui_controller.show_progressbar()
        for chunk in history:
            if self.stopped:
                return
            conn.send(chunk + '\r\n')
            count += 1
            self.ui_controller.update_progressbar(count / hsize)

        self.ui_controller.hide_progressbar()
        self.ui_controller.update_status(\
            "Waiting for the server complete. Please, wait...")
        response = conn.getresponse()
        #FIXME: analyze response for complete on server side.
        response.read()

    def send_client_media(self, history, media_count):
        if self.stopped:
            return
        count = 0
        hsize = float(media_count)
        self.ui_controller.show_progressbar()
        for child in cElementTree.fromstring(history):
            self.send_media_file(child.find('id').text.split('__for__')[0])
            count += 1
            self.ui_controller.update_progressbar(count / hsize)
        self.ui_controller.hide_progressbar()

    def send_finish_request(self):
        if self.stopped:
            return
        try:
            if urllib2.urlopen(self.uri + '/sync/finish').read() != "OK":
                raise SyncError("Finishing sync: error on server side.")
        except urllib2.URLError, error:
            raise SyncError("Finishing syncing: " + str(error))
        else:
            self.eman.update_last_sync_event()

    def get_media_file(self, fname):
        try:
            response = urllib2.urlopen(\
                self.uri + '/sync/server/media?fname=%s' % fname)
            data = response.read()
            if data != "CANCEL":
                fobj = open(os.path.join(self.config.mediadir(), fname), 'w')
                fobj.write(data)
                fobj.close()
        except urllib2.URLError, error:
            raise SyncError("Getting server media: " + str(error))

    def send_media_file(self, fname):
        mfile = open(os.path.join(self.config.mediadir(), fname), 'r')
        data = mfile.read()
        mfile.close()
        try:
            request = PutRequest(self.uri + '/sync/client/media?fname=%s' % \
                os.path.basename(fname), data)
            request.add_header('CONTENT_LENGTH', len(data))
            response = urllib2.urlopen(request)
            if response.read() != "OK":
                raise SyncError("Sending client media: error on server side.")
        except urllib2.URLError, error:
            raise SyncError("Sending client media: " + str(error))
