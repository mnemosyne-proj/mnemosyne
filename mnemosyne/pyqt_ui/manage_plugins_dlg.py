#
# manage_plugins_dlg.py <Peter.Bienstman@gmail.com>
#

import os
from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.pyqt_ui.ui_manage_plugins_dlg import Ui_ManagePluginsDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ManagePluginsDialog


class ManagePluginsDlg(QtWidgets.QDialog, ManagePluginsDialog,
                       Ui_ManagePluginsDlg):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.last_selected_row = 0
        self.build_plugin_list()
        state = self.config()["plugins_dlg_state"]
        if state:
            self.restoreGeometry(state)

    def build_plugin_list(self):
        plugin_dir = os.path.join(self.config().data_dir, "plugins")
        self.can_be_deleted = [filename.rsplit(".", 1)[0] for \
            filename in os.listdir(plugin_dir) \
            if filename.endswith(".manifest")]
        self.plugin_list.clear()
        self.previously_active = {}
        self.plugin_with_name = {}
        for plugin in self.plugins():
            list_item = QtWidgets.QListWidgetItem(_(plugin.name))
            list_item.setFlags(list_item.flags() \
                | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            self.plugin_with_name[_(plugin.name)] = plugin
            active = \
                plugin.__class__.__name__ in self.config()["active_plugins"]
            self.previously_active[_(plugin.name)] = active
            if active:
                list_item.setCheckState(QtCore.Qt.CheckState.Checked)
            else:
                list_item.setCheckState(QtCore.Qt.CheckState.Unchecked)
            self.plugin_list.addItem(list_item)
        self.plugin_list.setCurrentRow(self.last_selected_row)
        self.plugin_description.setText(_(self.plugins()[0].description))
        self.delete_button.setEnabled(\
            self.plugins()[0].__class__.__name__ in self.can_be_deleted)

    def plugin_selected(self, list_item, dummy=None):
        if list_item is None: # Sometimes Qt fires spurious events.
            return
        # If we get there through activating of the item, make sure we move
        # the selection to the activated item.
        self.plugin_list.setCurrentItem(list_item)
        plugin = self.plugin_with_name[list_item.text()]
        self.plugin_description.setText(_(plugin.description))
        self.delete_button.setEnabled(\
            plugin.__class__.__name__ in self.can_be_deleted)

    def activate(self):
        self.exec()

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
            plugin_name = list_item.text()
            if list_item.checkState() == QtCore.Qt.CheckState.Checked and \
                self.previously_active[plugin_name] == False:
                self.plugin_with_name[plugin_name].activate()
            elif list_item.checkState() == QtCore.Qt.CheckState.Unchecked and \
                self.previously_active[plugin_name] == True:
                self.plugin_with_name[plugin_name].deactivate()
        return QtWidgets.QDialog.accept(self)

    def install_plugin(self):
        self.last_selected_row = self.plugin_list.currentRow()
        self.controller().install_plugin()
        self.build_plugin_list()

    def delete_plugin(self):
        plugin_name = self.plugin_list.selectedItems()[0].text()
        question = _("Are you sure you want to delete the plugin") + " \"" + \
            plugin_name + "\" " + _("and not just deactivate it?")
        answer = self.main_widget().show_question(question,
            _("Delete"), _("Cancel"), "")
        if answer == 1:  # Cancel
            return
        self.controller().delete_plugin(self.plugin_with_name[plugin_name])
        self.build_plugin_list()
