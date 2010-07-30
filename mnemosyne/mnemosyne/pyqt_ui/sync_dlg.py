#
# sync_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_sync_dlg import Ui_SyncDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import SyncDialog


class SyncThread(QtCore.QThread):
    
    """We do the syncing in a separate thread so that the GUI still stays
    responsive when waiting for the server.

    Note that in Qt, we cannot do GUI updates in the server thread, so we
    use the signal/slot mechanism to notify the main thread to do the
    necessary GUI operations.

    """
    
    information_message = QtCore.pyqtSignal(QtCore.QString)
    error_message = QtCore.pyqtSignal(QtCore.QString)
    question_message = QtCore.pyqtSignal(QtCore.QString, QtCore.QString,
        QtCore.QString, QtCore.QString)
    set_progress_text_message = QtCore.pyqtSignal(QtCore.QString)
    set_progress_range_message = QtCore.pyqtSignal(int, int)
    set_progress_value_message = QtCore.pyqtSignal(int)    
    close_progress_message = QtCore.pyqtSignal()
    
    def __init__(self, machine_id, database, server, port, username, password):
        QtCore.QThread.__init__(self)
        self.machine_id = machine_id
        self.database = database
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        
    def run(self):
        from openSM2sync.client import Client
        import mnemosyne.version
        client = Client(self.machine_id, self.database, self)
        client.program_name = "Mnemosyne"
        client.program_version = mnemosyne.version.version
        client.capabilities = "mnemosyne_dynamic_cards"
        client.check_for_updated_media_files = True
        client.interested_in_old_reps = True
        client.do_backup = True
        client.upload_science_logs = True
        client.sync(self.server, self.port, self.username, self.password)
        
    def information_box(self, message):
        self.information_message.emit(message)
    
    def error_box(self, error):
        self.error_message.emit(error)

    def question_box(self, question, option0, option1, option2):
        self.question_message.emit(question, option0, option1, option2)

    def set_progress_text(self, text):
        self.set_progress_text_message.emit(text)
        
    def set_progress_range(self, minimum, maximum):
        self.set_progress_range_message.emit(minimum, maximum)        

    def set_progress_value(self, value):
        self.set_progress_value_message.emit(value) 

    def close_progress(self):
        self.close_progress_message.emit()


class SyncDlg(QtGui.QDialog, Ui_SyncDlg, SyncDialog):

    def __init__(self, component_manager):
        SyncDialog.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        if not self.config()["sync_help_shown"]:
            QtGui.QMessageBox.information(None, _("Mnemosyne"),
               _("Here, you can sync with a different desktop or a webserver. \nTo sync with a mobile device, first enable a sync server on this computer in the configuration dialog, and then start the sync from the mobile device."),
               _("&OK"), "", "", 0, -1)
            self.config()["sync_help_shown"] = True
        self.server.setText(self.config()["sync_as_client_server"])
        self.port.setValue(self.config()["sync_as_client_port"])
        self.username.setText(self.config()["sync_as_client_username"])
        self.password.setText(self.config()["sync_as_client_password"])
        if self.config()["sync_as_client_server"]:
            self.ok_button.setFocus()
        
    def activate(self):
        self.exec_()
        
    def accept(self):
        QtGui.QDialog.accept(self)
        # Store input for later use.
        server = unicode(self.server.text())
        port = self.port.value()
        username = unicode(self.username.text())
        password = unicode(self.password.text()) 
        self.config()["sync_as_client_server"] = server
        self.config()["sync_as_client_port"] = port
        self.config()["sync_as_client_username"] = username
        self.config()["sync_as_client_password"] = password
        # Do the actual sync in a separate thread.
        thread = SyncThread(self.config().machine_id(), self.database(),
            server, port, username, password)
        thread.information_message.connect(\
            self.main_widget().information_box)
        thread.error_message.connect(\
            self.main_widget().error_box)
        thread.question_message.connect(\
            self.main_widget().question_box)        
        thread.set_progress_text_message.connect(\
            self.main_widget().set_progress_text)
        thread.set_progress_range_message.connect(\
            self.main_widget().set_progress_range)
        thread.set_progress_value_message.connect(\
            self.main_widget().set_progress_value)
        thread.close_progress_message.connect(\
            self.main_widget().close_progress)
        thread.start()
        while thread.isRunning():
            QtGui.QApplication.instance().processEvents()
            thread.wait(100)
