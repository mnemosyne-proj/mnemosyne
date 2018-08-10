#
# card_type_language_list_wdgt.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component


class ComboDelegate(QtWidgets.QItemDelegate, Component):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.language_with_name = {} # TODO: needed?
        self.language_combobox_for_row = {}
        self.foreign_key_combobox_for_row = {}

    def createEditor(self, parent, option, index):
        row, column = index.row(), index.column()
        editor = QtWidgets.QComboBox(parent)
        if column == 1:
            self.language_combobox_for_row[row] = editor
            for language in self.languages():
                editor.addItem(language.name)
                self.language_with_name[language.name] = language
            editor.currentIndexChanged.connect(\
                lambda: self.update_foreign_keys(row))
        if column == 2:
            self.foreign_key_combobox_for_row[row] = editor
            self.update_foreign_keys(row)
        return editor

    def update_foreign_keys(self, row):
        language_name = self.language_combobox_for_row[row].currentText()
        # While we are still building the widget, return.
        if row not in self.foreign_key_combobox_for_row:
            return
        combobox = self.foreign_key_combobox_for_row[row]
        combobox.clear()
        if language_name == "":
            combobox.addItem("")
        else:
            language = self.language_with_name[language_name]
            # TODO: if card type is sentence or vocabulary, only have
            # one option.
            #if self.card_types[row] == "TODO":
            #    pass
            combobox.addItems(self.card_types[row].keys)
            key = self.card_types[row].current_key
            # TODO: key should be fixed, but description
            # should be translatable
            combobox.setCurrentIndex(combobox.findText(key))

    def paint(self, painter, option, index):
        value = index.data(QtCore.Qt.DisplayRole)
        style = QtWidgets.QApplication.style()
        opt = QtWidgets.QStyleOptionComboBox()
        opt.text = str(value)
        opt.rect = option.rect
        style.drawComplexControl(QtWidgets.QStyle.CC_ComboBox, opt, painter)
        QtWidgets.QItemDelegate.paint(self, painter, option, index)

    def setEditorData(self, editor, index):
        row, column = index.row(), index.column()
        if column == 1:
            language = self.card_types[row].current_lang
            # TODO: key should be ISO code, but description
            # should be translatable
            editor.setCurrentIndex(editor.findText(language))
        if column == 2:
            key = self.card_types[row].current_key
            # TODO: key should be fixed, but description
            # should be translatable
            editor.setCurrentIndex(editor.findText(key))

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, QtCore.Qt.DisplayRole, value)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class Model(QtCore.QAbstractTableModel, Component):

    def __init__(self, card_types, **kwds):
        super().__init__(**kwds)
        self.card_types = card_types

    def rowCount(self, parent):
        return len(self.card_types)

    def columnCount(self, parent):
        return 3

    def flags(self, index):
        column = index.column()
        if column == 0:
            return QtCore.Qt.ItemIsEnabled | \
                   QtCore.Qt.ItemIsSelectable
        else:
            return QtCore.Qt.ItemIsEditable | \
                   QtCore.Qt.ItemIsEnabled | \
                   QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            row, column = index.row(), index.column()
            card_type = self.card_types[row]
            if column == 0:
                if not card_type.id.startswith("7"):
                    return "%s (%s)" % (_(card_type.name),
                        _(card_type.__class__.__bases__[0].name))
                else:
                    return card_type.name
            elif column == 1:
                if card_type.id in self.config()["language_for_card_type_id"]:
                    language_id = self.config()["language_for_card_type_id"]
                    return self.language_with_id[language_id].name
                else:
                    return ""
            elif column == 2:
                if card_type.id in self.config()\
                   ["foreign_fact_key_for_card_type_id"]:
                    foreign_fact_key = self.config()\
                   ["foreign_fact_key_for_card_type_id"]
                    return card_type.fact
                return card_type.current_key

    def setData(self, index, value, role):
        # TODO
        if role == QtCore.Qt.EditRole:
            #self.table[index.row()][index.column()] = value
            pass
            #self.dataChanged.emit()
        return True

    def headerData(self, column, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and \
           role == QtCore.Qt.DisplayRole :
            if column == 0:
                return "Card type"
            elif column == 1:
                return "Language"
            elif column == 2:
                return "Foreign language field"
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return None
        return QtCore.QAbstractTableModel.headerData(\
            self, column, orientation, role)


class CardTypeLanguageListWdgt(QtWidgets.QTableView, Component):

    def __init__(self, card_types, **kwds):
        super().__init__(**kwds)
        self.set_card_types(card_types)
        delegate = ComboDelegate(component_manager=kwds["component_manager"],
                                 parent=self)
        self.setItemDelegateForColumn(1, delegate)
        self.setItemDelegateForColumn(2, delegate)
        # Make combo boxes editable with a single-click.
        for row in range(len(card_types)):
            self.openPersistentEditor(self.model.index(row, 1))
            self.openPersistentEditor(self.model.index(row, 2))

    def set_card_types(self, card_types):
        self.model = Model(component_manager=self.component_manager,
                           card_types=card_types)
        self.setModel(self.model)

