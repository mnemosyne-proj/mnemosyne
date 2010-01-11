#
# client.py - Max Usachev <maxusachev@gmail.com>
#             Ed Bartosh <bartosh@gmail.com>
#             Peter Bienstman <Peter.Bienstman@UGent.be>
#

import os
import base64
import tarfile
import urllib2
import httplib
from urlparse import urlparse
from xml.etree import cElementTree

from utils import tar_file_size
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
            self.put_client_media_files()
            self.put_client_log_entries()
            self.get_server_media_files()
            self.get_server_log_entries()
            self.finish_request()
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
            "database_name='%s'></client>") % (self.id, self.program_name,
            self.program_version, PROTOCOL_VERSION, self.capabilities,
            self.database.database_name())
        try:
            server_params = urllib2.urlopen(self.url + "/server/params").read()
            response = urllib2.urlopen(PutRequest(\
                self.url + "/client/params", client_params + "\n"))
            if response.read() != "OK":
                raise SyncError("Handshaking: error on server side.")
        except urllib2.URLError, error:
            raise SyncError("Handshaking: " + str(error))
        self.synchroniser.set_partner_params(server_params)
        self.server_id = self.synchroniser.partner["id"]
        self.database.create_partnership_if_needed_for(self.server_id)

    def put_client_media_files(self):
        self.ui.status_bar_message("Sending media files to server...")
        # Size of tar archive.
        filenames = list(self.database.media_filenames_to_sync_for(\
            self.server_id))
        size = tar_file_size(self.database.mediadir(), filenames)
        if size == 0:
            return
        response = urllib2.urlopen(PutRequest(self.url + \
            "/client/media/files/size", str(size) + "\n"))
        if response.read() != "OK":
            raise SyncError("Error sending media files size to server.")
        # Actual media files in a tar archive.
        parsed_url = urlparse(self.url)
        conn = httplib.HTTPConnection(parsed_url.hostname, parsed_url.port)
        conn.putrequest("PUT", "/client/media/files")
        conn.endheaders()
        # Stream the tar file over a buffered socket in order to save memory.
        # Note that this bypasses httplib.HTTPConnection.send. 
        tar_pipe = tarfile.open(mode="w|",  # Open in streaming mode.
             format=tarfile.PAX_FORMAT,
             fileobj=conn.sock.makefile("wb", bufsize=4096))
        for filename in filenames:
            tar_pipe.add(filename)
        tar_pipe.close()
        
        import sys; sys.stderr.write(str(conn.getresponse().status))
        #if conn.getresponse().read() != "OK":
        #    print 'failed'
            
    def put_client_log_entries(self):
        self.ui.status_bar_message("Sending log entries to server...")
        # Number of log entries.
        number_of_entries = self.database.number_of_log_entries_to_sync_for(\
            self.server_id)
        if number_of_entries == 0:
            return
        response = urllib2.urlopen(PutRequest(self.url + \
            "/number/of/client/log/entries/to/sync",
            str(number_of_entries) + "\n"))
        if response.read() != "OK":
            raise SyncError("Error sending log_entries length to server.")
        # Actual log entries.    
        parsed_url = urlparse(self.url) 
        conn = httplib.HTTPConnection(parsed_url.hostname, parsed_url.port)
        conn.putrequest("PUT", "/client/log_entries")
        conn.putheader("Connection", "keep-alive")
        conn.putheader("Content-Type", "text/plain")
        conn.putheader("Transfer-Encoding", "chunked")
        conn.putheader("Expect", "100-continue")
        conn.putheader("Accept", "*/*")
        conn.endheaders()
        progress_dialog = self.ui.get_progress_dialog()
        progress_dialog.set_range(0, number_of_entries)
        progress_dialog.set_text("Sending log entries to server...")
        count = 0
        for log_entry in self.database.log_entries_to_sync_for(\
            self.server_id):
            conn.send(self.synchroniser.log_entry_to_XML(log_entry) + "\n")
            count += 1
            progress_dialog.set_value(count)
        self.ui.status_bar_message("Waiting for server to complete...")
        response = conn.getresponse()
        # TODO: analyze response from server side.
        response.read()

    def get_server_media_files(self):
        self.ui.status_bar_message("Receiving server media files...")
        try:
            response = urllib2.urlopen(self.url + "/server/media/files/size")
            if response.read() == "0":
                return
            response = urllib2.urlopen(self.url + "/server/media/files")
            tar_pipe = tarfile.open(mode="r|", fileobj=response)
            tar_pipe.extractall(self.database.mediadir())
        except Exception, error:
            raise SyncError("Getting server media files: " + str(error))            

    def get_server_log_entries(self):
        self.ui.status_bar_message("Applying server log_entries...")
        try:
            log_entries = int(urllib2.urlopen(\
                self.url + "/number/of/server/log/entries/to/sync").read())
        except urllib2.URLError, error:
            raise SyncError("Get number of server log entries to sync: " \
                + str(error))        
        progress_dialog = self.ui.get_progress_dialog()
        progress_dialog.set_range(0, log_entries)
        progress_dialog.set_text("Applying server log_entries...")
        try:
            response = urllib2.urlopen(self.url + "/server/log_entries")
            count = 0
            while count != log_entries:
                chunk = response.readline()
                self.database.apply_log_entry(\
                    self.synchroniser.XML_to_log_entry(chunk))
                count += 1
                progress_dialog.set_value(count)
        except urllib2.URLError, error:
            raise SyncError("Getting server log_entries: " + str(error))
        progress_dialog.set_value(log_entries)

    def finish_request(self):
        self.ui.status_bar_message("Waiting for the server to complete...")
        try:
            if urllib2.urlopen(self.url + "/sync/finish").read() != "OK":
                raise SyncError("Finishing sync: error on server side.")
        except urllib2.URLError, error:
            raise SyncError("Finishing syncing: " + str(error))
        self.database.update_last_sync_log_entry_for(self.server_id)
            
