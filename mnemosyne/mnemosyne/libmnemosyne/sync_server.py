#
# sync_server.py <Peter.Bienstman@UGent.be>
#

import os

import mnemosyne.version

from threading import Thread
from openSM2sync.server import Server
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.component import Component


class SyncServer(Thread, Component, Server):

    component_type = "sync_server"

    def __init__(self, component_manager):
        Thread.__init__(self)
        Component.__init__(self, component_manager)
        self.program_name = "Mnemosyne"
        self.program_version = mnemosyne.version.version

    def activate(self):
        if self.config()["run_sync_server"]:
            self.start()

    def run(self):
        Server.__init__(self, self.config().machine_id(),
            self.config()["sync_server_port"], self.main_widget())
        self.serve_forever()
        
    def deactivate(self):       
        if self.is_alive():
            self.stop()
            self.join()
            
    def authorise(self, username, password):
        return username == self.config()["sync_server_username"] and \
               password == self.config()["sync_server_password"]

    def open_database(self, database_name):
        self.old_database = self.config()["path"]      
        if self.old_database != database_name:
            if not os.path.exists(expand_path(database_name,
                self.config().basedir)):
                self.database().new(database_name)
            else:
                self.database().load(database_name)
        return self.database()

    def after_sync(self, session):
        self.database().load(self.old_database)
        self.log().loaded_database()
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().update_status_bar()

