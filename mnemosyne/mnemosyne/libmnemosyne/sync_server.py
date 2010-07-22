#
# sync_server.py <Peter.Bienstman@UGent.be>
#

import mnemosyne.version

from threading import Thread
from openSM2sync.server import Server
from mnemosyne.libmnemosyne.component import Component


class SyncServer(Thread, Component, Server):

    component_type = "sync_server"

    def __init__(self, component_manager):
        Thread.__init__(self)
        Component.__init__(self, component_manager)
        self.rogram_name = "Mnemosyne"
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
               password == ["sync_server_password"]

    def open_database(self, database_name):
        self.controller().unload_database_before_sync()
        self.lock.acquire()
        self.controller().load_database_to_sync(database_name)
        return self.database()

    def close_database(self):
        self.database().unload()
        self.lock.release()   
        self.controller().load_database_after_sync()

