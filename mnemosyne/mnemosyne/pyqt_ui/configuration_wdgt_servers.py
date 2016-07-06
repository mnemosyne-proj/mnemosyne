#
# configuration_wdgt_servers.py <Peter.Bienstman@UGent.be>
#

import socket
import http.client
from PyQt5 import QtGui, QtWidgets

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import localhost_IP
from mnemosyne.libmnemosyne.ui_components.configuration_widget import \
     ConfigurationWidget
from mnemosyne.pyqt_ui.ui_configuration_wdgt_servers import \
     Ui_ConfigurationWdgtServers


class ConfigurationWdgtServers(QtWidgets.QWidget, ConfigurationWidget,
    Ui_ConfigurationWdgtServers):

    name = _("Servers")

    def __init__(self, **kwds):
        super().__init__(**kwds)    
        self.setupUi(self)
        sync_port = self.config()["sync_server_port"]
        web_port = self.config()["web_server_port"]
        self.sync_server_initially_running = self.is_server_running(sync_port)
        self.web_server_initially_running = self.is_server_running(web_port)
        self.run_sync_server.setChecked(self.config()["run_sync_server"])
        self.sync_port.setValue(sync_port)
        self.username.setText(self.config()["remote_access_username"])
        self.password.setText(self.config()["remote_access_password"])
        self.check_for_edited_local_media_files.setChecked(\
            self.config()["check_for_edited_local_media_files"])
        self.run_web_server.setChecked(self.config()["run_web_server"])
        self.web_port.setValue(web_port)
        if self.is_server_running(sync_port):
            self.sync_server_status.setText(_("Sync server running on ") + \
                localhost_IP() + " .")
        else:
            self.sync_server_status.setText(_("Sync server NOT running."))
        if self.is_server_running(web_port):
            self.web_server_status.setText(_("Web server running on ") + \
               "http://" + localhost_IP() + ":" + str(web_port) + " .")
        else:
            self.web_server_status.setText(_("Web server NOT running."))

    def is_server_running(self, port):
        timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(0.1)
            con = http.client.HTTPConnection(localhost_IP(), port)
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
        self.config()["remote_access_username"] = str(self.username.text())
        self.config()["remote_access_password"] = str(self.password.text())
        self.config()["check_for_edited_local_media_files"] = \
            self.check_for_edited_local_media_files.isChecked()
        self.config()["run_web_server"] = self.run_web_server.isChecked()
        self.config()["web_server_port"] = self.web_port.value()
        self.component_manager.current("sync_server").deactivate()
        if self.config()["run_sync_server"]:
            self.component_manager.current("sync_server").activate()
            if not self.sync_server_initially_running \
                and self.is_server_running(self.config()["sync_server_port"]):
                self.main_widget().show_information(\
                    _("Sync server now running on ") + localhost_IP() + ".")
        else:
            self.component_manager.current("sync_server").deactivate()
            if self.sync_server_initially_running and \
                not self.is_server_running(self.config()["sync_server_port"]):
                self.main_widget().show_information(\
                    _("Sync server stopped."))
        if self.config()["run_web_server"]:
            self.component_manager.current("web_server").activate()
            if not self.web_server_initially_running \
                and self.is_server_running(self.config()["web_server_port"]):
                self.main_widget().show_information(\
                    _("Web server now running on") + " http://" + \
                    localhost_IP() + ":" + \
                    str(self.config()["web_server_port"]) + " .")
        else:
            self.component_manager.current("web_server").deactivate()
            if self.web_server_initially_running and \
                not self.is_server_running(self.config()["web_server_port"]):
                self.main_widget().show_information(\
                    _("Web server stopped."))
