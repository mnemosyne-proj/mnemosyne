#
# sync_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_sync_dlg import Ui_SyncDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import SyncDialog


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
        # Do actual sync.
        from openSM2sync.client import Client
        import mnemosyne.version
        client = Client(self.config().machine_id(), self.database(),
            self.main_widget())
        client.program_name = "Mnemosyne"
        client.program_version = mnemosyne.version.version
        client.capabilities = "mnemosyne_dynamic_cards"
        client.check_for_updated_media_files = True
        client.interested_in_old_reps = True
        client.do_backup = True
        client.upload_science_logs = True
        client.sync(server, port, username, password)
