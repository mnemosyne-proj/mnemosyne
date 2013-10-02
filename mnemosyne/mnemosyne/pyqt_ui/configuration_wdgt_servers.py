#
# configuration_wdgt_servers.py <Peter.Bienstman@UGent.be>
#

import socket
import httplib
from PyQt4 import QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import localhost_IP
from mnemosyne.libmnemosyne.ui_components.configuration_widget import \
     ConfigurationWidget
from mnemosyne.pyqt_ui.ui_configuration_wdgt_servers import \
     Ui_ConfigurationWdgtServers


class ConfigurationWdgtServers(QtGui.QWidget,
    Ui_ConfigurationWdgtServers, ConfigurationWidget):

    name = _("Servers")

    def __init__(self, component_manager, parent):
        ConfigurationWidget.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.sync_server_initially_running = self.is_sync_server_running()
        self.run_sync_server.setChecked(self.config()["run_sync_server"])
        self.sync_port.setValue(self.config()["sync_server_port"])
        self.username.setText(self.config()["remote_access_username"])
        self.password.setText(self.config()["remote_access_password"])
        self.check_for_edited_local_media_files.setChecked(\
            self.config()["check_for_edited_local_media_files"])
        if self.is_sync_server_running():
            self.sync_server_status.setText(_("Sync server running on ") + \
                localhost_IP() + " .")
        else:
            self.sync_server_status.setText(_("Sync server NOT running."))

    def is_sync_server_running(self):
        timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(0.1)
            con = httplib.HTTPConnection(localhost_IP(),
                self.config()["sync_server_port"])
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
        self.sync_port.setValue(8512)
        self.username.setText("")
        self.password.setText("")
        self.check_for_edited_local_media_files.setChecked(False)
        self.web_port.setValue(8513)

    def apply(self):
        self.config()["run_sync_server"] = self.run_sync_server.isChecked()
        self.config()["sync_server_port"] = self.sync_port.value()
        self.config()["remote_access_username"] = unicode(self.username.text())
        self.config()["remote_access_password"] = unicode(self.password.text())
        self.config()["check_for_edited_local_media_files"] = \
            self.check_for_edited_local_media_files.isChecked()
        self.component_manager.current("sync_server").deactivate()
        if self.config()["run_sync_server"]:
            self.component_manager.current("sync_server").activate()
            if not self.sync_server_initially_running \
                and self.is_sync_server_running():
                self.main_widget().show_information(\
                    _("Sync server now running on ") + localhost_IP() + ".")
        else:
            self.component_manager.current("sync_server").deactivate()
            if self.sync_server_initially_running and \
                not self.is_sync_server_running():
                self.main_widget().show_information(\
                    _("Sync server stopped."))
