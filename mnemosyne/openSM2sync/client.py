#
# client.py - Max Usachev <maxusachev@gmail.com>
#             Ed Bartosh <bartosh@gmail.com>
#             Peter Bienstman <Peter.Bienstman@UGent.be>
#

import os
import base64
import urllib2
import httplib
from urlparse import urlparse
from xml.etree import cElementTree

from synchroniser import SyncError
from synchroniser import Synchroniser
from synchroniser import PROTOCOL_VERSION


class PutRequest(urllib2.Request):

    """Implement PUT request in urllib2, as needed by the RESTful API."""
    
    def get_method(self):
        return "PUT"


class Client(object):
    
    program_name = "unknown-SRS-app"
    program_version = "unknown"
    capabilities = None  # TODO: list possibilies.
    
    def __init__(self, database, ui):
        self.database = database
        self.ui = ui
        self.synchroniser = Synchroniser()
        self.synchroniser.database = database
        self.id = "TODO"

    def sync(self, url, username, password):       
        try:
            self.url = url           
            self.ui.status_bar_message("Creating backup...")
            backup_file = self.database.backup()           
            self.login(username, password)
            self.handshake()
            self.send_client_history()       
            self.get_server_history()
            self.send_finish_request()
        except SyncError, exception:
            self.database.load(backup_file) # TODO: use SQL rollback?
            self.ui.error_box("Error: " + str(exception))
        else:
            self.ui.information_box("Sync finished!")

    def login(self, username, password):
        self.ui.status_bar_message("Logging in...")
        request = urllib2.Request(self.url)
        base64string = base64.encodestring("%s:%s" % (username, password))
        # Add header and strip off trailing \n in base64string.
        request.add_header("AUTHORIZATION", "Basic %s" % base64string[:-1])
        try:
            urllib2.urlopen(request).read()
        except urllib2.URLError, error:
            if hasattr(error, "code") and error.code == 403:
                raise SyncError("Wrong login or password.")
            else:
                raise SyncError(str(error.reason))

    def handshake(self):
        self.ui.status_bar_message("Handshaking...")
        client_params = ("<client id='%s' program_name='%s' " + \
            "program_version='%s' protocol_version='%s' capabilities='%s' " + \
            "database_name='%s'></client>\n") % (self.id, self.program_name,
            self.program_version, PROTOCOL_VERSION, self.capabilities,
            self.database.database_name())
        try:
            server_params = urllib2.urlopen(self.url + '/server/params').read()
            response = urllib2.urlopen(PutRequest(\
                self.url + '/client/params', client_params))
            if response.read() != "OK":
                raise SyncError("Handshaking: error on server side.")
        except urllib2.URLError, error:
            raise SyncError("Handshaking: " + str(error))
        self.synchroniser.set_partner_params(server_params)
        self.server_id = self.synchroniser.partner["id"]
        self.database.create_partnership_if_needed_for(self.server_id)
            
    def send_client_history(self):
        self.ui.status_bar_message("Sending client history to the server...")
        log_entries = self.database.number_of_log_entries_to_sync_for(\
            self.server_id)
        if log_entries == 0:
            return

        parsed_url = urlparse(self.url) 
        conn = httplib.HTTPConnection(parsed_url.hostname, parsed_url.port)
        conn.putrequest("PUT", "/client/history")
        conn.putheader("User-Agent", "gzip")
        conn.putheader("Accept-Encoding", "gzip")
        conn.putheader("Connection", "keep-alive")
        conn.putheader("Content-Type", "text/plain")
        conn.putheader("Transfer-Encoding", "chunked")
        conn.putheader("Expect", "100-continue")
        conn.putheader("Accept", "*/*")
        conn.endheaders()

        # Send client history length.
        conn.send(str(log_entries) + "\r\n")
        
        progress_dialog = self.ui.get_progress_dialog()
        progress_dialog.set_range(0, log_entries)
        progress_dialog.set_text("Sending client history to the server...")
        count = 0
        for log_entry in self.database.get_log_entries_to_sync_for(\
            self.server_id):
            conn.send(self.synchroniser.log_entry_to_XML(log_entry) + "\r\n")
            count += 1
            progress_dialog.set_value(count)
        self.ui.status_bar_message("Waiting for the server to complete...")
        response = conn.getresponse()
        # TODO: analyze response from server side.
        response.read()

    def get_number_of_server_log_entries_to_sync(self):
        try:
            return int(urllib2.urlopen(\
                self.url + "/number/of/server/log/entries/to/sync").read())
        except urllib2.URLError, error:
            raise SyncError("Get number of server log entries to sync: " \
                + str(error))

    def get_server_history(self):
        log_entries = self.get_number_of_server_log_entries_to_sync()
        self.ui.status_bar_message("Applying server history...")
        progress_dialog = self.ui.get_progress_dialog()
        progress_dialog.set_range(0, log_entries)
        progress_dialog.set_text("Applying server history...")
        try:
            response = urllib2.urlopen(self.url + "/server/history")
            count = 0
            while count != log_entries:
                chunk = response.readline()
                self.database.apply_log_entry(\
                    self.synchroniser.XML_to_log_entry(chunk))
                count += 1
                progress_dialog.set_value(count)
        except urllib2.URLError, error:
            raise SyncError("Getting server history: " + str(error))
        progress_dialog.set_value(log_entries)
            
    def get_media_file(self, fname):
        try:
            response = urllib2.urlopen(\
                self.url + "/server/media?fname=%s" % fname)
            data = response.read()
            if data != "CANCEL":
                fobj = open(os.path.join(self.config.mediadir(), fname), "w")
                fobj.write(data)
                fobj.close()
        except urllib2.URLError, error:
            raise SyncError("Getting server media: " + str(error))

    def send_media_file(self, fname):
        mfile = open(os.path.join(self.config.mediadir(), fname), "r")
        data = mfile.read()
        mfile.close()
        try:
            request = PutRequest(self.url + "/client/media?fname=%s" % \
                os.path.basename(fname), data)
            request.add_header("CONTENT_LENGTH", len(data))
            response = urllib2.urlopen(request)
            if response.read() != "OK":
                raise SyncError("Sending client media: error on server side.")
        except urllib2.URLError, error:
            raise SyncError("Sending client media: " + str(error))

    def send_finish_request(self):
        self.ui.status_bar_message("Waiting for the server to complete...")
        try:
            if urllib2.urlopen(self.url + "/sync/finish").read() != "OK":
                raise SyncError("Finishing sync: error on server side.")
        except urllib2.URLError, error:
            raise SyncError("Finishing syncing: " + str(error))
        self.database.update_last_sync_log_entry_for(self.server_id)
            
