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
from data_format import DataFormat


class SyncError(Exception):
    pass


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
        self.data_format = DataFormat()
        self.id = "TODO"
        self.server_info = {}

    def sync(self, url, username, password):       
        try:
            self.url = url           
            self.ui.status_bar_message("Creating backup...")
            backup_file = self.database.backup()
            # We let the client check if files were updated outside of the
            # program. This can generate MEDIA_UPDATED log entries, so it
            # should be done first.
            self.database.check_for_updated_media_files()
            self.login(username, password)
            self.handshake()
            self.put_client_log_entries()
            # Here, the server should send a summary of the sync and of
            # conflicts encountered, so here the user will later get the
            # opportunity to cancel the sync.
            self.put_client_media_files()
            self.get_server_media_files()
            self.get_server_log_entries()
            self.finish_request()
        except SyncError, exception:
            self.database.load(backup_file)
            self.ui.error_box("Error: " + str(exception))
        else:
            self.ui.information_box("Sync finished!")

    def login(self, username, password):
        self.ui.status_bar_message("Logging in...")
        request = urllib2.Request(self.url)
        base64string = base64.encodestring("%s:%s" % (username, password))
        request.add_header("AUTHORIZATION", "Basic %s" % base64string)
        try:
            urllib2.urlopen(request).read()
        except urllib2.URLError, error:
            if hasattr(error, "code") and error.code == 403:
                raise SyncError("Wrong login or password.")
            else:
                raise SyncError(str(error.reason))

    def handshake(self):
        self.ui.status_bar_message("Handshaking...")
        try:
            server_info_repr = \
                urllib2.urlopen(self.url + "/server/info").read()
            client_info = {"id": self.id, "program_name": self.program_name,
                "program_version": self.program_version,
                "capabilities": self.capabilities,
                "database_name": self.database.name()}
            response = urllib2.urlopen(PutRequest(self.url + "/client/info",
                self.data_format.repr_partner_info(client_info) + "\n"))
            if response.read() != "OK":
                raise SyncError("Handshaking: error on server side.")
        except urllib2.URLError, error:
            raise SyncError("Handshaking: " + str(error))
        self.server_info = self.data_format.parse_partner_info(server_info_repr)
        self.database.create_partnership_if_needed_for(self.server_info["id"])

    def put_client_media_files(self):
        self.ui.status_bar_message("Sending media files to server...")
        # Size of tar archive.
        filenames = self.database.media_filenames_to_sync_for(\
            self.server_info["id"])
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
        saved_path = os.getcwdu()
        os.chdir(self.database.mediadir())
        tar_pipe = tarfile.open(mode="w|",  # Open in streaming mode.
             format=tarfile.PAX_FORMAT,
             fileobj=conn.sock.makefile("wb", bufsize=8192))
        for filename in filenames:
            tar_pipe.add(filename)
        tar_pipe.close()
        os.chdir(saved_path)
        if conn.getresponse().read() != "OK":
            raise SyncError("Error sending media files to server.")
            
    def put_client_log_entries(self):
        self.ui.status_bar_message("Sending log entries to server...")
        # Number of log entries.
        number_of_entries = self.database.number_of_log_entries_to_sync_for(\
            self.server_info["id"])
        if number_of_entries == 0:
            return
        response = urllib2.urlopen(PutRequest(self.url + \
            "/number/of/client/log/entries/to/sync",
            str(number_of_entries) + "\n"))
        if response.read() != "OK":
            raise SyncError("Error sending log_entries length to server.")
        # Send actual log entries across in a streaming manner.
        # Normally, one would use "Transfer-Encoding: chunked" for that, but
        # chunked requests are not supported by the WSGI 1.x standard.
        # However, it seems we can get around sending a Content-Length header
        # if the server knows when the datastream ends. We use the data format
        # footer  as a sentinel for that.
        parsed_url = urlparse(self.url) 
        conn = httplib.HTTPConnection(parsed_url.hostname, parsed_url.port)
        conn.putrequest("PUT", "/client/log_entries")
        conn.endheaders()
        progress_dialog = self.ui.get_progress_dialog()
        progress_dialog.set_range(0, number_of_entries)
        progress_dialog.set_text("Sending log entries to server...")
        count = 0
        BUFFER_SIZE = 8192
        chunk = self.data_format.log_entries_header        
        for log_entry in self.database.log_entries_to_sync_for(\
            self.server_info["id"]):
            chunk += self.data_format.repr_log_entry(log_entry)
            if len(chunk) > BUFFER_SIZE:
                conn.send(chunk.encode("utf-8"))
                chunk = ""
            count += 1
            progress_dialog.set_value(count)
        chunk += self.data_format.log_entries_footer
        conn.send(chunk.encode("utf-8"))
        self.ui.status_bar_message("Waiting for server to complete...")
        if conn.getresponse().read() != "OK":
            raise SyncError("Error sending log entries to server.")

    def get_server_media_files(self):
        self.ui.status_bar_message("Receiving server media files...")
        try:
            response = urllib2.urlopen(self.url + "/server/media/files/size")
            if response.read() == "0":
                return
            response = urllib2.urlopen(self.url + "/server/media/files")
            tar_pipe = tarfile.open(mode="r|", fileobj=response)
            # Work around http://bugs.python.org/issue7693.
            tar_pipe.extractall(self.database.mediadir().encode("utf-8"))
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
            for log_entry in self.data_format.parse_log_entries(response):
                self.database.apply_log_entry(log_entry)
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
        self.database.update_last_sync_log_entry_for(self.server_info["id"])
            
