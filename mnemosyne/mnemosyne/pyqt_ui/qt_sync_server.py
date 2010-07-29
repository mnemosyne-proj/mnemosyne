#
# qt_sync_server.py <Peter.Bienstman@UGent.be>
#

import socket

from PyQt4 import QtCore

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.sync_server import SyncServer

# The following is some thread synchronisation machinery to ensure that
# either the sync server thread or the main thread is doing database
# operations.

mutex = QtCore.QMutex()
main_thread_database_loaded = True
wait_for_main_thread_database_unloaded = QtCore.QWaitCondition()


class ServerThread(QtCore.QThread, SyncServer):
    
    """When a sync request comes in, the main thread will unload the database.
    Subsequently, the server thread will start a separate Mnemosyne instance
    loading the database to be synced. When the sync is finished, the server
    thread will unload the database, and the main thread will reload its
    original database (which could be different from the one that was synced).
    This way, there is maximum separation between the data of the two threads.

    We need to care of the three different situations where the main database
    needs to be reloaded:

     -after a successful sync (the easy case).
     -after a sync server error. For that reason, the openSM2sync server is
      written such that all exceptions are caught and also result in
      'unload_database' being called.
     -when the client disappears halfway through the sync, and the user of
      the server database wants to go on using it. For that reason,
      libmnemosyne calls 'flush_sync_server' before each GUI action.

    Also note that in Qt, we cannot do GUI updates in the server thread, so we
    use the signal/slot mechanism to notify the main thread to do the
    necessary GUI operations.

    """
    
    sync_started_message = QtCore.pyqtSignal()
    sync_ended_message = QtCore.pyqtSignal()
    error_message = QtCore.pyqtSignal(QtCore.QString)
    set_progress_text_message = QtCore.pyqtSignal(QtCore.QString)
    set_progress_range_message = QtCore.pyqtSignal(int, int)
    set_progress_value_message = QtCore.pyqtSignal(int)    
    
    def __init__(self, component_manager):
        QtCore.QThread.__init__(self)
        SyncServer.__init__(self, component_manager, self)

    def run(self):
        self.serve_forever()

    def open_database(self, database_name):
        mutex.lock()
        self.sync_started_message.emit()
        if main_thread_database_loaded:
            wait_for_main_thread_database_unloaded.wait(mutex)
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
            "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.main_widget", "MainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.initialise(self.config().basedir, database_name)
        mutex.unlock()
        import sys; sys.stderr.write("thread: load database\n")
        return self.mnemosyne.database()

    def unload_database(self, database):
        import sys; sys.stderr.write("thread: unload database\n")
        mutex.lock()
        self.mnemosyne.finalise()
        self.sync_ended_message.emit()
        mutex.unlock()
        
    def error_box(self, error):
        self.error_message.emit(error)

    def set_progress_text(self, text):
        self.set_progress_text_message.emit(text)
    
    def set_progress_range(self, minimum, maximum):
        self.set_progress_range_message.emit(minimum, maximum)        

    def set_progress_value(self, value):
        self.set_progress_value_message.emit(value) 


class QtSyncServer(Component, QtCore.QObject):

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
            self.thread.error_message.connect(\
                self.main_widget().error_box)
            self.thread.set_progress_text_message.connect(\
                self.main_widget().set_progress_text)
            self.thread.set_progress_range_message.connect(\
                self.main_widget().set_progress_range)
            self.thread.set_progress_value_message.connect(\
                self.main_widget().set_progress_value)
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
        import sys; sys.stderr.write("main: reloaded\n")
        mutex.unlock()

    def flush_sync_server(self):
        global main_thread_database_loaded
        import sys; sys.stderr.write("main: entered flush\n")
        mutex.lock()
        if self.thread:
            self.thread.terminate_all_sessions()
        reload_needed = not main_thread_database_loaded
        mutex.unlock()
        if reload_needed:
            self.load_database_after_sync()
            
    def deactivate(self):
        if self.thread:
            self.thread.stop()
            self.thread = None
