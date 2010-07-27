#
# sync_server.py <Peter.Bienstman@UGent.be>
#

import os
import sys

import mnemosyne.version

from threading import Thread
from openSM2sync.server import Server
from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import traceback_string

from PyQt4 import QtCore, QtGui

class Widget(object):

    # We can't easily access the GUI from within a thread, so
    # we go for text-based reporting only...
    
    def status_bar_message(self, message):
        print message
        
    def information_box(self, info):
        print info
        
    def error_box(self, error):
        sys.stderr.write(error)
        

class ServerThread(QtCore.QThread, Component, Server):

    # QT specific stuff
    
    error_message = QtCore.pyqtSignal(QtCore.QString)

    def stop_thread(self):
        self.stop() # server
        
    
    def __init__(self, component_manager):
        Component.__init__(self, component_manager)
        QtCore.QThread.__init__(self, self.main_widget())
        self.program_name = "Mnemosyne"
        self.program_version = mnemosyne.version.version
        
    def run(self):
        try:
            Server.__init__(self, self.config().machine_id(),
                self.config()["sync_server_port"], Widget())
            self.serve_forever()
        except:
            # This should move to the ui object
            self.error_message.emit(_("Failed to start server:") + "\n" + traceback_string())
            
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
        # If we are closing down the program, and there are still dangling
        # sessions in the server, we cannot continue.
        if not self.database():
            return
        self.database().load(self.old_database)
        self.log().loaded_database()
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().update_status_bar()


class SyncServer(Component, QtCore.QObject):

    component_type = "sync_server"

    def __init__(self, component_manager):
        Component.__init__(self, component_manager)
        self.thread = None

    def error_message(self, error):
        self.main_widget().error_box(error)
        self.thread = None

    def activate(self):
        if self.config()["run_sync_server"]:
            # Not all threading systems allow for threads to be restarted,
            # so we always create a new one.
            self.deactivate()
            self.thread = ServerThread(self.component_manager)

            # QT specific
            self.thread.error_message.connect(self.error_message)


            
            self.thread.start()
        
    def deactivate(self):
        if self.thread:
            self.thread.stop_thread()
            self.thread = None
            

