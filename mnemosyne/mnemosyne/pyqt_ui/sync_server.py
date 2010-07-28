#
# sync_server.py <Peter.Bienstman@UGent.be>
#

import socket

from PyQt4 import QtCore

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.openSM2sync_server import OpenSM2SyncServer

mutex = QtCore.QMutex()
main_thread_database_loaded = True
wait_for_main_thread_database_unloaded = QtCore.QWaitCondition()


class ServerThread(QtCore.QThread, OpenSM2SyncServer):
    
    sync_started_message = QtCore.pyqtSignal()
    sync_ended_message = QtCore.pyqtSignal()
    information_message = QtCore.pyqtSignal(QtCore.QString)
    error_message = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self, component_manager):
        QtCore.QThread.__init__(self)
        OpenSM2SyncServer.__init__(self, component_manager, self)

    def open_database(self, database_name):
        mutex.lock()
        self.sync_started_message.emit()
        if main_thread_database_loaded:
            wait_for_main_thread_database_unloaded.wait(mutex)

        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
            "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "ProgressDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.main_widget", "MainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.initialise(self.config().basedir, database_name)

        
        mutex.unlock()
        return self.mnemosyne.database()

    def after_sync(self):
        import sys; sys.stderr.write("thread: after sync\n")
        mutex.lock()
        self.mnemosyne.database().save()
        self.sync_ended_message.emit()
        mutex.unlock()
        
    def run(self):
        self.serve_forever()

    def get_progress_dialog(self):
        pass 
            
    def status_bar_message(self, message):
        print message
        
    def information_box(self, info):  
        self.information_message.emit(info)
        
    def error_box(self, error):
        self.error_message.emit(error)       


class SyncServer(Component, QtCore.QObject):

    component_type = "sync_server"

    def __init__(self, component_manager):
        Component.__init__(self, component_manager)
        self.thread = None

    def activate(self):
        if self.config()["run_sync_server"]:
            # Restart the thread to have the new settings take effect.
            self.deactivate()
            try:
                self.thread = ServerThread(self.component_manager)
            except socket.error, (errno, e):
                if errno == 98:
                    self.main_widget().error_box(\
                        _("Unable to start sync server.") + " " + \
    _("There still seems to be an old server running on the requested port.")\
                        + " " + _("Terminate that process and try again."))
                    self.thread = None
                    return
            self.thread.sync_started_message.connect(\
                self.unload_database_before_sync)
            self.thread.sync_ended_message.connect(\
                self.load_database_after_sync)
            self.thread.information_message.connect(\
                self.main_widget().information_box)
            self.thread.error_message.connect(\
                self.main_widget().error_box)
            self.thread.start()
            
    def unload_database_before_sync(self):
        global main_thread_database_loaded
        mutex.lock()
        self.old_database = self.config()["path"]
        self.database().unload()
        main_thread_database_loaded = False
        import sys; sys.stderr.write("main: unloaded\n")
        wait_for_main_thread_database_unloaded.wakeAll()
        mutex.unlock()

    def load_database_after_sync(self):
        global main_thread_database_loaded
        # If we are closing down the program, and there are still dangling
        # sessions in the server, we cannot continue.
        if not self.database():
            return
        mutex.lock()
        self.database().load(self.old_database)
        self.log().loaded_database()
        main_thread_database_loaded = True
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().update_status_bar()
        import sys; sys.stderr.write("main: loaded\n")
        mutex.unlock()

    def flush_sync_server(self):
        global main_thread_database_loaded
        import sys; sys.stderr.write("main: entered flush\n")
        mutex.lock()
        if self.thread:
            self.thread.terminate_all_sessions()

        # TODO: wrap in
        
        if main_thread_database_loaded == False:
            self.database().load(self.old_database)
            self.log().loaded_database()
            main_thread_database_loaded = True
            self.review_controller().reset_but_try_to_keep_current_card()
            self.review_controller().update_status_bar()
            import sys; sys.stderr.write("main: loaded in flush\n")
            
        mutex.unlock()
        
    def deactivate(self):
        if self.thread:
            self.thread.stop()
            self.thread = None
