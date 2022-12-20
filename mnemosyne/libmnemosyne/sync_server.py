#
# sync_server.py <Peter.Bienstman@gmail.com>
#

import os
import http.client
import threading
import mnemosyne.version
from argon2 import PasswordHasher
from argon2.exceptions import HashingError, VerificationError

from openSM2sync.ui import UI
from openSM2sync.server import Server
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import expand_path, localhost_IP


class SyncServer(Component, Server):

    """libmnemosyne-specific parts of the openSM2sync server."""

    program_name = "Mnemosyne"
    program_version = mnemosyne.version.version

    def __init__(self, **kwds):
        config = kwds["component_manager"].current("config")
        if "server_only" in kwds:
            self.server_only = kwds["server_only"]
            del kwds["server_only"]
        else:
            self.server_only = False
        super().__init__(machine_id=config.machine_id(),
            port=config["sync_server_port"], **kwds)
        self.check_for_edited_local_media_files = \
            self.config()["check_for_edited_local_media_files"]

    def authorization_set_up(self) -> bool:
        auth_username = self.config()["remote_access_username"]
        auth_password = self.config()["remote_access_password"]
        return auth_password != "" and auth_username != ""

    def authorise(self, username, password):
        # We should not be running if authorization is not set up,
        # but check just in case.
        if not self.authorization_set_up() or \
                username != self.config()["remote_access_username"]:
            return False

        ph = PasswordHasher()
        hashed_password = self.config()["remote_access_password"]
        if self.config()["remote_access_password_algo"] == "argon2":
            try:
                ph.verify(hashed_password, password)
                if ph.check_needs_rehash(hashed_password):
                    self.config()["remote_access_password"] = ph.hash(password)
                    self.config().save()
                return True
            except HashingError:
                # Rehashing failed but password was valid
                return True
            except VerificationError:
                return False

        if self.config()["remote_access_password_algo"] == "":
            # Fallback for legacy plaintext password
            try:
                if password != hashed_password:
                    return False
                # Hash the password, plaintext is bad
                self.config()["remote_access_password"] = ph.hash(password)
                self.config()["remote_access_password_algo"] = "argon2"
                self.config().save()
            except HashingError:
                # Automatic hashing failed, but password was valid
                pass
            return True

        # Unsupported hash algorithm
        return False

    def load_database(self, database_name):
        if self.server_only:
            # First see if web server needs to release database.
            try:
                con = http.client.HTTPConnection("127.0.0.1",
                    self.config()["web_server_port"])
                con.request("GET", "/release_database")
                response = con.getresponse()
            except:
                pass
            if not os.path.exists(expand_path(database_name,
                self.config().data_dir)):
                self.database().new(database_name)
            else:
                self.database().load(database_name)
        else:
            self.previous_database = self.config()["last_database"]
            if self.previous_database != database_name:
                if not os.path.exists(expand_path(database_name,
                    self.config().data_dir)):
                    self.database().new(database_name)
                else:
                    self.database().load(database_name)
        return self.database()

    def unload_database(self, database):
        if self.server_only:
            self.database().unload()
        else:
            self.database().load(self.previous_database)
            self.log().loaded_database()
            self.review_controller().reset_but_try_to_keep_current_card()
            self.review_controller().update_dialog(redraw_all=True)

    def flush(self):

        """If there are still dangling sessions (i.e. those waiting in vain
        for more client input) in the sync server, we should flush them and
        make sure they restore from backup before doing anything that could
        change the database (e.g. adding a card). Otherwise, if these
        sessions close later during program shutdown, their backup
        restoration will override the changes.

        """

        self.expire_old_sessions()


class SyncServerThread(threading.Thread, SyncServer):

    """Basic threading implementation of the sync server, suitable for text-
    based UIs. A GUI-based client will want to override several functions
    in SyncServer and SyncServerThread in view of the interaction between
    multiple threads and the GUI event loop.

    """

    def __init__(self, component_manager):
        threading.Thread.__init__(self)
        SyncServer.__init__(self, component_manager=component_manager,
                            ui=UI(), server_only=True)

    def run(self):
        if not self.authorization_set_up():
            print("""Error: Authorization not set up.
If on a headless server, you may use the following commands in the sqlite3 console on config.db to configure authorization:
   update config set value="" where key = "remote_access_password_algo"
   update config set value="'<username>'" where key = "remote_access_username";
   update config set value="'<password>'" where key = "remote_access_password";""")
            return

        # Start server.
        print(("Sync server listening on " + localhost_IP() + ":" + \
            str(self.config()["sync_server_port"])))
        self.serve_until_stopped()
        server_hanging = (len(self.sessions) != 0)
        if server_hanging:
            self.terminate_all_sessions()
            self.database().release_connection()
