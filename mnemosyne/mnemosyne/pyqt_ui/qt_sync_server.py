#
# qt_sync_server.py <Peter.Bienstman@UGent.be>
#

import os
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
database_released = QtCore.QWaitCondition()


class ServerThread(QtCore.QThread, SyncServer):
    
    """When a sync request comes in, the main thread will release the
    database connection, which will be recreated in the server thread. After
    the sync is finished, the server thread will release the database
    connection again.
    
    We need to care of the three different situations where the server needs
    to call 'unload_database':

     - after a successful sync (the easy case).
     - after a sync server error. For that reason, the openSM2sync server is
       written such that all exceptions are caught and also result in
       'unload_database' being called.
     - when the client disappears halfway through the sync, and the user of
       the server database wants to go on using it. For that reason,
       libmnemosyne calls 'flush_sync_server' before each GUI action.

    Also note that in Qt, we cannot do GUI updates in the server thread, so we
    use the signal/slot mechanism to notify the main thread to do the
    necessary GUI operations.

    """
    
    sync_started_signal = QtCore.pyqtSignal()
    sync_ended_signal = QtCore.pyqtSignal()
    error_signal = QtCore.pyqtSignal(QtCore.QString)
    set_progress_text_signal = QtCore.pyqtSignal(QtCore.QString)
    set_progress_range_signal = QtCore.pyqtSignal(int, int)
    set_progress_value_signal = QtCore.pyqtSignal(int)    
    close_progress_signal = QtCore.pyqtSignal()
    
    def __init__(self, component_manager):
        QtCore.QThread.__init__(self)
        SyncServer.__init__(self, component_manager, self)

    def run(self):
        import select
        while not self.stopped:
            if select.select([self.socket], [], [], 0.25)[0]:
                self.handle_request()
        self.socket.close()

        mutex.lock()
        import sys; sys.stderr.write("stopped!")
        self.terminate_all_sessions()
        self.database().release_connection()
        database_released.wakeAll()
        mutex.unlock()

    def open_database(self, database_name):
        mutex.lock()
        self.sync_started_signal.emit()
        if self.database().is_loaded():
            database_released.wait(mutex)
        mutex.unlock()
        previous_database = self.config()["path"]      
        if previous_database != database_name:
            if not os.path.exists(expand_path(database_name,
                self.config().basedir)):
                self.database().new(database_name)
            else:
                self.database().load(database_name)
        return self.database()

    def unload_database(self, database):
        mutex.lock()
        self.database().release_connection()
        self.sync_ended_signal.emit()
        mutex.unlock()
        
    def error_box(self, error):
        self.error_signal.emit(error)

    def set_progress_text(self, text):
        self.set_progress_text_signal.emit(text)
        
    def set_progress_range(self, minimum, maximum):
        self.set_progress_range_signal.emit(minimum, maximum)        

    def set_progress_value(self, value):
        self.set_progress_value_signal.emit(value) 

    def close_progress(self):
        self.close_progress_signal.emit()

        
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
            self.thread.sync_started_signal.connect(\
                self.unload_database)
            self.thread.sync_ended_signal.connect(\
                self.load_database)
            self.thread.error_signal.connect(\
                self.main_widget().error_box)
            self.thread.set_progress_text_signal.connect(\
                self.main_widget().set_progress_text)
            self.thread.set_progress_range_signal.connect(\
                self.main_widget().set_progress_range)
            self.thread.set_progress_value_signal.connect(\
                self.main_widget().set_progress_value)
            self.thread.close_progress_signal.connect(\
                self.main_widget().close_progress)
            self.thread.start()
            
    def unload_database(self):
        mutex.lock()
        self.previous_database = self.config()["path"]
        self.database().release_connection()
        database_released.wakeAll()
        mutex.unlock()

    def load_database(self):
        mutex.lock()
        self.database().load(self.previous_database)
        self.log().loaded_database()
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().update_dialog(redraw_all=True)
        mutex.unlock()

    def stop_server(self):
        mutex.lock()
        self.thread.stopped = True
        if self.database().is_loaded():
            database_released.wait(mutex)
        mutex.unlock()       
        self.thread.wait()
        self.thread = None
        
    def flush_sync_server(self):
        if not self.thread or len(self.thread.sessions) == 0:
            return
        # The server has the database.
        self.stop_server()
        self.activate()
            
    def deactivate(self):
        # We have the database.
        if not self.thread:
            return
        self.stop_server()

        
