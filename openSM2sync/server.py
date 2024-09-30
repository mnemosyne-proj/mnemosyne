#
# server.py - Max Usachev <maxusachev@gmail.com>
#             Ed Bartosh <bartosh@gmail.com>
#             Peter Bienstman <Peter.Bienstman@gmail.com>

import os
import sys
import time
import types
import select
import socket
import urllib
import tarfile
import http.client
import tempfile

from .partner import Partner
from .log_entry import EventTypes
from .text_formats.xml_format import XMLFormat
from .utils import traceback_string, rand_uuid
import collections


# Register binary formats.

from .binary_formats.mnemosyne_format import MnemosyneFormat
BinaryFormats = [MnemosyneFormat]


class Session(object):

    """Very basic session support.

    Note that although the current code supports multiple open sessions at
    once, it does not yet support the locking mechanisms to make this
    thread-safe.

    In order to do conflict resolution easily, one of the sync partners has to
    have both logs in memory. We do this at the server side, as the client
    could be a resource-limited mobile device.

    """

    def __init__(self, client_info, database):
        self.token = rand_uuid()
        self.client_info = client_info
        self.database = database
        self.client_log = []
        self.client_o_ids = []
        self.number_of_client_entries = None
        self.apply_error = None
        self.expires = time.time() + 60*60
        self.backup_file = self.database.backup()
        self.database.set_sync_partner_info(client_info)

    def is_expired(self):
        return time.time() > self.expires

    def close(self):
        self.database.update_last_log_index_synced_for(\
            self.client_info["machine_id"])
        self.database.save()

    def terminate(self):

        """Restore from backup if the session failed to close normally."""

        if self.backup_file:
            self.database.restore(self.backup_file)


# When Cherrypy wants to stream a binary file using chunked transfer encoding,
# we sometimes know the size of that file beforehand and send it across in a
# header, so that the client can show progress bars.
mnemosyne_content_length = None


class Server(Partner):

    program_name = "unknown-SRS-app"
    program_version = "unknown"
    BUFFER_SIZE = 8192

    # The following setting can be set to False to speed up the syncing
    # process on e.g. Servers which are storage only and where media files
    # cannot be edited.
    check_for_edited_local_media_files = False

    dont_cause_conflict = set([EventTypes.STARTED_PROGRAM,
        EventTypes.STOPPED_PROGRAM, EventTypes.STARTED_SCHEDULER,
        EventTypes.LOADED_DATABASE, EventTypes.SAVED_DATABASE,
        EventTypes.EDITED_CRITERION, EventTypes.WARNED_TOO_MANY_CARDS])

    def __init__(self, machine_id, port, ui):
        self.machine_id = machine_id
        # We only use 1 thread, such that subsequent requests don't run into
        # SQLite access problems.
        from cheroot import wsgi
        self.wsgi_server = wsgi.Server\
            (("0.0.0.0", port), self.wsgi_app, server_name="localhost",
            numthreads=1, timeout=1000)
        Partner.__init__(self, ui)
        self.text_format = XMLFormat()
        self.sessions = {} # {session_token: session}
        self.session_token_for_user = {} # {user_name: session_token}

    def serve_until_stopped(self):
        try:
            self.wsgi_server.start() # Sets self.wsgi_server.ready
        except KeyboardInterrupt:
            self.wsgi_server.stop()

    def wsgi_app(self, environ, start_response):
        # Catch badly formed requests.
        status, method, args  = self.get_method(environ)
        if status != "200 OK":
            response_headers = [("content-type", "text/plain")]
            start_response(status, response_headers)
            return [status]
        # Note that it is no use to wrap the function call in a try/except
        # statement. The reponse could be an iterable, in which case more
        # calls to e.g. 'get_server_log_entries' could follow outside of this
        # function 'wsgi_app'. Any exceptions that occur then will no longer
        # be caught here. Therefore, we need to catch all of our exceptions
        # ourselves at the lowest level.
        global mnemosyne_content_length
        mnemosyne_content_length = None
        data = getattr(self, method)(environ, **args)
        response_headers = [("content-type", self.text_format.mime_type)]
        if mnemosyne_content_length is not None:
            response_headers.append(\
                ("mnemosyne-content-length", str(mnemosyne_content_length)))
        if type(data) == bytes or type(data) == str:
            response_headers.append(("content-length", str(len(data))))
            start_response("200 OK", response_headers)
            return [data]
        else:  # We have an iterator. With a HTTP/1.0 client (i.e. a Mnemosyne
        # client behind an HTTP/1.0 proxy like Squid pre 3.1) we cannot use
        # chunked encoding, so we need to assemble the entire message
        # beforehand. This obviously results in higher memory requirements for
        # the server and less concurrent processing between client and server.
            if environ["SERVER_PROTOCOL"] == "HTTP/1.0":
                message = b"".join(data)
                response_headers.append(("content-length", str(len(message))))
                start_response("200 OK", response_headers)
                return [message]
            else:
                start_response("200 OK", response_headers)
                return data

    def get_method(self, environ):
        # Convert e.g. GET /foo_bar into get_foo_bar.
        method = (environ["REQUEST_METHOD"] + \
                  environ["PATH_INFO"].replace("/", "_")).lower()
        args = urllib.parse.parse_qs(environ["QUERY_STRING"])
        args = dict([(key, val[0]) for key, val in list(args.items())])
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

    # The following functions are not yet thread-safe.

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
        self.ui.show_error(\
            "Sync failed, the next sync will be a full sync.")

    def is_sync_in_progress(self):
        for session_token, session in self.sessions.items():
            if not session.is_expired():
                return True
        return False

    def is_idle(self):

        """No sessions, expired or otherwise."""

        return (len(self.sessions) == 0)

    def expire_old_sessions(self):
        for session_token, session in self.sessions.items():
            if session.is_expired():
                self.terminate_session_with_token(session_token)

    def terminate_all_sessions(self):
        for session_token in self.sessions.keys():
            self.terminate_session_with_token(session_token)

    def handle_error(self, session=None, traceback_string=None):
        print(traceback_string)
        self.ui.close_progress()
        if session:
            self.terminate_session_with_token(session.token)
        if traceback_string:
            if "GeneratorExit" in traceback_string:
                self.ui.show_error("The client terminated the connection.")
            else:
                self.ui.show_error(traceback_string)
            return self.text_format.repr_message("Internal server error",
                traceback_string).encode("utf-8")

    def stop(self):
        self.terminate_all_sessions()
        self.ui.close_progress()
        self.wsgi_server.stop()

    def binary_format_for(self, session):
        for BinaryFormat in BinaryFormats:
            binary_format = BinaryFormat(session.database)
            if binary_format.supports(session.client_info["program_name"],
                session.client_info["program_version"],
                session.client_info["database_version"]):
                return binary_format
        return None

    def supports_binary_transfer(self, session):

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
        return self.text_format.repr_message("OK").encode("utf-8")

    def put_login(self, environ):
        session = None
        try:
            self.ui.set_progress_text("Client logging in...")
            client_info_repr = environ["wsgi.input"].readline()
            client_info = self.text_format.parse_partner_info(\
                client_info_repr)
            if not self.authorise(client_info["username"],
                client_info["password"]):
                self.ui.close_progress()
                return self.text_format.\
                       repr_message("Access denied").encode("utf-8")
            # Close old session waiting in vain for client input.
            # This will also close any session which timed out while
            # trying to log in just before, so we need to make sure the
            # client timeout is long enough for e.g. a NAS which is slow to
            # wake from hibernation.
            old_running_session_token = self.session_token_for_user.\
                get(client_info["username"])
            if old_running_session_token:
                self.terminate_session_with_token(old_running_session_token)
            session = self.create_session(client_info)
            # If the client database is empty, perhaps it was reset, and we
            # need to delete the partnership from our side too.
            if session.client_info["is_database_empty"] == True:
                session.database.remove_partnership_with(\
                    session.client_info["machine_id"])
            # Make sure there are no cycles in the sync graph. Don't worry
            # about this if the database is empty, sinc the previous statement
            # would otherwise cause a spurious error.
            server_in_client_partners = self.machine_id in \
                session.client_info["partners"]
            client_in_server_partners = session.client_info["machine_id"] in \
                session.database.partners()
            if (server_in_client_partners and not client_in_server_partners)\
               or \
               (client_in_server_partners and not server_in_client_partners):
                if not session.client_info["is_database_empty"]:
                    self.terminate_session_with_token(session.token)
                    self.ui.close_progress()
                    return self.text_format.\
                           repr_message("Sync cycle detected").encode("utf-8")
            # Detect the case where a user has copied the entire mnemosyne
            # directory before syncing.
            if session.client_info["machine_id"] == self.machine_id:
                self.terminate_session_with_token(session.token)
                self.ui.close_progress()
                return self.text_format.\
                       repr_message("same machine ids").encode("utf-8")
            # Create partnerships.
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
                "supports_binary_transfer": \
                    self.supports_binary_transfer(session),
                "is_database_empty": session.database.is_empty()}
            # Signal if we need a sync reset after restoring from a backup.
            server_info["sync_reset_needed"] = \
                session.database.is_sync_reset_needed(\
                client_info["machine_id"])
            # Add optional program-specific information.
            server_info = \
                session.database.append_to_sync_partner_info(server_info)
            return self.text_format.repr_partner_info(server_info)\
                   .encode("utf-8")
        except:
            # We need to be really thorough in our exception handling, so as
            # to always revert the database to its last backup if an error
            # occurs. It is important that this happens as soon as possible,
            # especially if this server is being run as a built-in server in a
            # thread in an SRS desktop application.
            # As mentioned before, the error handling should happen here, at
            # the lowest level, and not in e.g. 'wsgi_app'.
            return self.handle_error(session, traceback_string())

    def get_server_check_media_files(self, environ, session_token):
        # We check if files were updated outside of the program, or if
        # media files need to be generated dynamically, e.g. latex. This
        # can generate MEDIA_EDITED log entries, so it should be done first.
        try:
            session = self.sessions[session_token]
            if self.check_for_edited_local_media_files:
                self.ui.set_progress_text("Checking for edited media files...")
                session.database.check_for_edited_media_files()
            # Always create media files, otherwise they are not synced across.
            self.ui.set_progress_text("Dynamically creating media files...")
            session.database.dynamically_create_media_files()
            return self.text_format.repr_message("OK").encode("utf-8")
        except:
            return self.handle_error(session, traceback_string())

    def put_client_log_entries(self, environ, session_token):
        try:
            session = self.sessions[session_token]
            self.ui.set_progress_text("Receiving log entries...")
            socket = environ["wsgi.input"]
            element_loop = self.text_format.parse_log_entries(socket)
            session.number_of_client_entries = int(next(element_loop))
            if session.number_of_client_entries == 0:
                return self.text_format.repr_message("OK").encode("utf-8")
            self.ui.set_progress_range(session.number_of_client_entries)
            self.ui.set_progress_update_interval(\
                session.number_of_client_entries/50)
            for log_entry in element_loop:
                session.client_log.append(log_entry)
                if log_entry["type"] not in self.dont_cause_conflict:
                    if "fname" in log_entry:
                        log_entry["o_id"] = log_entry["fname"]
                    session.client_o_ids.append(log_entry["o_id"])
                self.ui.set_progress_value(len(session.client_log))
            # If we haven't downloaded all entries yet, tell the client
            # it's OK to continue.
            if len(session.client_log) < session.number_of_client_entries:
                return self.text_format.repr_message("Continue").encode("utf-8")
            # Now we have all the data from the client and we can determine
            # whether there are conflicts.
            for log_entry in session.database.log_entries_to_sync_for(\
                session.client_info["machine_id"]):
                if not log_entry:
                    continue  # Irrelevent entry for card-based clients.
                if "fname" in log_entry:
                    log_entry["o_id"] = log_entry["fname"]
                if log_entry["type"] not in self.dont_cause_conflict and \
                    log_entry["o_id"] in session.client_o_ids:
                    return self.text_format.\
                           repr_message("Conflict").encode("utf-8")
            if session.database.is_empty():
                session.database.change_user_id(session.client_info["user_id"])
            return self.text_format.repr_message("OK").encode("utf-8")
        except:
            return self.handle_error(session, traceback_string())

    def put_client_entire_database_binary(self, environ, session_token):
        try:
            session = self.sessions[session_token]
            self.ui.set_progress_text("Getting entire binary database...")
            filename = session.database.path()
            session.database.abandon()
            file_size = int(environ["CONTENT_LENGTH"])
            self.download_binary_file(\
                environ["wsgi.input"], filename, file_size)
            session.database.load(filename)
            session.database.change_user_id(session.client_info["user_id"])
            session.database.create_if_needed_partnership_with(\
                session.client_info["machine_id"])
            session.database.remove_partnership_with(self.machine_id)
            # Next sync with a third party should be a full sync too.
            session.database.reset_partnerships()
            return self.text_format.repr_message("OK").encode("utf-8")
        except:
            return self.handle_error(session, traceback_string())

    def _stream_log_entries(self, log_entries, number_of_entries):
        self.ui.set_progress_range(number_of_entries)
        self.ui.set_progress_update_interval(number_of_entries/50)
        buffer = self.text_format.log_entries_header(number_of_entries)
        for log_entry in log_entries:
            self.ui.increase_progress(1)
            buffer += self.text_format.repr_log_entry(log_entry)
            if len(buffer) > self.BUFFER_SIZE:
                yield buffer.encode("utf-8")
                buffer = ""
        buffer += self.text_format.log_entries_footer()
        yield buffer.encode("utf-8")

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
            for buffer in self._stream_log_entries(log_entries,
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
            print(traceback_string())
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
            for buffer in self._stream_log_entries(log_entries,
                number_of_entries):
                yield buffer
        except:
            yield self.handle_error(session, traceback_string())

    def get_server_entire_database_binary(self, environ, session_token):
        try:
            session = self.sessions[session_token]
            self.ui.set_progress_text("Sending entire binary database...")
            binary_format = self.binary_format_for(session)
            filename = binary_format.binary_filename(\
                session.client_info["store_pregenerated_data"],
                session.client_info["interested_in_old_reps"])
            global mnemosyne_content_length
            mnemosyne_content_length = os.path.getsize(filename)
            # Since we want to modify the headers in this function, we cannot
            # use 'yield' directly to stream content, but have to add one layer
            # of indirection: http://www.cherrypy.org/wiki/ReturnVsYield
            #
            # Since we return an iterator, we also need to re-encapsulate our
            # code in a try block.
            def content():
                try:
                    for buffer in self.stream_binary_file(filename):
                        yield buffer
                    binary_format.clean_up()
                except:
                    yield self.handle_error(session, traceback_string())
            return content()
            # This is a full sync, we don't need to apply client log
            # entries here.
        except:
            return self.handle_error(session, traceback_string())

    def get_server_generate_log_entries_for_settings(\
            self, environ, session_token):
        try:
            session = self.sessions[session_token]
            session.database.generate_log_entries_for_settings()
            return self.text_format.repr_message("OK").encode("utf-8")
        except:
            return self.handle_error(session, traceback_string())

    def put_client_binary_file(self, environ, session_token, filename):
        try:
            session = self.sessions[session_token]
            socket = environ["wsgi.input"]
            size = int(environ["CONTENT_LENGTH"])
            # Make sure a malicious client cannot overwrite anything outside
            # of the media directory.
            filename = filename.replace("../", "").replace("..\\", "")
            filename = filename.replace("/..", "").replace("\\..", "")
            filename = os.path.join(session.database.data_dir(), filename)
            # We don't have progress bars here, as 'put_client_binary_file'
            # gets called too frequently, and this would slow down the UI.
            self.download_binary_file(environ["wsgi.input"], filename, size,
                progress_bar=False)
            return self.text_format.repr_message("OK").encode("utf-8")
        except:
            return self.handle_error(session, traceback_string())

    def get_server_media_filenames(self, environ, session_token,
                                   redownload_all=False):
        try:
            session = self.sessions[session_token]
            global mnemosyne_content_length
            mnemosyne_content_length = 0
            self.ui.set_progress_text("Sending media files...")
            # Send list of filenames in the format <mediadir>/<filename>, i.e.
            # relative to the data_dir. Note we always use / internally.
            subdir = os.path.basename(session.database.media_dir())
            if redownload_all in ["1", "True", "true"]:
                filenames = [subdir + "/" + filename for filename in \
                             session.database.all_media_filenames()]
            else:
                filenames = [subdir + "/" + filename  for filename in \
                             session.database.media_filenames_to_sync_for(\
                                 session.client_info["machine_id"])]
            if len(filenames) == 0:
                return b""
            for filename in filenames:
                mnemosyne_content_length += os.path.getsize((os.path.join(\
                        session.database.data_dir(), filename)))
            return "\n".join(filenames).encode("utf-8")
        except:
            return self.handle_error(session, traceback_string())

    def get_server_archive_filenames(self, environ, session_token):
        try:
            session = self.sessions[session_token]
            global mnemosyne_content_length
            mnemosyne_content_length = 0
            self.ui.set_progress_text("Sending archive files...")
            # Send list of filenames in the format "archive"/<filename>, i.e.
            # relative to the data_dir. Note we always use / internally.
            archive_dir = os.path.join(session.database.data_dir(), "archive")
            if not os.path.exists(archive_dir):
                return b""
            filenames = ["archive/" + filename for filename in \
                         os.listdir(archive_dir) if os.path.isfile\
                         (os.path.join(archive_dir, filename))]
            if len(filenames) == 0:
                return b""
            for filename in filenames:
                mnemosyne_content_length += os.path.getsize(os.path.join(\
                        session.database.data_dir(), filename))
            return "\n".join(filenames).encode("utf-8")
        except:
            return self.handle_error(session, traceback_string())

    def get_server_binary_file(self, environ, session_token, filename):
        try:
            session = self.sessions[session_token]
            global mnemosyne_content_length
            socket = environ["wsgi.input"]
            # Make sure a malicious client cannot access anything outside
            # of the media directory.
            filename = filename.replace("../", "").replace("..\\", "")
            filename = filename.replace("/..", "").replace("\\..", "")
            filename = os.path.join(session.database.data_dir(), filename)
            file_size = os.path.getsize(filename)
            mnemosyne_content_length = file_size
            # Since we want to modify the headers in this function, we cannot
            # use 'yield' directly to stream content, but have to add one layer
            # of indirection: http://www.cherrypy.org/wiki/ReturnVsYield
            #
            # We don't have progress bars here, as 'get_server_media_file'
            # gets called too frequently, and this would slow down the UI.
            #
            # Since we return an iterator, we also need to re-encapsulate our
            # code in a try block.
            def content():
                try:
                    for buffer in self.stream_binary_file(\
                        filename, progress_bar=False):
                        yield buffer
                except:
                    yield self.handle_error(session, traceback_string())
            return content()
        except:
            return self.handle_error(session, traceback_string())

    def get_sync_cancel(self, environ, session_token):
        try:
            self.ui.set_progress_text("Sync cancelled!")
            if session_token != "none":
                self.cancel_session_with_token(session_token)
            self.ui.close_progress()
            return self.text_format.repr_message("OK").encode("utf-8")
        except:
            if session_token != "none":
                session = self.sessions[session_token]
                return self.handle_error(session, traceback_string())

    def get_sync_finish(self, environ, session_token):
        try:
            session = self.sessions[session_token]
            if session.apply_error is not None:
                return self.handle_error(session, session.apply_error)
            self.ui.set_progress_text("Sync finished!")
            self.close_session_with_token(session_token)
            # Now is a good time to garbage-collect dangling sessions.
            self.expire_old_sessions()
            return self.text_format.repr_message("OK").encode("utf-8")
        except:
            return self.handle_error(session, traceback_string())
