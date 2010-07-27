#
# configuration_wdgt_sync_server.py <Peter.Bienstman@UGent.be>
#

import socket
from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.ui_components.configuration_widget import \
     ConfigurationWidget
from mnemosyne.pyqt_ui.ui_configuration_wdgt_sync_server import \
     Ui_ConfigurationWdgtSyncServer


class ConfigurationWdgtSyncServer(QtGui.QWidget,
    Ui_ConfigurationWdgtSyncServer, ConfigurationWidget):

    name = "Sync server"

    def __init__(self, component_manager, parent):
        ConfigurationWidget.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

    def display(self):
        self.run_sync_server.setChecked(self.config()["run_sync_server"])
        self.port.setValue(self.config()["sync_server_port"])
        self.username.setText(self.config()["sync_server_username"])
        self.password.setText(self.config()["sync_server_password"])
            
    def reset_to_defaults(self):
        self.run_sync_server.setChecked(False)
        self.port.setValue(8512)
        self.username.setText("")
        self.password.setText("")
                
    def apply(self):
        self.config()["run_sync_server"] = self.run_sync_server.isChecked()
        self.config()["sync_server_port"] = self.port.value()
        self.config()["sync_server_username"] = self.username.text()
        self.config()["sync_server_password"] = self.password.text()    
        self.component_manager.get_current("sync_server").deactivate() 
        if self.config()["run_sync_server"]:
            self.component_manager.get_current("sync_server").activate()
            # TODO: should only be displayed if there are no errors.
            QtGui.QMessageBox.information(None, _("Mnemosyne"),
               _("Server now running on ") + str(socket.getfqdn()) + ".",
               _("&OK"), "", "", 0, -1)
    
            
