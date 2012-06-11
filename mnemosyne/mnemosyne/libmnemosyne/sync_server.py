#
# sync_server.py <Peter.Bienstman@UGent.be>
#

import os
import mnemosyne.version

from openSM2sync.server import Server
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.component import Component


class SyncServer(Component, Server):

    """These are the libmnemosyne-specific parts of the openSH2sync server.
    Code to run the server in a separate thread is not provided here, as this
    is best done at the GUI level in view of the interaction between multiple
    threads and the GUI event loop.

    Also, a GUI will typically want to override/wrap 'load_database' and
    'unload_database', 'flush' too, because these will be subject to threading
    issues as well.

    """

    program_name = "Mnemosyne"
    program_version = mnemosyne.version.version

    def __init__(self, component_manager, ui):
        Component.__init__(self, component_manager)
        Server.__init__(self, self.config().machine_id(),
            self.config()["port_for_sync_as_server"], ui)
        self.check_for_edited_local_media_files = \
            self.config()["check_for_edited_local_media_files"]

    def authorise(self, username, password):
        return username == self.config()["remote_access_username"] and \
               password == self.config()["remote_access_password"]

    def load_database(self, database_name):
        self.previous_database = self.config()["last_database"]
        if self.previous_database != database_name:
            if not os.path.exists(expand_path(database_name,
                self.config().data_dir)):
                self.database().new(database_name)
            else:
                self.database().load(database_name)
        return self.database()

    def unload_database(self, database):
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