#
# remove_tags_dlg.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtGui, QtCore, QtWidgets

from mnemosyne.pyqt_ui.ui_remove_tags_dlg import Ui_RemoveTagsDlg


class RemoveTagsDlg(QtWidgets.QDialog, Ui_RemoveTagsDlg):

    def __init__(self, tags, return_values, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.return_values = return_values
        for tag in tags:
            if tag.name != "__UNTAGGED__":
                list_item = QtWidgets.QListWidgetItem(tag.name)
                list_item.setFlags(\
                    list_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                list_item.setCheckState(QtCore.Qt.CheckState.Unchecked)
                self.tag_list.addItem(list_item)

    def accept(self):
        self.return_values["tag_names"] = []
        for index in range(self.tag_list.count()):
            list_item = self.tag_list.item(index)
            if list_item.checkState() == QtCore.Qt.CheckState.Checked:
                self.return_values["tag_names"].append(list_item.text())
        return QtWidgets.QDialog.accept(self)
