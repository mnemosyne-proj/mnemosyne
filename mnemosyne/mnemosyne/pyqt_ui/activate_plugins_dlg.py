#
# activate_plugins_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.ui_activate_plugins_dlg import Ui_ActivatePluginsDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ActivatePluginsDialog

class PluginListModel(QtCore.QAbstractTableModel, Component):

    def __init__(self, component_manager):
        QtCore.QAbstractTableModel.__init__(self)
        Component.__init__(self, component_manager)

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.plugins())
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        return 2
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or \
               not (0 <= index.row() < len(self.plugins())):
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return QtCore.QVariant(self.plugins()[index.row()].name)
            elif index.column() == 1:
                return QtCore.QVariant(self.plugins()[index.row()].description)
        if role == QtCore.Qt.CheckStateRole:
            if index.column() == 0:
                if self.plugins()[index.row()].__class__.__name__ in \
                       self.config()["active_plugins"]:
                    return QtCore.QVariant(QtCore.Qt.Checked)
                else:
                    return QtCore.QVariant(QtCore.Qt.Unchecked)                   
        return  QtCore.QVariant()

    def flags(self, index):
        if index.column() == 0:
            return QtCore.Qt.ItemIsEnabled| QtCore.Qt.ItemIsUserCheckable
        else:
            return QtCore.Qt.ItemIsEnabled

    def setData(self, index, value, role):
        if index.isValid() and index.column() == 0:
            if role == QtCore.Qt.CheckStateRole:
                plugin = self.plugins()[index.row()]
                if value == QtCore.QVariant(QtCore.Qt.Checked):
                    plugin.activate()
                    if plugin.activation_message:
                        self.main_widget().information_box(\
                            plugin.activation_message)
                else:
                    if plugin.deactivate() == False:
                        return False
                    self.emit(QtCore.SIGNAL(\
                        "dataChanged(QModelIndex,QModelIndex)"),index, index)
            return True
        return False
                    
    def headerData(self, index, orientation, role):
        if role == QtCore.Qt.DisplayRole and \
           orientation == QtCore.Qt.Horizontal:
            if index == 0:
                return QtCore.QVariant(_("Name"))
            elif index == 1:
                return QtCore.QVariant(_("Description"))
        return QtCore.QVariant()

        
class ActivatePluginsDlg(QtGui.QDialog, Ui_ActivatePluginsDlg, ActivatePluginsDialog):

    def __init__(self, parent, component_manager):
        Component.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.model = PluginListModel(self.component_manager)
        self.plugins.setModel(self.model)
        self.plugins.resizeColumnToContents(0)    
        self.plugins.resizeColumnToContents(1)
        self.plugins.setTextElideMode(QtCore.Qt.ElideNone)
        self.plugins.setRootIsDecorated(False)
        self.plugins.setItemsExpandable(False)
        width, height = self.config()["plugins_widget_size"]
        if width:
            self.resize(width, height)
            
    def closeEvent(self, event):
        self.config()["plugins_widget_size"] = (self.width(), self.height())
        
    def accept(self):
        self.config()["plugins_widget_size"] = (self.width(), self.height())
        return QtGui.QDialog.accept(self)       
