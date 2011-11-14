#
# configuration_wdgt_sync_server.py <Peter.Bienstman@UGent.be>
#

import socket
import httplib
from PyQt4 import QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.ui_components.configuration_widget import \
     ConfigurationWidget
from mnemosyne.pyqt_ui.ui_configuration_wdgt_sync_server import \
     Ui_ConfigurationWdgtSyncServer


# Hack to determine local IP.

from openSM2sync.server import realsocket
def localhost_IP():
    s = realsocket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("google.com", 8000))
    return s.getsockname()[0]


class ConfigurationWdgtSyncServer(QtGui.QWidget,
    Ui_ConfigurationWdgtSyncServer, ConfigurationWidget):

    name = _("Sync server")

    def __init__(self, component_manager, parent):
        ConfigurationWidget.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.initially_running = self.is_server_running()
        self.run_sync_server.setChecked(self.config()["run_sync_server"])
        self.port.setValue(self.config()["port_for_sync_as_server"])
        self.username.setText(self.config()["remote_access_username"])
        self.password.setText(self.config()["remote_access_password"])
        self.check_for_edited_local_media_files.setChecked(\
            self.config()["check_for_edited_local_media_files"])
        if self.is_server_running():
            self.server_status.setText(_("Server running on ") + \
                localhost_IP() + ".")
        else:
            self.server_status.setText(_("Server NOT running."))   

    def is_server_running(self):
        timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(0.1)
            con = httplib.HTTPConnection(localhost_IP(),
                self.config()["port_for_sync_as_server"])
            con.request("GET", "/status")
            assert "OK" in con.getresponse().read()
            socket.setdefaulttimeout(timeout)
            return True
        except socket.error:
            socket.setdefaulttimeout(timeout)
            return False

    def reset_to_defaults(self):
        answer = self.main_widget().show_question(\
            _("Reset current tab to defaults?"), _("&Yes"), _("&No"), "")
        if answer == 1:
            return
        self.run_sync_server.setChecked(False)
        self.port.setValue(8512)
        self.username.setText("")
        self.password.setText("")
        self.check_for_edited_local_media_files.setChecked(False)
                
    def apply(self):
        self.config()["run_sync_server"] = self.run_sync_server.isChecked()
        self.config()["port_for_sync_as_server"] = self.port.value()
        self.config()["remote_access_username"] = unicode(self.username.text())
        self.config()["remote_access_password"] = unicode(self.password.text())
        self.config()["check_for_edited_local_media_files"] = \
            self.check_for_edited_local_media_files.isChecked()
        self.component_manager.current("sync_server").deactivate()
        if self.config()["run_sync_server"]:
            self.component_manager.current("sync_server").activate()
            if not self.initially_running and self.is_server_running():
                QtGui.QMessageBox.information(None, _("Mnemosyne"),
                    _("Server now running on ") + localhost_IP() + ".",
                   _("&OK"), "", "", 0, -1)                
        else:
            self.component_manager.current("sync_server").deactivate()
            if self.initially_running and not self.is_server_running():
                QtGui.QMessageBox.information(None, _("Mnemosyne"),
                    _("Server stopped."), _("&OK"), "", "", 0, -1)
    
            
