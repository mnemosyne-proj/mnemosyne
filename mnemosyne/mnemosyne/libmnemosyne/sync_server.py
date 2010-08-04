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
    'unload_database' too, because these will be subject to threading issues
    as well.

    """

    program_name = "Mnemosyne"
    program_version = mnemosyne.version.version

    def __init__(self, component_manager, ui):
        Component.__init__(self, component_manager)
        Server.__init__(self, self.config().machine_id(),
            self.config()["sync_server_port"], ui)
    
    def authorise(self, username, password):
        return username == self.config()["sync_server_username"] and \
               password == self.config()["sync_server_password"]
    
    def load_database(self, database_name):
        self.previous_database = self.config()["path"]   
        if self.previous_database != database_name:
            if not os.path.exists(expand_path(database_name,
                self.config().basedir)):
                self.database().new(database_name)
            else:
                self.database().load(database_name)
        return self.database()
    
    def unload_database(self, database):
        self.database().load(self.previous_database)
        self.log().loaded_database()
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().update_dialog(redraw_all=True)

