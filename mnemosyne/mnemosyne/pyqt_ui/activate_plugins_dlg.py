#
# activate_plugins_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui


from mnemosyne.pyqt_ui.ui_activate_plugins_dlg import Ui_ActivatePluginsDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ActivatePluginsDialog


class ActivatePluginsDlg(QtGui.QDialog, Ui_ActivatePluginsDlg,
    ActivatePluginsDialog):

    def __init__(self, component_manager):
        ActivatePluginsDialog.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        self.build_plugin_list()
        state = self.config()["plugins_dlg_state"]
        if state:
            self.restoreGeometry(state)

    def build_plugin_list(self):
        self.plugin_list.clear()
        self.previously_active = {}
        self.plugin_with_name = {}
        for plugin in self.plugins():
            list_item = QtGui.QListWidgetItem(plugin.name)
            list_item.setFlags(list_item.flags() | QtCore.Qt.ItemIsUserCheckable)
            self.plugin_with_name[plugin.name] = plugin
            active = \
                plugin.__class__.__name__ in self.config()["active_plugins"]
            self.previously_active[plugin.name] = active
            if active:
                list_item.setCheckState(QtCore.Qt.Checked)
            else:
                list_item.setCheckState(QtCore.Qt.Unchecked)
            self.plugin_list.addItem(list_item)
        self.plugin_list.itemActivated.connect(self.plugin_selected)
        self.plugin_list.setCurrentRow(0)
        self.plugin_description.setText(self.plugins()[0].description)

    def plugin_selected(self, list_item):
        self.plugin_description.setText(\
            self.plugin_with_name[unicode(list_item.text())].description)

    def activate(self):
        self.exec_()

    def _store_state(self):
        self.config()["plugins_dlg_state"] = self.saveGeometry()

    def closeEvent(self, event):
        # Generated when clicking the window's close button.
        self._store_state()

    def accept(self):
        # 'accept' does not generate a close event.
        self._store_state()
        for index in range(self.plugin_list.count()):
            list_item = self.plugin_list.item(index)
            plugin_name = unicode(list_item.text())
            if list_item.checkState() == QtCore.Qt.Checked and \
                self.previously_active[plugin_name] == False:
                self.plugin_with_name[plugin_name].activate()
            elif list_item.checkState() == QtCore.Qt.Unchecked and \
                self.previously_active[plugin_name] == True:
                self.plugin_with_name[plugin_name].deactivate()
        return QtGui.QDialog.accept(self)

    def install_plugin(self):
        self.controller().install_plugin()
        self.build_plugin_list()

    def delete_plugin(self):
        self.controller().delete_plugin()
        self.build_plugin_list()
