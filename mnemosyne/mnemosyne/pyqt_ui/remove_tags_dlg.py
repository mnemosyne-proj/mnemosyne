#
# remove_tags_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtGui, QtCore

from mnemosyne.pyqt_ui.ui_remove_tags_dlg import Ui_RemoveTagsDlg


class RemoveTagsDlg(QtGui.QDialog, Ui_RemoveTagsDlg):

    def __init__(self, parent, tags, return_values):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        self.return_values = return_values
        for tag in tags:
            if tag.name != "__UNTAGGED__":
                list_item = QtGui.QListWidgetItem(tag.name)
                list_item.setFlags(list_item.flags() | QtCore.Qt.ItemIsUserCheckable)
                list_item.setCheckState(QtCore.Qt.Unchecked)
                self.tag_list.addItem(list_item)

    def accept(self):
        self.return_values["tag_names"] = []
        for index in range(self.tag_list.count()):
            list_item = self.tag_list.item(index)
            if list_item.checkState() == QtCore.Qt.Checked:
                self.return_values["tag_names"].append(\
                    unicode(list_item.text()))
        return QtGui.QDialog.accept(self)
