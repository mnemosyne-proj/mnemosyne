#
# client.py - Max Usachev <maxusachev@gmail.com>
#             Ed Bartosh <bartosh@gmail.com>
#             Peter Bienstman <Peter.Bienstman@UGent.be>
#

import os
import tarfile
import urllib2
import httplib
from urlparse import urlparse
from xml.etree import cElementTree

from utils import tar_file_size
from data_format import DataFormat


# Avoid delays caused by Nagle's algorithm.
# http://www.cmlenz.net/archives/2008/03/python-httplib-performance-problems

import socket
realsocket = socket.socket
def socketwrap(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0):
    sockobj = realsocket(family, type, proto)
    sockobj.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    return sockobj
socket.socket = socketwrap


# Implement PUT request in urllib2, as needed by the RESTful API.

class PutRequest(urllib2.Request):
    
    """Implement PUT request in urllib2, as needed by the RESTful API."""
    
    def get_method(self):
        return "PUT"

class SyncError(Exception):
    pass


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
        try:
            client_info = {"username": username, "password": password,
                "id": self.id, "program_name": self.program_name,
                "program_version": self.program_version,
                "capabilities": self.capabilities,
                "database_name": self.database.name()}
            response = urllib2.urlopen(PutRequest(self.url + "/login",
                self.data_format.repr_partner_info(client_info) + "\n")).read()
            if response == "403 Forbidden":
                raise SyncError("Wrong username or password.")
            self.server_info = self.data_format.parse_partner_info(response)
            self.database.create_partnership_if_needed_for(self.server_info["id"])
        except Exception, exception:
            raise SyncError("login: " + str(exception))
        
    def put_client_log_entries(self):
        self.ui.status_bar_message("Sending log entries to server...")
        number_of_entries = self.database.number_of_log_entries_to_sync_for(\
            self.server_info["id"])
        if number_of_entries == 0:
            return
        # Send actual log entries across in a streaming manner.
        # Normally, one would use "Transfer-Encoding: chunked" for that, but
        # chunked requests are not supported by the WSGI 1.x standard.
        # However, it seems we can get around sending a Content-Length header
        # if the server knows when the datastream ends. We use the data format
        # footer as a sentinel for that.
        # As the first line in the stream, we send across the number of log
        # entries, so that the other side can track progress.
        # We also buffer the stream until we have sufficient data to send, in
        # order to improve throughput.
        parsed_url = urlparse(self.url) 
        conn = httplib.HTTPConnection(parsed_url.hostname, parsed_url.port)
        conn.putrequest("PUT", "/client/log_entries")
        conn.endheaders()
        progress_dialog = self.ui.get_progress_dialog()
        progress_dialog.set_range(0, number_of_entries)
        progress_dialog.set_text("Sending log entries to server...")  
        count = 0
        BUFFER_SIZE = 8192
        buffer = str(number_of_entries) + "\n"
        buffer += self.data_format.log_entries_header        
        for log_entry in self.database.log_entries_to_sync_for(\
            self.server_info["id"]):
            buffer += self.data_format.repr_log_entry(log_entry)
            if len(buffer) > BUFFER_SIZE:
                conn.send(buffer.encode("utf-8"))
                buffer = ""
            count += 1
            progress_dialog.set_value(count)
        buffer += self.data_format.log_entries_footer
        conn.send(buffer.encode("utf-8"))
        self.ui.status_bar_message("Waiting for server to complete...")
        if conn.getresponse().read() != "OK":
            raise SyncError("Error sending log entries to server.")
        
    def get_server_log_entries(self):
        self.ui.status_bar_message("Getting server log entries...")       
        try:
            response = urllib2.urlopen(self.url + "/server/log_entries")
            number_of_entries = int(response.readline())
            progress_dialog = self.ui.get_progress_dialog()
            progress_dialog.set_range(0, number_of_entries)
            progress_dialog.set_text("Getting server log entries...")            
            count = 0
            for log_entry in self.data_format.parse_log_entries(response):
                self.database.apply_log_entry(log_entry)
                count += 1
                progress_dialog.set_value(count)
            progress_dialog.set_value(number_of_entries)
        except urllib2.URLError, error:
            raise SyncError("Getting server log entries: " + str(error))
        
    def put_client_media_files(self):
        self.ui.status_bar_message("Sending media files to server...")
        # Size of tar archive.
        filenames = self.database.media_filenames_to_sync_for(\
            self.server_info["id"])
        size = tar_file_size(self.database.mediadir(), filenames)
        if size == 0:
            return
        parsed_url = urlparse(self.url)
        conn = httplib.HTTPConnection(parsed_url.hostname, parsed_url.port)
        conn.putrequest("PUT", "/client/media/files")
        conn.endheaders()     
        socket = conn.sock.makefile("wb", bufsize=8192)
        socket.write(str(size) + "\n")
        # Bundle the media files in a single tar stream, and send it over a
        # buffered socket in order to save memory. Note that this bypasses
        # httplib.HTTPConnection.send.
        saved_path = os.getcwdu()
        os.chdir(self.database.mediadir())
        tar_pipe = tarfile.open(mode="w|",  # Open in streaming mode.
             format=tarfile.PAX_FORMAT, fileobj=socket)
        for filename in filenames:
            tar_pipe.add(filename)
        tar_pipe.close()
        os.chdir(saved_path)
        if conn.getresponse().read() != "OK":
            raise SyncError("Error sending media files to server.")

    def get_server_media_files(self):
        self.ui.status_bar_message("Receiving server media files...")
        try:
            response = urllib2.urlopen(self.url + "/server/media/files")
            size = int(response.readline())
            if size == 0:
                return
            tar_pipe = tarfile.open(mode="r|", fileobj=response)
            # Work around http://bugs.python.org/issue7693.
            tar_pipe.extractall(self.database.mediadir().encode("utf-8"))
        except Exception, error:
            raise SyncError("Getting server media files: " + str(error))

    def finish_request(self):
        self.ui.status_bar_message("Waiting for the server to complete...")
        try:
            if urllib2.urlopen(self.url + "/sync/finish").read() != "OK":
                raise SyncError("Sync finish: error on server side.")
        except urllib2.URLError, error:
            raise SyncError("Sync finish: " + str(error))
        self.database.update_last_sync_log_entry_for(self.server_info["id"])
            
