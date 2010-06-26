#
# client.py - Max Usachev <maxusachev@gmail.com>
#             Ed Bartosh <bartosh@gmail.com>
#             Peter Bienstman <Peter.Bienstman@UGent.be>
#

import os
import tarfile
import httplib
from xml.etree import cElementTree

from utils import tar_file_size
from text_formats.xml_format import XMLFormat


# Avoid delays caused by Nagle's algorithm.
# http://www.cmlenz.net/archives/2008/03/python-httplib-performance-problems

import socket
realsocket = socket.socket
def socketwrap(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0):
    sockobj = realsocket(family, type, proto)
    sockobj.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    return sockobj
socket.socket = socketwrap

# Buffer the response socket.
# http://mail.python.org/pipermail/python-bugs-list/2006-September/035156.html

class HTTPResponse(httplib.HTTPResponse):
               
    def __init__(self, sock, **kw):
        httplib.HTTPResponse.__init__(self, sock, **kw)
        self.fp = sock.makefile("rb") # Was unbuffered: sock.makefile("rb", 0)

httplib.HTTPConnection.response_class = HTTPResponse

class SyncError(Exception):
    pass


BUFFER_SIZE = 8192


class Client(object):
    
    program_name = "unknown-SRS-app"
    program_version = "unknown"
    # The capabilities supported by the client. Note that we assume that the
    # server supports "mnemosyne_dynamic_cards".
    capabilities = "mnemosyne_dynamic_cards"  # "facts", "cards"
    # The following setting can be set to False to speed up the syncing
    # process on e.g. read only mobile clients where the media files don't get
    # updated anyway.
    check_for_updated_media_files = True
    # Setting the following to False will speed up the initial sync, but in that
    # case the client will not have access to all of the review history in order
    # to e.g. display statistics.
    interested_in_old_reps = True
    # On SD cards copying a large database for the backup before sync can take
    # a long time, so we offer reckless users the possibility to skip this.
    do_backup = True
    # Setting this to False will leave all the uploading of anonymous science
    # logs to the sync server. Recommended to set this to False for mobile
    # clients, which are not always guaranteed to have internet connection.
    upload_science_logs = True
    
    def __init__(self, machine_id, database, ui):
        self.machine_id = machine_id
        self.database = database
        self.ui = ui
        self.text_format = XMLFormat()
        self.server_info = {}

    def sync(self, hostname, port, username, password):       
        try:    
            self.ui.status_bar_message("Creating backup...")
            if self.do_backup:
                backup_file = self.database.backup()
            # We check if files were updated outside of the program. This can
            # generate MEDIA_UPDATED log entries, so it should be done first.
            if self.check_for_updated_media_files:
                self.database.check_for_updated_media_files()
            self.login(hostname, port, username, password)
            result = self.put_client_log_entries()
            # Deal with conflict resolution.
            if result == "cancel":
                self.get_sync_cancel()
                return
            elif result == "keep_local":
                pass
                return
            elif result == "keep_remote":
                if self.server_info["supports_binary_log_download"]:
                    self.get_server_entire_database_binary()
                else:
                    self.get_server_entire_database()
                self.get_sync_finish()
                return
            # Normal case.
            self.put_client_media_files()
            self.get_server_media_files()
            if self.database.is_empty() and \
               self.server_info["supports_binary_log_download"]:
                self.get_server_entire_database_binary()
            else:
                self.get_server_log_entries()
            self.get_sync_finish()
        except SyncError, exception:
            if self.do_backup:
                self.database.restore(backup_file)
            self.ui.error_box("Error: " + str(exception))
        else:
            self.ui.information_box("Sync finished!")

    def login(self, hostname, port, username, password):
        self.ui.status_bar_message("Logging in...")
        try:
            client_info = {}
            client_info["username"] = username
            client_info["password"] = password
            client_info["user_id"] = self.database.user_id()
            client_info["machine_id"] = self.machine_id
            client_info["program_name"] = self.program_name
            client_info["program_version"] = self.program_version
            client_info["capabilities"] = self.capabilities
            client_info["database_name"] = self.database.name()
            client_info["partners"] = self.database.partners()
            client_info["interested_in_old_reps"] = self.interested_in_old_reps
            client_info["upload_science_logs"] = self.upload_science_logs            
            # Not yet implemented: downloading cards as pictures.
            client_info["cards_as_pictures"] = "no" # "yes", "non_latin_only"
            client_info["cards_pictures_res"] = "320x200"
            client_info["reset_cards_as_pictures"] = False # True redownloads.
            self.con = httplib.HTTPConnection(hostname, port)
            self.con.request("PUT", "/login",
                self.text_format.repr_partner_info(client_info).\
                    encode("utf-8") + "\n")
            response = self.con.getresponse().read()
            if response == "403 Forbidden":
                raise SyncError("Wrong username or password.")
            if "cycle" in response.lower():
                raise SyncError(\
                    "Sync cycle detected. Sync through intermediate partner.")             
            self.server_info = self.text_format.parse_partner_info(response)
            self.database.set_sync_partner_info(self.server_info)
            if self.database.is_empty():
                self.database.set_user_id(self.server_info["user_id"])
            elif self.server_info["user_id"] != client_info["user_id"]:
                raise SyncError("mismatched user_ids.")
            self.database.create_partnership_if_needed_for(\
                self.server_info["machine_id"])
            self.database.merge_partners(self.server_info["partners"])
        except Exception, exception:
            raise SyncError("login: " + str(exception))
        
    def put_client_log_entries(self):
        self.ui.status_bar_message("Sending log entries to server...")
        number_of_entries = self.database.number_of_log_entries_to_sync_for(\
            self.server_info["machine_id"])
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
        # We also tried compression here, but for typical scenarios that is
        # slightly slower on a WLAN and mobile phone.
        self.con.putrequest("PUT", "/client/log_entries?session_token=%s" \
            % (self.server_info["session_token"], ))
        self.con.endheaders()
        progress_dialog = self.ui.get_progress_dialog()
        progress_dialog.set_range(0, number_of_entries)
        progress_dialog.set_text("Sending log entries to server...")  
        count = 0
        buffer = self.text_format.log_entries_header(number_of_entries)        
        for log_entry in self.database.log_entries_to_sync_for(\
            self.server_info["machine_id"]):
            buffer += self.text_format.repr_log_entry(log_entry)
            if len(buffer) > BUFFER_SIZE:
                self.con.send(buffer.encode("utf-8"))
                buffer = ""
            count += 1
            progress_dialog.set_value(count)
        buffer += self.text_format.log_entries_footer()
        self.con.send(buffer.encode("utf-8"))
        self.ui.status_bar_message("Waiting for server to complete...")
        response = self.con.getresponse().read().lower()
        if "conflict" in response:
            result = self.ui.question_box("Conflicts detected during sync!",
               "Keep local version", "Keep remote version", "Cancel")
            results = {0: "keep_local", 1: "keep_remote", 2: "cancel"}
            return results[result]
        return "OK"
        
    def get_server_log_entries(self):
        self.ui.status_bar_message("Getting server log entries...")
        try:
            if self.upload_science_logs:
                self.database.dump_to_science_log()
            self.con.request("GET", "/server/log_entries?session_token=%s" \
                % (self.server_info["session_token"], ))
            response = self.con.getresponse()
            element_loop = self.text_format.parse_log_entries(response)
            number_of_entries = element_loop.next()
            if number_of_entries == 0:
                return
            progress_dialog = self.ui.get_progress_dialog()
            progress_dialog.set_range(0, number_of_entries)
            progress_dialog.set_text("Getting server log entries...")            
            count = 0
            for log_entry in element_loop:
                self.database.apply_log_entry(log_entry)
                count += 1
                progress_dialog.set_value(count)
            progress_dialog.set_value(number_of_entries)
            # The server will always upload the science logs of the log events
            # which originated at the server side.
            self.database.skip_science_log()
        except Exception, exception:
            raise SyncError("Getting server log entries: " + str(exception))
        
    def get_server_entire_database_binary(self):
        self.ui.status_bar_message("Getting entire binary server database...")
        try:
            filename = self.database.path()
            self.database.abandon()
            new_database = file(filename, "wb")
            self.con.request("GET", "/server/entire_database_binary?" + \
                "session_token=%s" % (self.server_info["session_token"], ))
            response = self.con.getresponse()
            file_size = int(response.fp.readline())
            progress_dialog = self.ui.get_progress_dialog()
            progress_dialog.set_text("Getting entire binary database...")
            progress_dialog.set_range(0, file_size)
            remaining = file_size
            while remaining:
                if remaining < BUFFER_SIZE:
                    new_database.write(response.read(remaining))
                    remaining = 0
                else:
                    new_database.write(response.read(BUFFER_SIZE))
                    remaining -= BUFFER_SIZE
                progress_dialog.set_value(file_size - remaining)
            progress_dialog.set_value(file_size)
            new_database.close()
            self.database.load(filename)
            self.database.create_partnership_if_needed_for(\
                self.server_info["machine_id"])
            self.database.remove_partnership_with_self()
        except Exception, exception:
            raise SyncError("Getting entire binary server database: " \
                + str(exception))
        
    def put_client_media_files(self):
        self.ui.status_bar_message("Sending media files to server...")
        # Size of tar archive.
        filenames = self.database.media_filenames_to_sync_for(\
            self.server_info["machine_id"])
        size = tar_file_size(self.database.mediadir(), filenames)
        if size == 0:
            return
        self.con.putrequest("PUT", "/client/media/files?session_token=%s" \
            % (self.server_info["session_token"], ))
        self.con.endheaders()     
        socket = self.con.sock.makefile("wb", bufsize=BUFFER_SIZE)
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
        if self.con.getresponse().read() != "OK":
            raise SyncError("Error sending media files to server.")

    def get_server_media_files(self):
        self.ui.status_bar_message("Receiving server media files...")
        try:
            self.con.request("GET", "/server/media_files?session_token=%s" \
                % (self.server_info["session_token"], ))
            response = self.con.getresponse()
            size = int(response.fp.readline())
            if size == 0:
                return
            tar_pipe = tarfile.open(mode="r|", fileobj=response)
            # Work around http://bugs.python.org/issue7693.
            tar_pipe.extractall(self.database.mediadir().encode("utf-8"))
        except Exception, exception:
            raise SyncError("Getting server media files: " + str(exception))

    def get_sync_cancel(self):
        self.ui.status_bar_message("Waiting for the server to complete...")
        try:
            self.con.request("GET", "/sync/cancel?session_token=%s" \
                % (self.server_info["session_token"], ))
            response = self.con.getresponse()
            if response.read() != "OK":
                raise SyncError("Sync finish: error on server side.")
        except Exception, exception:
            raise SyncError("Sync finish: " + str(exception))

    def get_sync_finish(self):
        self.ui.status_bar_message("Waiting for the server to complete...")
        try:
            self.con.request("GET", "/sync/finish?session_token=%s" \
                % (self.server_info["session_token"], ))
            response = self.con.getresponse()
            if response.read() != "OK":
                raise SyncError("Sync finish: error on server side.")
            self.database.update_last_log_index_synced_for(\
                self.server_info["machine_id"])
        except Exception, exception:
            raise SyncError("Sync finish: " + str(exception))            
