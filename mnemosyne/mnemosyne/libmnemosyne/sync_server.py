#
# sync_server.py <Peter.Bienstman@UGent.be>
#

import os
import httplib
import threading
import mnemosyne.version

from openSM2sync.ui import UI
from openSM2sync.server import Server
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import expand_path, localhost_IP


class SyncServer(Component, Server):

    """libmnemosyne-specific parts of the openSH2sync server."""

    program_name = "Mnemosyne"
    program_version = mnemosyne.version.version

    def __init__(self, component_manager, ui, server_only=False):
        Component.__init__(self, component_manager)
        Server.__init__(self, self.config().machine_id(),
            self.config()["sync_server_port"], ui)
        self.server_only = server_only
        self.check_for_edited_local_media_files = \
            self.config()["check_for_edited_local_media_files"]

    def authorise(self, username, password):
        return username == self.config()["remote_access_username"] and \
               password == self.config()["remote_access_password"]

    def load_database(self, database_name):
        if self.server_only:
            # First see if web server needs to release database.
            try:
                con = httplib.HTTPConnection("127.0.0.1",
                self.config()["web_server_port"])
                con.request("GET", "/release_database")
                response = con.getresponse()
            except:
                pass
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
        SyncServer.__init__(self, component_manager, UI(), server_only=True)

    def run(self):
        print "Sync server listening on " + localhost_IP() + ":" + \
            str(self.config()["sync_server_port"])
        self.serve_until_stopped()
        server_hanging = (len(self.sessions) != 0)
        if server_hanging:
            self.terminate_all_sessions()
            self.database().release_connection()


