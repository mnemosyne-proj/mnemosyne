#
# card_type_language_list_wdgt.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
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
            editor.addItem("")
            for language in self.languages():
                editor.addItem(language.name)
            editor.currentTextChanged.connect(\
                lambda: self.update_foreign_keys(index, editor))
        if column == 2:
            self.foreign_key_combobox_for_row[row] = editor
            self.update_foreign_keys(index, editor)
        return editor

    def update_foreign_keys(self, index, editor):
        row, column = index.row(), index.column()
        language_name = self.language_combobox_for_row[row].currentText()
        # While we are still building the widget, return.
        if row not in self.foreign_key_combobox_for_row:
            return
        combobox = self.foreign_key_combobox_for_row[row]
        combobox.clear()
        if language_name == "":
            combobox.addItem("")
        else:
            card_type = index.model().card_types[row]
            # If card type is Sentence or Vocabulary, there is only one option.
            if card_type.id.startswith("3") or card_type.id.startswith("6"):
                combobox.addItem(card_type.fact_key_names()[0])
            else:
                combobox.addItems(card_type.fact_key_names())
                key = self.config().card_type_property(\
                    "foreign_fact_key", card_type)
                if key:
                    key_name = card_type.name_for_fact_key(key)
            # If this is the first time we set a language, make sure to also
            # save the foreign fact key.
            key = self.config().card_type_property(\
                "foreign_fact_key", card_type, default="")
            if not key:
                foreign_key_index = index.model().index(row, column+1)
                index.model().setData(foreign_key_index, combobox.currentText())
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)

    def paint(self, painter, option, index):
        value = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
        style = QtWidgets.QApplication.style()
        opt = QtWidgets.QStyleOptionComboBox()
        opt.text = str(value)
        opt.rect = option.rect
        style.drawComplexControl(QtWidgets.QStyle.ComplexControl.CC_ComboBox, opt, painter)
        QtWidgets.QItemDelegate.paint(self, painter, option, index)

    def setEditorData(self, editor, index):
        editor.setCurrentIndex(editor.findText(index.data()))

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class Model(QtCore.QAbstractTableModel, Component):

    def __init__(self, card_types, **kwds):
        super().__init__(**kwds)
        self.card_types = card_types
        self.language_id_with_name = {}
        for language in self.languages():
            self.language_id_with_name[language.name] = language.used_for
        self.language_id_with_name[""] = ""

    def rowCount(self, parent):
        return len(self.card_types)

    def columnCount(self, parent):
        return 3

    def flags(self, index):
        column = index.column()
        if column == 0:
            return QtCore.Qt.ItemFlag.ItemIsEnabled | \
                   QtCore.Qt.ItemFlag.ItemIsSelectable
        else:
            return QtCore.Qt.ItemFlag.ItemIsEditable | \
                   QtCore.Qt.ItemFlag.ItemIsEnabled | \
                   QtCore.Qt.ItemFlag.ItemIsSelectable

    def data(self, index, role):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            row, column = index.row(), index.column()
            card_type = self.card_types[row]
            if column == 0:
                if not card_type.id.startswith("7") and ":" in card_type.id:
                    return "%s (%s)" % (_(card_type.name),
                            _(card_type.__class__.__bases__[0].name))
                else:
                    return card_type.name
            elif column == 1:
                language_id = self.config().card_type_property(\
                    "language_id", card_type, default="")
                return "" if not language_id else \
                       self.language_with_id(language_id).name
            elif column == 2:
                key = self.config().card_type_property(\
                    "foreign_fact_key", card_type, default="")
                return "" if not key else \
                       card_type.name_for_fact_key(key)

    def setData(self, index, value):
        row, column = index.row(), index.column()
        card_type = self.card_types[row]
        if column == 1:
            self.config().set_card_type_property("language_id",
                self.language_id_with_name[value], card_type)
        elif column == 2:
            self.config().set_card_type_property("foreign_fact_key",
                card_type.fact_key_with_name(value), card_type)
        self.dataChanged.emit(index, index)
        return True

    def headerData(self, column, orientation, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if orientation == QtCore.Qt.Orientation.Horizontal and \
           role == QtCore.Qt.ItemDataRole.DisplayRole :
            if column == 0:
                return "Card type"
            elif column == 1:
                return "Language"
            elif column == 2:
                return "Foreign language field"
        if orientation == QtCore.Qt.Orientation.Vertical and role == QtCore.Qt.ItemDataRole.DisplayRole:
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
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding,
                           QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.horizontalHeader().setSectionResizeMode(\
            QtWidgets.QHeaderView.ResizeMode.Stretch)

    def set_card_types(self, card_types):
        self.model = Model(component_manager=self.component_manager,
                           card_types=card_types)
        self.setModel(self.model)
        # Make combo boxes editable with a single-click.
        for row in range(len(card_types)):
            self.openPersistentEditor(self.model.index(row, 1))
            self.openPersistentEditor(self.model.index(row, 2))

    def selected_card_type(self):
        index = self.selectionModel().currentIndex()
        if not index:
            return None
        else:
            return self.model.card_types[index.row()]


