#
# sync_server.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.openSM2sync_server import OpenSM2SyncServer


class ServerThread(QtCore.QThread, OpenSM2SyncServer):

    information_message = QtCore.pyqtSignal(QtCore.QString)
    error_message = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self, component_manager):
        QtCore.QThread.__init__(self)
        OpenSM2SyncServer.__init__(self, component_manager, self)
        
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
        
    def information_box(self, error):
        # TODO: can we skip this?
        self.main_widget().information_box(error)
        
    def error_box(self, error):
        self.main_widget().error_box(error)
        self.thread = None

    def activate(self):
        if self.config()["run_sync_server"]:
            # Restart the thread to have the new settings take effect.
            self.deactivate()
            self.thread = ServerThread(self.component_manager)
            self.thread.information_message.connect(self.information_box)
            self.thread.error_message.connect(self.error_box)
            self.thread.start()
        
    def deactivate(self):
        if self.thread:
            self.thread.stop()
            self.thread = None
