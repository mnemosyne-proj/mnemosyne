#
# activate_plugins_dlg.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from copy import deepcopy

from ui_activate_plugins_dlg import Ui_ActivatePluginsDlg

from mnemosyne.libmnemosyne.component_manager import config, plugins


class PluginListModel(QAbstractTableModel):

    def rowCount(self, parent=QModelIndex()):
        return len(plugins())
    
    def columnCount(self, parent=QModelIndex()):
        return 2
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(plugins())):
            return QVariant()
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return QVariant(plugins()[index.row()].name)
            elif index.column() == 1:
                return QVariant(plugins()[index.row()].description)
        if role == Qt.CheckStateRole:
            if index.column() == 0:
                if plugins()[index.row()].active == True:
                    return QVariant(Qt.Checked)
                else:
                    return QVariant(Qt.Unchecked)                   
        return QVariant()

    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemIsEnabled|Qt.ItemIsUserCheckable
        else:
            return Qt.ItemIsEnabled

    def setData(self, index, value, role):
        if index.isValid() and index.column() == 0:
            if role == Qt.CheckStateRole:
                plugin = plugins()[index.row()]
                if value == QVariant(Qt.Checked):
                    plugin.activate()
                    plugin.active = True
                else:
                    plugin.deactivate()                    
                    plugin.active = False
            self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                      index, index)
            return True
        return False
                    
    def headerData(self, index, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if index == 0:
                return QVariant(_("Name"))
            elif index == 1:
                return QVariant(_("Description"))
        return QVariant()

        
class ActivatePluginsDlg(QDialog, Ui_ActivatePluginsDlg):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.model = PluginListModel()
        self.plugins.setModel(self.model)
        self.plugins.resizeColumnToContents(0)    
        self.plugins.resizeColumnToContents(1)
        self.plugins.setTextElideMode(Qt.ElideNone)
        self.plugins.setRootIsDecorated(False)
        self.plugins.setItemsExpandable(False)
