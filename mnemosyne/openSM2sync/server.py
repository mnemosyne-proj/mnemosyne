#
# server.py - Max Usachev <maxusachev@gmail.com>
#             Ed Bartosh <bartosh@gmail.com>
#             Peter Bienstman <Peter.Bienstman@UGent.be>

import os
import sys
import cgi
import uuid
import time
import select
import socket
import tarfile
import httplib
import tempfile
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from utils import traceback_string
from text_formats.xml_format import XMLFormat
from partner import Partner, UnsizedLogEntryStreamReader, BUFFER_SIZE

# Avoid delays caused by Nagle's algorithm.
# http://www.cmlenz.net/archives/2008/03/python-httplib-performance-problems

realsocket = socket.socket
def socketwrap(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0):
    sockobj = realsocket(family, type, proto)
    sockobj.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    return sockobj
socket.socket = socketwrap


# Work around http://bugs.python.org/issue6085.

def not_insane_address_string(self):
    host, port = self.client_address[:2]
    return "%s (no getfqdn)" % host

WSGIRequestHandler.address_string = not_insane_address_string

# Don't pollute our testsuite output.

def dont_log(*kwargs):
    pass

WSGIRequestHandler.log_message = dont_log

# Register binary formats.

from binary_formats.mnemosyne_format import MnemosyneFormat
BinaryFormats = [MnemosyneFormat]


class Session(object):

    def __init__(self, client_info, database):
        self.token = str(uuid.uuid4())
        self.client_info = client_info
        self.database = database
        self.client_log = []
        self.apply_error = None
        self.expires = time.time() + 60*60
        self.backup_file = self.database.backup()
        self.database.set_sync_partner_info(client_info)

    def is_expired(self):
        return time.time() > self.expired

    def close(self):
        self.database.update_last_log_index_synced_for(\
            self.client_info["machine_id"])
        self.database.save()

    def terminate(self):

        """Restore from backup if the session failed to close normally."""

        self.database.restore(self.backup_file)
        

class Server(WSGIServer, Partner):

    program_name = "unknown-SRS-app"
    program_version = "unknown"

    def __init__(self, machine_id, port, ui):        
        self.machine_id = machine_id
        WSGIServer.__init__(self, ("", port), WSGIRequestHandler)
        self.set_app(self.wsgi_app)
        Partner.__init__(self, ui)
        self.text_format = XMLFormat()
        self.stopped = False
        self.sessions = {} # {session_token: session}
        self.session_token_for_user = {} # {user_name: session_token}

    def serve_until_stopped(self):
        while not self.stopped:
            # We time out every 0.25 seconds, so that we changing
            # self.stopped can have an effect.
            if select.select([self.socket], [], [], 0.25)[0]:
                self.handle_request()
        self.socket.close()

    def wsgi_app(self, environ, start_response):
        # Catch badly formed requests.
        status, method, args  = self.get_method(environ)
        if status != "200 OK":
            response_headers = [("Content-type", "text/plain")]
            start_response(status, response_headers)
            return [status]
        # Note that it is no use to wrap the function call in a try/except
        # statement. The reponse could be an iterable, in which case more
        # calls to e.g. 'get_server_log_entries' could follow outside of this
        # function 'wsgi_app'. Any exceptions that occur then will no longer
        # be caught here. Therefore, we need to catch all of our exceptions
        # ourselves at the lowest level.
        response_headers = [("Content-type", self.text_format.mime_type)]
        start_response("200 OK", response_headers)
        return getattr(self, method)(environ, **args)
        
    def get_method(self, environ):
        # Convert e.g. GET /foo_bar into get_foo_bar.
        method = (environ["REQUEST_METHOD"] + \
                  environ["PATH_INFO"].replace("/", "_")).lower()
        args = cgi.parse_qs(environ["QUERY_STRING"])
        args = dict([(key, val[0]) for key, val in args.iteritems()])
        # Login method.
        if method == "put_login" or method == "get_status":
            if len(args) == 0:
                return "200 OK", method, args
            else:
                return "400 Bad Request", None, None             
        # See if the token matches.
        if not "session_token" in args or args["session_token"] \
            not in self.sessions:
            return "403 Forbidden", None, None
        # See if the method exists.
        if hasattr(self, method) and callable(getattr(self, method)):
            return "200 OK", method, args
        else:
            return "404 Not Found", None, None

    def create_session(self, client_info):
        database = self.load_database(client_info["database_name"])
        session = Session(client_info, database)
        self.sessions[session.token] = session
        self.session_token_for_user[client_info["username"]] = session.token
        return session

    def close_session_with_token(self, session_token):
        session = self.sessions[session_token]
        session.close()
        self.unload_database(session.database)        
        del self.session_token_for_user[session.client_info["username"]]
        del self.sessions[session_token]
        self.ui.close_progress()
        
    def cancel_session_with_token(self, session_token):

        """Cancel a session at the user's request, e.g. after detecting
        conflicts.

        """
        
        session = self.sessions[session_token]
        self.unload_database(session.database)
        del self.session_token_for_user[session.client_info["username"]]
        del self.sessions[session_token]
        self.ui.close_progress()
        
    def terminate_session_with_token(self, session_token):

        """Clean up a session which failed to close normally."""

        session = self.sessions[session_token]
        session.terminate()
        self.unload_database(session.database)      
        del self.session_token_for_user[session.client_info["username"]]
        del self.sessions[session_token]
        self.ui.close_progress()
        
    def terminate_all_sessions(self):
        for session_token in self.sessions.keys():
            self.terminate_session_with_token(session_token)
            
    def handle_error(self, session=None, traceback_string=None):
        if session:
            self.terminate_session_with_token(session.token)
        if traceback_string:
            self.ui.error_box(traceback_string)
            return self.text_format.repr_message("Internal server error",
                traceback_string)
    
    def stop(self):
        self.terminate_all_sessions()
        self.stopped = True
        self.ui.close_progress()
        
    def binary_format_for(self, session):
        for BinaryFormat in BinaryFormats:
            binary_format = BinaryFormat(session.database)
            if binary_format.supports(session.client_info["program_name"],
                session.client_info["program_version"],
                session.client_info["database_version"]):
                return binary_format
        return None

    def supports_binary_log_download(self, session):

        """For testability, can easily be overridden by testsuite. """
        
        return self.binary_format_for(session) is not None
    
    # The following functions are to be overridden by the actual server code,
    # to implement e.g. authorisation, storage, ... .

    def authorise(self, username, password):

        """Returns True if 'password' is correct for 'username'."""
        
        raise NotImplementedError

    def load_database(self, database_name):

        """Returns a database object for the database named 'database_name'.
        Should create the database if it does not exist yet.

        """

        raise NotImplementedError

    def unload_database(self, database):

        """Here, there is the possibility for a custom server to do some
        after sync cleanup.

        """
        
        pass
    
    # The following are methods that are supported by the server through GET
    # and PUT calls. 'get_foo_bar' gets executed after a 'GET /foo_bar'
    # request. Similarly, 'put_foo_bar' gets executed after a 'PUT /foo_bar'
    # request.

    def get_status(self, environ):
        return [self.text_format.repr_message("OK")]

    def put_login(self, environ):
        session = None
        try:
            self.ui.set_progress_text("Client logging in...")
            client_info_repr = environ["wsgi.input"].readline()
            client_info = self.text_format.parse_partner_info(\
                client_info_repr)
            if not self.authorise(client_info["username"],
                client_info["password"]):
                return [self.text_format.repr_message("Access denied")]
            # Close old session waiting in vain for client input.
            old_running_session_token = self.session_token_for_user.\
                get(client_info["username"])
            if old_running_session_token:
                self.terminate_session_with_token(old_running_session_token)
            session = self.create_session(client_info)
            # If the client database is empty, perhaps it was reset, and we
            # need to delete the partnership from our side too.
            if session.client_info["database_is_empty"] == True:
                session.database.remove_partnership_with(\
                    session.client_info["machine_id"])
            # Make sure there are no cycles in the sync graph.
            server_in_client_partners = self.machine_id in \
                session.client_info["partners"]
            client_in_server_partners = session.client_info["machine_id"] in \
                session.database.partners()
            if (server_in_client_partners and not client_in_server_partners)\
               or \
               (client_in_server_partners and not server_in_client_partners):
                self.terminate_session_with_token(session.token)                
                return [self.text_format.repr_message("Sync cycle detected")]
            session.database.create_if_needed_partnership_with(\
                client_info["machine_id"])
            session.database.merge_partners(client_info["partners"])
            # Note that we need to send 'user_id' to the client as well, so
            # that the client can make sure the 'user_id's (used to label the
            # anonymous uploaded logs) are consistent across machines.
            server_info = {"user_id": session.database.user_id(),
                "machine_id": self.machine_id,
                "program_name": self.program_name,
                "program_version": self.program_version,
                "database_version": session.database.version,
                "partners": session.database.partners(),
                "session_token": session.token,
                "supports_binary_log_download": \
                    self.supports_binary_log_download(session)}
            # We check if files were updated outside of the program. This can
            # generate MEDIA_EDITED log entries, so it should be done first.
            session.database.check_for_edited_media_files()
            return [self.text_format.repr_partner_info(server_info)\
                   .encode("utf-8")] 
        except:
            # We need to be really thorough in our exception handling, so as
            # to always revert the database to its last backup if an error
            # occurs. It is important that this happens as soon as possible,
            # especially if this server is being run as a built-in server in a
            # thread in an SRS desktop application.
            # As mentioned before, the error handling should happen here, at
            # the lowest level, and not in e.g. 'wsgi_app'.
            return [self.handle_error(session, traceback_string())]

    def put_client_log_entries(self, environ, session_token):
        try:
            session = self.sessions[session_token]
            self.ui.set_progress_text("Receiving log entries...")
            socket = environ["wsgi.input"]
            # In order to do conflict resolution easily, one of the sync
            # partners has to have both logs in memory. We do this at the
            # server side, as the client could be a resource-limited mobile
            # device.
            session.client_log = []
            client_o_ids = []
            def callback(context, log_entry):
                context["session_client_log"].append(log_entry)
                if log_entry["type"] > 5: # not STARTED_PROGRAM,
                    # STOPPED_PROGRAM, STARTED_SCHEDULER, LOADED_DATABASE,
                    # SAVED_DATABASE
                    if "fname" in log_entry:
                        log_entry["o_id"] = log_entry["fname"]
                    context["client_o_ids"].append(log_entry["o_id"])
            context = {"session_client_log": session.client_log,
                       "client_o_ids": client_o_ids}
            adapted_stream = UnsizedLogEntryStreamReader(socket,
                self.text_format.log_entries_footer())
            self.download_log_entries(adapted_stream, callback, context)
            # Now we can determine whether there are conflicts.
            for log_entry in session.database.log_entries_to_sync_for(\
                session.client_info["machine_id"]):
                if not log_entry:
                    continue  # Irrelevent entry for card-based clients.
                if "fname" in log_entry:
                    log_entry["o_id"] = log_entry["fname"]
                if log_entry["type"] > 5 and \
                    log_entry["o_id"] in client_o_ids:
                    return [self.text_format.repr_message("Conflict")]
            return [self.text_format.repr_message("OK")]
        except:
            return [self.handle_error(session, traceback_string())]
        
    def put_client_entire_database_binary(self, environ, session_token):
        try:
            session = self.sessions[session_token] 
            self.ui.set_progress_text("Getting entire binary database...")
            filename = session.database.path()
            session.database.abandon()
            self.download_binary_file(filename, environ["wsgi.input"])
            session.database.load(filename)
            session.database.create_if_needed_partnership_with(\
                session.client_info["machine_id"])
            session.database.remove_partnership_with(self.machine_id)
            return [self.text_format.repr_message("OK")]
        except:
            return [self.handle_error(session, traceback_string())]

    def get_server_log_entries(self, environ, session_token):
        try:
            session = self.sessions[session_token]
            self.ui.set_progress_text("Sending log entries...")
            log_entries = session.database.log_entries_to_sync_for(\
                session.client_info["machine_id"],
                session.client_info["interested_in_old_reps"])
            number_of_entries = session.database.\
                number_of_log_entries_to_sync_for(\
                session.client_info["machine_id"],
                session.client_info["interested_in_old_reps"])
            for buffer in self.stream_log_entries(log_entries,
                number_of_entries):
                yield buffer        
        except:
            yield self.handle_error(session, traceback_string())
        # Now that all the data is underway to the client, we can already
        # start applying the client log entries. If there are errors that
        # occur, we save them and communicate them to the client in
        # 'get_sync_finish'.
        try:    
            self.ui.set_progress_text("Applying log entries...")
            # First, dump to the science log, so that we can skip over the new
            # logs in case the client uploads them.
            session.database.dump_to_science_log()
            for log_entry in session.client_log:
                session.database.apply_log_entry(log_entry)
            # Skip over the logs that the client promised to upload.
            if session.client_info["upload_science_logs"]:
                session.database.skip_science_log()
        except:
            session.apply_error = traceback_string()

    def get_server_entire_database(self, environ, session_token):
        try:
            session = self.sessions[session_token]
            self.ui.set_progress_text("Sending entire database...")
            session.database.dump_to_science_log()
            log_entries = session.database.all_log_entries(\
                session.client_info["interested_in_old_reps"])
            number_of_entries = session.database.number_of_log_entries(\
                session.client_info["interested_in_old_reps"])
            for buffer in self.stream_log_entries(log_entries,
                number_of_entries):
                yield buffer
        except:
            yield self.handle_error(session, traceback_string())

    def get_server_entire_database_binary(self, environ, session_token):
        try:
            session = self.sessions[session_token]
            self.ui.set_progress_text("Sending entire binary database...")
            binary_format = self.binary_format_for(session)
            binary_file, file_size = binary_format.binary_file_and_size(\
                session.client_info["interested_in_old_reps"])
            for buffer in self.stream_binary_file(binary_file, file_size):
                yield buffer
            binary_format.clean_up()
            # This is a full sync, we don't need to apply client log
            # entries here.
        except:
            yield self.handle_error(session, traceback_string())        

    def put_client_media_files(self, environ, session_token):
        try:
            session = self.sessions[session_token]
            self.ui.set_progress_text("Getting media files...")
            socket = environ["wsgi.input"]
            size = int(socket.readline())
            tar_pipe = tarfile.open(mode="r|", fileobj=socket)
            # Work around http://bugs.python.org/issue7693.
            tar_pipe.extractall(session.database.media_dir().encode("utf-8"))
            return [self.text_format.repr_message("OK")]
        except:
            return [self.handle_error(session, traceback_string())]        

    def get_server_media_files(self, environ, session_token,
                               redownload_all=False):
        try:
            session = self.sessions[session_token]
            # Note that for media files, we use tar stream directy for efficiency
            # reasons, and bypass the routines in Partner.
            self.ui.set_progress_text("Sending media files...")
            # Determine files to send across.
            if redownload_all in ["1", "True", "true"]:
                filenames = list(session.database.all_media_filenames())
            else:
                filenames = list(session.database.media_filenames_to_sync_for(\
                    session.client_info["machine_id"]))
            if len(filenames) == 0:
                yield "0\n"
                return
            # Create a temporary tar file with the files.
            tmp_file = tempfile.NamedTemporaryFile(delete=False)
            tmp_file_name = tmp_file.name
            saved_path = os.getcwdu()
            os.chdir(session.database.media_dir())
            tar_pipe = tarfile.open(mode="w|", fileobj=tmp_file,
                bufsize=BUFFER_SIZE, format=tarfile.PAX_FORMAT)
            for filename in filenames:
                tar_pipe.add(filename)
            tar_pipe.close()
            # Stream tar file across.
            tmp_file = file(tmp_file_name, "rb")
            file_size = os.path.getsize(tmp_file_name)
            for buffer in self.stream_binary_file(tmp_file, file_size):
                yield buffer            
            os.remove(tmp_file_name)
            os.chdir(saved_path)
        except:
            yield self.handle_error(session, traceback_string())

    def get_sync_cancel(self, environ, session_token):
        try:
            self.ui.set_progress_text("Sync cancelled!")
            self.cancel_session_with_token(session_token)
            return [self.text_format.repr_message("OK")]
        except:
            session = self.sessions[session_token]
            return [self.handle_error(session, traceback_string())]
        
    def get_sync_finish(self, environ, session_token):           
        try:
            session = self.sessions[session_token]
            if session.apply_error:
                return [self.handle_error(session, session.apply_error)]
            self.ui.set_progress_text("Sync finished!")
            self.close_session_with_token(session_token) 
            # Now is a good time to garbage-collect dangling sessions.
            # Only relevant for multi-user server.
            for session_token, session in self.sessions.iteritems():
                if session.is_expired():
                    self.terminate_session_with_token(session_token)
            return [self.text_format.repr_message("OK")]
        except:
            return [self.handle_error(session, traceback_string())]
