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
import cStringIO
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from utils import traceback_string
from partner import Partner, BUFFER_SIZE
from text_formats.xml_format import XMLFormat


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
        self.expires = time.time() + 60*60
        import sys; sys.stderr.write("backup")
        self.backup_file = self.database.backup()
        self.database.set_sync_partner_info(client_info)

    def is_expired(self):
        return time.time() > self.expired

    def close(self):
        import sys; sys.stderr.write("update")
        self.database.update_last_log_index_synced_for(\
            self.client_info["machine_id"])
        self.database.save()

    def terminate(self):

        """Restore from backup if the session failed to close normally."""
        import sys; sys.stderr.write("rollback")
        self.database.restore(self.backup_file)


class Server(WSGIServer, Partner):

    program_name = "unknown-SRS-app"
    program_version = "unknown"

    def __init__(self, machine_id, port, ui):        
        self.machine_id = machine_id
        WSGIServer.__init__(self, (socket.getfqdn(), port), WSGIRequestHandler)
        self.set_app(self.wsgi_app)
        Partner.__init__(self, ui)
        self.text_format = XMLFormat()
        self.stopped = False
        self.sessions = {} # {session_token: session}
        self.session_token_for_user = {} # {user_name: session_token}

    def wsgi_app(self, environ, start_response):
        status, mime, method, args = self.get_method(environ)
        response_headers = [("Content-type", mime)]
        start_response(status, response_headers)
        if method:
            return getattr(self, method)(environ, **args)
        else:
            return status

    def serve_forever(self):
        self.ui.status_bar_message("Waiting for client connection...")
        while not self.stopped:
            if select.select([self.socket], [], [])[0]:
                self.handle_request()
        self.socket.close()
        
    def get_method(self, environ):
        # Convert e.g. GET /foo_bar into get_foo_bar.
        method = (environ["REQUEST_METHOD"] + \
                  environ["PATH_INFO"].replace("/", "_")).lower()
        args = cgi.parse_qs(environ["QUERY_STRING"])
        args = dict([(key, val[0]) for key, val in args.iteritems()])
        # Login method.
        if method == "put_login":
            if len(args) == 0:
                return "200 OK", "xml/text", method, args
            else:
                return "400 Bad Request", "text/plain", None, None             
        # See if the token matches.
        if not "session_token" in args or args["session_token"] \
            not in self.sessions:
            return "403 Forbidden", "text/plain", None, None
        # Call the method.
        if hasattr(self, method) and callable(getattr(self, method)):
            return "200 OK", "xml/text", method, args
        else:
            return "404 Not Found", "text/plain", None, None

    def create_session(self, client_info):
        database = self.open_database(client_info["database_name"])
        session = Session(client_info, database)
        self.sessions[session.token] = session
        self.session_token_for_user[client_info["username"]] = session.token
        return session

    def close_session_with_token(self, session_token):
        session = self.sessions[session_token]
        self.after_sync(session)
        session.close()        
        del self.session_token_for_user[session.client_info["username"]]
        del self.sessions[session_token]

    def cancel_session_with_token(self, session_token):

        """Cancel a session at the user's request, e.g. after detecting
        conflicts.

        """
        
        session = self.sessions[session_token]
        self.after_sync(session)
        del self.session_token_for_user[session.client_info["username"]]
        del self.sessions[session_token]
            
    def terminate_session_with_token(self, session_token):

        """Clean up a session which failed to close normally."""

        session = self.sessions[session_token]
        self.after_sync(session)
        session.terminate()        
        del self.session_token_for_user[session.client_info["username"]]
        del self.sessions[session_token]
            
    def stop(self):
        for session_token in self.sessions.keys():
            self.terminate_session_with_token(session_token)
        self.stopped = True
        # Make dummy request for self.stopped to take effect.
        con = httplib.HTTPConnection(socket.getfqdn(), self.server_port)   
        con.request("GET", "dummy_request")
        con.getresponse().read()

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

    def open_database(self, database_name):

        """Returns a database object for the database named 'database_name'.
        Should create the database if it does not exist yet.

        """

        raise NotImplementedError

    def after_sync(self, session):
        pass
    
    # The following are methods that are supported by the server through GET
    # and PUT calls. 'get_foo_bar' gets executed after a 'GET /foo_bar'
    # request. Similarly, 'put_foo_bar' gets executed after a 'PUT /foo_bar'
    # request.

    def put_login(self, environ):
        self.ui.status_bar_message("Client logging in...")
        client_info_repr = environ["wsgi.input"].readline()
        client_info = self.text_format.parse_partner_info(client_info_repr)
        if not self.authorise(client_info["username"],
            client_info["password"]):
            return "403 Forbidden"
        # Close old session if it failed to finish properly.
        old_running_session_token = self.session_token_for_user.\
            get(client_info["username"])
        if old_running_session_token:
            self.terminate_session_with_token(old_running_session_token)
        session = self.create_session(client_info)
        # Make sure there are no cycles in the sync graph.
        server_in_client_partners = self.machine_id in \
            session.client_info["partners"]
        client_in_server_partners = session.client_info["machine_id"] in \
            session.database.partners()      
        if (server_in_client_partners and not client_in_server_partners) or \
           (client_in_server_partners and not server_in_client_partners):
            self.terminate_session_with_token(session.token)                
            return "Cycle detected"
        import sys; sys.stderr.write("create")
        session.database.create_partnership_if_needed_for(\
            client_info["machine_id"])
        session.database.merge_partners(client_info["partners"])
        # Note that we need to send 'user_id' to the client as well, so that the
        # client can make sure the 'user_id's (used to label the anonymous
        # uploaded logs) are consistent across machines.
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
        # generate MEDIA_UPDATED log entries, so it should be done first.
        session.database.check_for_updated_media_files()
        return self.text_format.repr_partner_info(server_info).encode("utf-8")

    def _read_unsized_log_entry_stream(self, stream):
        # Since chunked requests are not supported by the WSGI 1.x standard,
        # the client does not set Content-Length in order to be able to
        # stream the log entries. Therefore, it is our responsability that we
        # consume the entire stream, nothing more and nothing less. For that,
        # we use the file format footer as a sentinel.
        # For simplicity, we also keep the entire stream in memory, as the
        # server is not expected to be resource limited.
        
        sentinel = self.text_format.log_entries_footer()
        lines = []
        line = stream.readline()
        lines.append(line)
        while not line.rstrip().endswith(sentinel.rstrip()):
            line = stream.readline()
            lines.append(line)
        return cStringIO.StringIO("".join(lines))

    def put_client_log_entries(self, environ, session_token):
        self.ui.status_bar_message("Receiving client log entries...")
        session = self.sessions[session_token]
        socket = environ["wsgi.input"]
        # In order to do conflict resolution easily, one of the sync partners
        # has to have both logs in memory. We do this at the server side, as
        # the client could be a resource-limited mobile device.
        session.client_log = []
        client_o_ids = []
        def callback(context, log_entry):
            context["session_client_log"].append(log_entry)
            if log_entry["type"] > 5: # not STARTED_PROGRAM, STOPPED_PROGRAM,
                # STARTED_SCHEDULER, LOADED_DATABASE, SAVED_DATABASE
                if "fname" in log_entry:
                    log_entry["o_id"] = log_entry["fname"]
                context["client_o_ids"].append(log_entry["o_id"])
        context = {"session_client_log": session.client_log,
                   "client_o_ids": client_o_ids}
        self.download_log_entries(self._read_unsized_log_entry_stream(socket),
            "Getting client log entries...", callback, context)        
        # Now we can determine whether there are conflicts.
        for log_entry in session.database.log_entries_to_sync_for(\
            session.client_info["machine_id"]):
            if not log_entry: # Irrelevent entry for card-based clients.
                continue
            if "fname" in log_entry:
                log_entry["o_id"] = log_entry["fname"]
            if log_entry["type"] > 5 and log_entry["o_id"] in client_o_ids:
                return "Conflict"
        return "OK"

    def put_client_entire_database_binary(self, environ, session_token):
        self.ui.status_bar_message("Getting entire binary client database...")
        session = self.sessions[session_token] 
        filename = session.database.path()
        session.database.abandon()
        try:
            self.download_binary_file(filename, environ["wsgi.input"],
                    "Getting entire binary database...")
            session.database.load(filename)
            session.database.create_partnership_if_needed_for(\
                session.client_info["machine_id"])
            session.database.remove_partnership_with_self()
            return "OK"
        except:
            self.ui.error_box(traceback_string())
            self.terminate_session_with_token(session_token)        
            
    def get_server_log_entries(self, environ, session_token):
        self.ui.status_bar_message("Sending log entries to client...")
        session = self.sessions[session_token]
        log_entries = session.database.log_entries_to_sync_for(\
            session.client_info["machine_id"],
            session.client_info["interested_in_old_reps"])
        number_of_entries = session.database.\
            number_of_log_entries_to_sync_for(\
            session.client_info["machine_id"],
            session.client_info["interested_in_old_reps"])
        for buffer in self.stream_log_entries(log_entries, number_of_entries,
            "Sending log entries to client..."):
            yield buffer
        # Now that all the data is underway to the client, we can start
        # applying the client log entries.
        # First, dump to the science log, so that we can skip over the new
        # logs in case the client uploads them.
        try:
            session.database.dump_to_science_log()
            for log_entry in session.client_log:
                session.database.apply_log_entry(log_entry)
            # Skip over the logs that the client promised to upload.
            if session.client_info["upload_science_logs"]:
                session.database.skip_science_log()
        except Exception, exception:
            self.ui.error_box("Error: " + str(exception) + \
                "\n" + traceback_string())
            self.terminate_session_with_token(session_token)
            
    def get_server_entire_database(self, environ, session_token):
        self.ui.status_bar_message("Sending entire database to client...")
        session = self.sessions[session_token]
        session.database.dump_to_science_log()
        log_entries = session.database.all_log_entries(\
            session.client_info["interested_in_old_reps"])
        number_of_entries = session.database.number_of_log_entries(\
            session.client_info["interested_in_old_reps"])
        for buffer in self.stream_log_entries(log_entries, number_of_entries,
            "Sending entire database to client..."):
            yield buffer
            
    def get_server_entire_database_binary(self, environ, session_token):
        self.ui.status_bar_message("Sending entire binary database to client...")
        try:
            session = self.sessions[session_token]
            binary_format = self.binary_format_for(session)
            binary_file, file_size = binary_format.binary_file_and_size(\
                session.client_info["interested_in_old_reps"])
            for buffer in self.stream_binary_file(binary_file, file_size,
                "Sending entire binary database to client..."):
                yield buffer
                binary_format.clean_up()
        except:
            self.ui.error_box(traceback_string())
            yield "CANCEL"
        # This is a full sync, we don't need to apply client log entries here.
            
    def put_client_media_files(self, environ, session_token):
        self.ui.status_bar_message("Receiving client media files...")
        try:
            session = self.sessions[session_token]
            socket = environ["wsgi.input"]
            size = int(socket.readline())
            tar_pipe = tarfile.open(mode="r|", fileobj=socket)
            # Work around http://bugs.python.org/issue7693.
            tar_pipe.extractall(session.database.mediadir().encode("utf-8"))
        except:
            self.ui.error_box(traceback_string())
            return "CANCEL"
        return "OK"
    
    def get_server_media_files(self, environ, session_token,
                               redownload_all=False):
        # Note that for media files, we use tar stream directy for efficiency
        # reasons, and bypass the routines in Partner.
        self.ui.status_bar_message("Sending media files to client...")
        try:
            # Determine files to send across.
            session = self.sessions[session_token]
            if redownload_all in ["1", "True", "true"]:
                filenames = list(session.database.all_media_filenames())
            else:
                filenames = list(session.database.media_filenames_to_sync_for(\
                    session.client_info["machine_id"]))
            # TODO: implement creating pictures from cards, based on the
            # following client_info fields: "cards_as_pictures",
            # "cards_pictures_res", "reset_cards_as_pictures".
            if len(filenames) == 0:
                yield "0\n"
                return
            # Create a temporary tar file with the files.
            tmp_file = tempfile.NamedTemporaryFile(delete=False)
            tmp_file_name = tmp_file.name
            saved_path = os.getcwdu()
            os.chdir(session.database.mediadir())
            tar_pipe = tarfile.open(mode="w|", fileobj=tmp_file,
                bufsize=BUFFER_SIZE, format=tarfile.PAX_FORMAT)
            for filename in filenames:
                tar_pipe.add(filename)
            tar_pipe.close()
            # Stream tar file across.
            tmp_file = file(tmp_file_name, "rb")
            file_size = os.path.getsize(tmp_file_name)
            for buffer in self.stream_binary_file(tmp_file, file_size,
                "Sending media files to client..."):
                yield buffer            
            os.remove(tmp_file_name)
            os.chdir(saved_path)
        except:
            self.ui.error_box(traceback_string())
            yield "CANCEL"
            
    def get_sync_cancel(self, environ, session_token):
        self.ui.status_bar_message("Waiting for client to finish...")
        self.cancel_session_with_token(session_token)
        return "OK"
    
    def get_sync_finish(self, environ, session_token):
        self.ui.status_bar_message("Waiting for client to finish...")
        self.close_session_with_token(session_token) 
        # Now is a good time to garbage-collect dangling sessions.
        for session_token, session in self.sessions.iteritems():
            if session.is_expired():
                self.terminate_session_with_token(session_token)
        return "OK"
    
