#
# client.py - Max Usachev <maxusachev@gmail.com>
#             Ed Bartosh <bartosh@gmail.com>
#             Peter Bienstman <Peter.Bienstman@gmail.com>
#

import os
import socket
import urllib.request, urllib.parse, urllib.error
import tarfile
import http.client

from .partner import Partner
from .text_formats.xml_format import XMLFormat
from .utils import SyncError, SeriousSyncError, traceback_string

# Register binary formats.

from .binary_formats.mnemosyne_format import MnemosyneFormat
BinaryFormats = [MnemosyneFormat]


class Client(Partner):

    program_name = "unknown-SRS-app"
    program_version = "unknown"
    BUFFER_SIZE = 8192
    # The capabilities supported by the client. Note that we assume that the
    # server supports "mnemosyne_dynamic_cards".
    capabilities = "mnemosyne_dynamic_cards"  # "facts", "cards"
    # The following setting can be set to False to speed up the syncing
    # process on e.g. mobile clients where the media files don't get edited
    # externally.
    check_for_edited_local_media_files = True
    # Setting the following to False will speed up the initial sync, but in that
    # case the client will not have access to all of the review history in order
    # to e.g. display statistics. Also, it will not be possible to keep the
    # local database when there are sync conflicts. If a client makes it
    # possible for the user to change this value, doing so should result in
    # redownloading the entire database from scratch.
    interested_in_old_reps = True
    # Store prerendered question, answer and tag fields in database. The only
    # benefit of this is fast operation for a 'browse cards' dialog which
    # directly operates at the SQL level. If you don't use this, set to False
    # to reduce the database size.
    store_pregenerated_data = True
    # On mobile clients with slow SD cards copying a large database for the
    # backup before sync can take longer than the sync itself, so we offer
    # reckless users the possibility to skip this.
    do_backup = True
    # Setting this to False will leave all the uploading of anonymous science
    # logs to the sync server. Recommended to set this to False for mobile
    # clients, which are not always guaranteed to have an internet connection.
    upload_science_logs = True

    def __init__(self, machine_id, database, ui):
        Partner.__init__(self, ui)
        self.machine_id = machine_id
        self.database = database
        self.text_format = XMLFormat()
        self.server_info = {}
        self.con = None
        self.behind_proxy = None  # Explicit variable for testability.
        self.proxy = None

    def request_connection(self):

        """If we are not behind a proxy, create the connection once and reuse
        it for all requests. If we are behind a proxy, we need to revert to
        HTTP 1.0 and use a separate connection for each request.

        """

        # If we haven't done so, determine whether we're behind a proxy.
        if self.behind_proxy is None:
            import urllib.request, urllib.parse, urllib.error
            proxies = urllib.request.getproxies()
            if "http" in proxies:
                self.behind_proxy = True
                self.proxy = proxies["http"]
            else:
                self.behind_proxy = False
        # Create a new connection or reuse an existing one.
        if self.behind_proxy:
            http.client.HTTPConnection._http_vsn = 10
            http.client.HTTPConnection._http_vsn_str = "HTTP/1.0"
            if self.proxy is not None:
                self.con = http.client.HTTPConnection(self.proxy, self.port)
            else:  # Testsuite has set self.behind_proxy to True to simulate
                # being behind a proxy.
                self.con = http.client.HTTPConnection(self.server, self.port)
        else:
            http.client.HTTPConnection._http_vsn = 11
            http.client.HTTPConnection._http_vsn_str = "HTTP/1.1"
            if not self.con:
                self.con = http.client.HTTPConnection(self.server, self.port)

    def url(self, url_string):
        if self.behind_proxy and self.proxy:
            url_string = self.server + ":/" + url_string
        return url_string

    def sync(self, server, port, username, password):
        try:
            self.server = socket.gethostbyname(server)
            self.port = port
            backup_file = None
            if self.do_backup:
                self.ui.set_progress_text("Creating backup...")
                backup_file = self.database.backup()
            # We check if files were edited outside of the program. This can
            # generate EDITED_MEDIA_FILES log entries, so it should be done
            # first.
            if self.check_for_edited_local_media_files:
                self.ui.set_progress_text("Checking for edited media files...")
                self.database.check_for_edited_media_files()
            # Always create media files, otherwise they are not synced across.
            self.ui.set_progress_text("Dynamically creating media files...")
            self.database.dynamically_create_media_files()
            # Set timeout long enough for e.g. a slow NAS waking from
            # hibernation.
            socket.setdefaulttimeout(60)
            self.login(username, password)
            # Generating media files at the server side could take some time,
            # so we update the timeout.
            self.con = None
            socket.setdefaulttimeout(15*60)
            self.get_server_check_media_files()
            # Do a full sync after either the client or the server has restored
            # from a backup.
            if self.database.is_sync_reset_needed(\
                self.server_info["machine_id"]) or \
                self.server_info["sync_reset_needed"] == True:
                self.resolve_conflicts(restored_from_backup=True)
            # First sync, fetch database from server.
            elif self.database.is_empty():
                self.get_server_media_files(redownload_all=True)
                self.get_server_archive_files()
                if self.server_info["supports_binary_transfer"]:
                    self.get_server_entire_database_binary()
                else:
                    self.get_server_entire_database()
                self.get_sync_finish()
                # Fetch config settings.
                self.login(username, password)
                self.get_server_generate_log_entries_for_settings()
                self.get_server_log_entries()
                self.get_sync_finish()
            # First sync, put binary database to server if supported.
            elif not self.database.is_empty() and \
                    self.server_info["is_database_empty"] and \
                    self.supports_binary_upload():
                self.put_client_media_files(reupload_all=True)
                self.put_client_archive_files()
                self.put_client_entire_database_binary()
                self.get_sync_finish()
                # Upload config settings.
                self.login(username, password)
                self.database.generate_log_entries_for_settings()
                self.put_client_log_entries()
                self.get_server_log_entries()
                self.get_sync_finish()
            else:
                # Upload local changes and check for conflicts.
                result = self.put_client_log_entries()
                if result == "OK":
                    # We always need to put the client media files, regardless
                    # of self.check_for_edited_local_media_files, as there could
                    # be entirely new media files.
                    self.put_client_media_files()
                    self.get_server_media_files()
                    self.get_server_log_entries()
                    self.get_sync_finish()
                else:
                    self.resolve_conflicts()
            self.ui.close_progress()
            self.ui.show_information("Sync finished!")
        except Exception as exception:
            self.ui.close_progress()
            serious = True
            if type(exception) == type(socket.timeout()):
                self.ui.show_error("Timeout while waiting for server!")
            elif type(exception) == type(socket.gaierror()):
                self.ui.show_error("Could not find server!")
                serious = False
            elif type(exception) == type(SyncError()):
                self.ui.show_error(str(exception))
                serious = False
            elif type(exception) == type(SeriousSyncError()):
                self.ui.show_error(str(exception))
            else:
                self.ui.show_error(traceback_string())
            if serious and self.do_backup:
                # Only serious errors should result in the need for a full
                # sync next time.
                self.ui.show_error(\
                    "Sync failed, the next sync will be a full sync.")
                if backup_file:
                    self.database.restore(backup_file)
        finally:

            # TMP: preparation for future fix
            #self.get_sync_cancel()


            if self.con:
                self.con.close()
            self.ui.close_progress()

    def supports_binary_upload(self):
        return self.capabilities == "mnemosyne_dynamic_cards" and \
            self.interested_in_old_reps and self.store_pregenerated_data and \
            self.program_name == self.server_info["program_name"] and \
            self.database.version == self.server_info["database_version"]

    def resolve_conflicts(self, restored_from_backup=False):
        if restored_from_backup:
            message = "The database was restored from a backup, either " + \
    "automatically because of an aborted sync or manually by " + \
    "the user.\nFor safety, a full sync of cards and history needs to happen and " + \
    "you need to choose which copy of the database to keep and " + \
    "which copy to discard.\n"
        else:
            message = "Conflicts detected during sync! This typically happens if you review the same card on both machines. Choose which version of the entire database (cards + history) to keep and which version to discard."
        # Ask for conflict resolution direction.
        if self.supports_binary_upload():
            result = self.ui.show_question(message,
                "Keep local version", "Fetch remote version", "Cancel")
            results = {0: "KEEP_LOCAL", 1: "KEEP_REMOTE", 2: "CANCEL"}
            result = results[result]
        else:
            message += " " + "Your local client uses a different software version or only stores part of the remote server database, so you can only fetch the remote version."
            result = self.ui.show_question(message,
                "Fetch remote version", "Cancel", "")
            results = {0: "KEEP_REMOTE", 1: "CANCEL"}
            result = results[result]
        # Keep remote. Reset the partnerships afterwards, such that syncing
        # with a third party will also trigger a full sync.
        if result == "KEEP_REMOTE":
            self.get_server_media_files(redownload_all=True)
            self.get_server_archive_files()
            if self.server_info["supports_binary_transfer"]:
                self.get_server_entire_database_binary()
            else:
                self.get_server_entire_database()
            self.database.reset_partnerships()
            self.get_sync_finish()
        # Keep local.
        elif result == "KEEP_LOCAL":
            self.put_client_media_files(reupload_all=True)
            self.put_client_archive_files()
            self.put_client_entire_database_binary()
            self.get_sync_finish()
        # Cancel.
        elif result == "CANCEL":
            self.get_sync_cancel()

    def _check_response_for_errors(self, response, can_consume_response=True):
        # Check for non-Mnemosyne error messages.
        if response.status != http.client.OK:
            raise SeriousSyncError("Internal server error:\n" + \
                                   str(response.read(), "utf-8"))
        if can_consume_response == False:
            return
        # Check for Mnemosyne error messages.
        message, traceback = self.text_format.parse_message(response.read())
        if "server error" in message.lower():
            raise SeriousSyncError(message + "\n" + traceback)

    def login(self, username, password):
        self.ui.set_progress_text("Logging in...")
        client_info = {}
        client_info["username"] = username
        client_info["password"] = password
        client_info["user_id"] = self.database.user_id()
        client_info["machine_id"] = self.machine_id
        client_info["program_name"] = self.program_name
        client_info["program_version"] = self.program_version
        client_info["database_name"] = self.database.name()
        client_info["database_version"] = self.database.version
        client_info["capabilities"] = self.capabilities
        client_info["partners"] = self.database.partners()
        client_info["interested_in_old_reps"] = self.interested_in_old_reps
        client_info["store_pregenerated_data"] = self.store_pregenerated_data
        client_info["upload_science_logs"] = self.upload_science_logs
        # Signal if the database is empty, so that the server does not give a
        # spurious sync cycle warning if the client database was reset.
        client_info["is_database_empty"] = self.database.is_empty()
        # Not yet implemented: preferred renderer.
        client_info["render_chain"] = ""
        # Add optional program-specific information.
        client_info = self.database.append_to_sync_partner_info(client_info)
        # Try to establish a connection, but don't force a restore from backup
        # if we can't login.
        try:
            self.request_connection()
            self.con.request("PUT", self.url("/login"),
                self.text_format.repr_partner_info(client_info).\
                encode("utf-8") + b"\n")
            response = self.con.getresponse()
        except socket.gaierror:
            raise SyncError("Could not find server!")
        except socket.timeout:
            raise SyncError("Timeout when trying to connect to server!")
        except socket.error as e:
            raise SyncError("Socket error: " + str(e))
        except Exception as e:
            print(e)
            raise SyncError("Could not connect to server!\n\n" \
                            + traceback_string())
        # Check for errors, but don't force a restore from backup if we can't
        # login.
        try:
            self._check_response_for_errors(\
                response, can_consume_response=False)
        except SeriousSyncError:
            raise SyncError("Logging in: server error.")
        response = str(response.read(), "utf-8")
        if "message" in response:
            message, traceback = self.text_format.parse_message(response)
            message = message.lower()
            if "server error" in message:
                raise SyncError("Logging in: server error.")
            if "access denied" in message:
                raise SyncError("Wrong username or password.")
            if "cycle" in message:
                raise SyncError(\
"Sync cycle detected. Please always sync with the same server. Backup and delete the database and resync from scratch if necessary.")
            if "same machine ids" in message:
                raise SyncError(\
"You have manually copied the data directory before sync. Sync needs to start from an empty database.")
        self.server_info = self.text_format.parse_partner_info(response)
        self.database.set_sync_partner_info(self.server_info)
        if self.database.is_empty():
            self.database.change_user_id(self.server_info["user_id"])
        elif self.server_info["user_id"] != client_info["user_id"] and \
            self.server_info["is_database_empty"] == False:
            raise SyncError("Error: mismatched user ids.\n" + \
                "The first sync should happen on an empty database.\n" + \
                "Backup then delete the local database and try again.")
        if self.server_info["database_version"] != client_info["database_version"]:
            raise SyncError("Error: database version mismatch.\n" + \
                "Make sure you are running the latest Mnemosyne version on both devices involved in the sync.")
        self.database.create_if_needed_partnership_with(\
            self.server_info["machine_id"])
        self.database.merge_partners(self.server_info["partners"])

    def get_server_check_media_files(self):
        self.ui.set_progress_text("Asking server to check for updated media files...")
        self.request_connection()
        self.con.request("GET", self.url(\
            "/server_check_media_files?" + \
            "session_token=%s" % (self.server_info["session_token"], )))
        response = self.con.getresponse()
        self._check_response_for_errors(response, can_consume_response=True)

    def put_client_log_entries(self):

        """Contrary to binary files, the size of the log is not known until we
        create it. In order to save memory on mobile devices, we don't want to
        construct the entire log in memory before sending it on to the server.
        However, chunked uploads are in the grey area of the WSGI spec and are
        also not supported by older HTTP 1.0 proxies (e.g. Squid before 3.1).
        Therefore, as a compromise, rather then streaming chunks in a single
        message, we break up the entire log in different messages of size
        self.BUFFER_SIZE.

        """

        number_of_entries = self.database.number_of_log_entries_to_sync_for(\
            self.server_info["machine_id"])
        if number_of_entries == 0:
            return
        self.ui.set_progress_text("Sending log entries...")
        self.ui.set_progress_range(number_of_entries)
        self.ui.set_progress_update_interval(number_of_entries/20)
        buffer = ""
        count = 0
        for log_entry in self.database.log_entries_to_sync_for(\
                self.server_info["machine_id"]):
            buffer += self.text_format.repr_log_entry(log_entry)
            count += 1
            self.ui.increase_progress(1)
            if len(buffer) > self.BUFFER_SIZE or count == number_of_entries:
                buffer = \
                    self.text_format.log_entries_header(number_of_entries) \
                    + buffer + self.text_format.log_entries_footer()
                self.request_connection()
                self.con.request("PUT", self.url(\
                    "/client_log_entries?session_token=%s" \
                    % (self.server_info["session_token"],)),
                    buffer.encode("utf-8"))
                buffer = ""
                response = self.con.getresponse()
                self._check_response_for_errors(response,
                    can_consume_response=False)
                response = response.read()
                message, traceback = self.text_format.parse_message(response)
                message = message.lower()
                if "server error" in message:
                    raise SeriousSyncError(message)
                if "conflict" in message:
                    return "conflict"
        return "OK"

    def put_client_entire_database_binary(self):
        self.ui.set_progress_text("Sending entire binary database...")
        for BinaryFormat in BinaryFormats:
            binary_format = BinaryFormat(self.database)
            if binary_format.supports(self.server_info["program_name"],
                self.server_info["program_version"],
                self.server_info["database_version"]):
                assert self.store_pregenerated_data == True
                assert self.interested_in_old_reps == True
                filename = binary_format.binary_filename(\
                    self.store_pregenerated_data, self.interested_in_old_reps)
                break
        self.request_connection()
        self.con.putrequest("PUT",
                self.url("/client_entire_database_binary?session_token=%s" \
                % (self.server_info["session_token"], )))
        self.con.putheader("content-length", os.path.getsize(filename))
        self.con.endheaders()
        for buffer in self.stream_binary_file(filename):
            self.con.send(buffer)
        binary_format.clean_up()
        self._check_response_for_errors(self.con.getresponse())

    def _download_log_entries(self, stream):
        element_loop = self.text_format.parse_log_entries(stream)
        number_of_entries = int(next(element_loop))
        if number_of_entries == 0:
            return
        self.ui.set_progress_range(number_of_entries)
        self.ui.set_progress_update_interval(number_of_entries/50)
        for log_entry in element_loop:
            self.database.apply_log_entry(log_entry)
            self.ui.increase_progress(1)
        self.ui.set_progress_value(number_of_entries)

    def get_server_log_entries(self):
        self.ui.set_progress_text("Getting log entries...")
        if self.upload_science_logs:
            self.database.dump_to_science_log()
        self.request_connection()
        self.con.request("GET", self.url(\
            "/server_log_entries?session_token=%s" \
            % (self.server_info["session_token"], )))
        response = self.con.getresponse()
        self._check_response_for_errors(response, can_consume_response=False)
        self._download_log_entries(response)
        # The server will always upload the science logs of the log events
        # which originated at the server side.
        self.database.skip_science_log()

    def get_server_entire_database(self):
        self.ui.set_progress_text("Getting entire database...")
        filename = self.database.path()
        # Create a new database. Note that this also resets the
        # partnerships, as required.
        self.database.new(filename)
        self.request_connection()
        self.con.request("GET", self.url("/server_entire_database?" + \
            "session_token=%s" % (self.server_info["session_token"], )))
        response = self.con.getresponse()
        self._check_response_for_errors(response, can_consume_response=False)
        self._download_log_entries(response)
        self.database.load(filename)
        # The server will always upload the science logs of the log events
        # which originated at the server side.
        self.database.skip_science_log()
        # Since we start from a new database, we need to create the
        # partnership again.
        self.database.create_if_needed_partnership_with(\
            self.server_info["machine_id"])

    def get_server_entire_database_binary(self):
        self.ui.set_progress_text("Getting entire binary database...")
        filename = self.database.path()
        self.database.abandon()
        self.request_connection()
        self.con.request("GET", self.url(\
            "/server_entire_database_binary?" + \
            "session_token=%s" % (self.server_info["session_token"], )))
        response = self.con.getresponse()
        self._check_response_for_errors(response, can_consume_response=False)
        file_size = int(response.getheader("mnemosyne-content-length"))
        self.download_binary_file(response, filename, file_size)
        self.database.load(filename)
        self.database.create_if_needed_partnership_with(\
            self.server_info["machine_id"])
        self.database.remove_partnership_with(self.machine_id)

    def get_server_generate_log_entries_for_settings(self):
        self.ui.set_progress_text("Getting settings...")
        self.request_connection()
        self.con.request("GET", self.url(\
            "/server_generate_log_entries_for_settings?" + \
            "session_token=%s" % (self.server_info["session_token"], )))
        response = self.con.getresponse()
        self._check_response_for_errors(response, can_consume_response=True)

    def put_client_media_files(self, reupload_all=False):
        self.ui.set_progress_text("Sending media files...")
        # Get list of filenames in the format <mediadir>/<filename>, i.e.
        # relative to the data_dir. Note we always use / internally.
        subdir = os.path.basename(self.database.media_dir())
        if reupload_all:
            filenames = [subdir + "/" + filename for filename in \
                         self.database.all_media_filenames()]
        else:
            filenames = [subdir + "/" + filename for filename in \
                         self.database.media_filenames_to_sync_for(\
                         self.server_info["machine_id"])]
        # Calculate file size and upload.
        total_size = 0
        for filename in filenames:
            total_size += os.path.getsize(os.path.join(\
                self.database.data_dir(), filename))
        self.put_client_binary_files(filenames, total_size)
        self.ui.close_progress()

    def put_client_archive_files(self):
        archive_dir = os.path.join(self.database.data_dir(), "archive")
        if not os.path.exists(archive_dir):
            return
        # Get list of filenames in the format "archive"/<filename>, i.e.
        # relative to the data_dir. Note we always use / internally.
        self.ui.set_progress_text("Sending archive files...")
        filenames = ["archive/" + filename for filename in \
                     os.listdir(archive_dir) if os.path.isfile\
                     (os.path.join(archive_dir, filename))]
        # Calculate file size and upload.
        total_size = 0
        for filename in filenames:
            total_size += os.path.getsize(os.path.join(\
                self.database.data_dir(), filename))
        self.put_client_binary_files(filenames, total_size)
        self.ui.close_progress()

    def put_client_binary_files(self, filenames, total_size):
        # Filenames are relative to the data_dir.
        self.ui.set_progress_range(total_size)
        self.ui.set_progress_update_interval(total_size/50)
        for filename in filenames:
            self.request_connection()
            #print(filename.encode("utf-8", "surrogateescape"))
            self.con.putrequest("PUT",
                self.url("/client_binary_file?session_token=%s&filename=%s" \
                % (self.server_info["session_token"],
                urllib.parse.quote(filename.encode("utf-8"), ""))))
            full_path = os.path.join(self.database.data_dir(), filename)
            file_size = os.path.getsize(full_path)
            self.con.putheader("content-length", file_size)
            self.con.endheaders()
            for buffer in self.stream_binary_file(full_path, progress_bar=False):
                self.con.send(buffer)
                self.ui.increase_progress(len(buffer))
            self._check_response_for_errors(self.con.getresponse())
        self.ui.set_progress_value(total_size)

    def get_server_media_files(self, redownload_all=False):
        self.ui.set_progress_text("Getting list of media files to download...")
        # Get list of names of all media files to download.
        # Filenames are relative to the data_dir.
        media_url = "/server_media_filenames?session_token=%s" \
            % (self.server_info["session_token"], )
        if redownload_all:
             media_url += "&redownload_all=1"
        self.request_connection()
        self.con.request("GET", self.url(media_url))
        response = self.con.getresponse()
        self._check_response_for_errors(response, can_consume_response=False)
        total_size = int(response.getheader("mnemosyne-content-length"))
        if total_size == 0:
            # Make sure to read the full message, even if it's empty,
            # since we reuse our connection.
            response.read()
            return
        filenames = []
        for filename in response.read().split(b"\n"):
            filenames.append(str(filename, "utf-8"))
        self.ui.set_progress_text("Getting media files...")
        self.get_server_binary_files(filenames, total_size)
        self.ui.close_progress()

    def get_server_archive_files(self):
        self.ui.set_progress_text("Getting list of archive files to download...")
        # Get list of names of all archive files to download.
        # Filenames are relative to the data_dir.
        archive_url = "/server_archive_filenames?session_token=%s" \
            % (self.server_info["session_token"], )
        self.request_connection()
        self.con.request("GET", self.url(archive_url))
        response = self.con.getresponse()
        self._check_response_for_errors(response, can_consume_response=False)
        total_size = int(response.getheader("mnemosyne-content-length"))
        if total_size == 0:
            # Make sure to read the full message, even if it's empty,
            # since we reuse our connection.
            response.read()
            return
        filenames = []
        for filename in response.read().split(b"\n"):
            filenames.append(str(filename, "utf-8"))
        self.ui.set_progress_text("Getting archive files...")
        self.get_server_binary_files(filenames, total_size)
        self.ui.close_progress()

    def get_server_binary_files(self, filenames, total_size):
        self.ui.set_progress_range(total_size)
        self.ui.set_progress_update_interval(total_size/50)
        for filename in filenames:
            self.request_connection()
            self.con.request("GET",
                self.url("/server_binary_file?session_token=%s&filename=%s" \
                % (self.server_info["session_token"],
                urllib.parse.quote(filename.encode("utf-8"), ""))))
            response = self.con.getresponse()
            self._check_response_for_errors(response,
                can_consume_response=False)
            file_size = int(response.getheader("mnemosyne-content-length"))
            # Make sure a malicious server cannot overwrite anything outside
            # of the media directory.
            filename = filename.replace("../", "").replace("..\\", "")
            filename = filename.replace("/..", "").replace("\\..", "")
            filename = os.path.join(self.database.data_dir(), filename)
            self.download_binary_file(response, filename,
                                      file_size, progress_bar=False)
            self.ui.increase_progress(file_size)
        self.ui.set_progress_value(total_size)

    def get_sync_cancel(self):
        self.ui.set_progress_text("Cancelling sync...")
        self.request_connection()
        session_token = self.server_info.get("session_token", "none")
        self.con.request("GET", self.url("/sync_cancel?session_token=%s" \
            % (session_token, )), headers={"connection": "close"})
        self._check_response_for_errors(self.con.getresponse())

    def get_sync_finish(self):
        self.ui.set_progress_text("Finishing sync...")
        self.request_connection()
        self.con.request("GET", self.url("/sync_finish?session_token=%s" \
            % (self.server_info["session_token"], )),
            headers={"connection": "close"})
        self._check_response_for_errors(self.con.getresponse())
        # Only update after we are sure there have been no errors.
        self.database.update_last_log_index_synced_for(\
            self.server_info["machine_id"])
