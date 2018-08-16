#
# card_type_language_list_wdgt.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component


class ComboDelegate(QtWidgets.QItemDelegate, Component):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.language_combobox_for_row = {}
        self.foreign_key_combobox_for_row = {}

    def createEditor(self, parent, option, index):
        row, column = index.row(), index.column()
        editor = QtWidgets.QComboBox(parent)
        if column == 1:
            self.language_combobox_for_row[row] = editor
            for language in self.languages():
                editor.addItem(language.name)
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
            card_type = self.card_types[row]
            # If card type is Sentence or Vocabulary, there is only one option.
            if card_type.id.startswidth(3) or card_type.id.startswith(6):
                combobox.addItem(card_type.fact_key_names()[0])
            else:
                combobox.addItems(card_type.fact_key_names())
                key = self.config()[\
                    "foreign_fact_key_for_card_type_id"][card_type.id]
                key_name = card_type.name_for_fact_key(key)
                combobox.setCurrentIndex(combobox.findText(key_name))

    def paint(self, painter, option, index):
        value = index.data(QtCore.Qt.DisplayRole)
        style = QtWidgets.QApplication.style()
        opt = QtWidgets.QStyleOptionComboBox()
        opt.text = str(value)
        opt.rect = option.rect
        style.drawComplexControl(QtWidgets.QStyle.CC_ComboBox, opt, painter)
        QtWidgets.QItemDelegate.paint(self, painter, option, index)

    def setEditorData(self, editor, index):
        editor.setCurrentIndex(editor.findText(index.data()))

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, QtCore.Qt.DisplayRole, value)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class Model(QtCore.QAbstractTableModel, Component):

    def __init__(self, card_types, **kwds):
        super().__init__(**kwds)
        self.card_types = card_types
        self.language_id_with_name = {}
        for language in self.languages():
            self.language_id_with_name[language.name] = language.used_for

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
                    return card_type.name_for_fact_key[foreign_fact_key]
                else:
                    return ""

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole:
            row, column = index.row(), index.column()
            card_type = self.card_types[row]
            if column == 1:
                self.config()["language_for_card_type_id"]\
                    [card_type.id] = self.language_with_id_name[value]
            elif column == 2:
                self.config()["foreign_fact_key_for_card_type_id"]\
                    [card_type.id] = card_type.fact_key_with_name[value]
            self.dataChanged.emit()
            return True
        return False

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

    def __init__(self, **kwds):
        super().__init__(**kwds)
        delegate = ComboDelegate(component_manager=kwds["component_manager"],
                                 parent=self)
        self.setItemDelegateForColumn(1, delegate)
        self.setItemDelegateForColumn(2, delegate)

    def set_card_types(self, card_types):
        self.model = Model(component_manager=self.component_manager,
                           card_types=card_types)
        self.setModel(self.model)
        # Make combo boxes editable with a single-click.
        for row in range(len(card_types)):
            self.openPersistentEditor(self.model.index(row, 1))
            self.openPersistentEditor(self.model.index(row, 2))

