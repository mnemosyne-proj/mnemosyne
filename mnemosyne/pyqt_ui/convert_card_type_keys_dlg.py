#
# convert_card_type_keys_dlg.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.pyqt_ui.ui_convert_card_type_keys_dlg import \
     Ui_ConvertCardTypeKeysDlg


class ConvertCardTypeKeysDlg(QtWidgets.QDialog, Ui_ConvertCardTypeKeysDlg):

    def __init__(self, old_card_type, new_card_type, correspondence,
                 check_required_fact_keys=True, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.old_card_type = old_card_type
        self.new_card_type = new_card_type
        self.correspondence = correspondence
        self.check_required_fact_keys = check_required_fact_keys
        self.comboboxes = {}
        index = 1
        for old_fact_key, old_fact_key_name in \
            old_card_type.fact_keys_and_names:
            label = QtWidgets.QLabel(self)
            label.setText(_(old_fact_key_name) + ":")
            font = QtGui.QFont()
            font.setWeight(50)
            font.setBold(False)
            label.setFont(font)
            self.gridLayout.addWidget(label, index, 0, 1, 1)
            combobox = QtWidgets.QComboBox(self)
            for new_fact_key, new_key_name in \
                new_card_type.fact_keys_and_names:
                combobox.addItem(_(new_key_name))
            combobox.addItem(_("<none>"))
            combobox.setCurrentIndex(combobox.count()-1)
            self.gridLayout.addWidget(combobox, index, 1, 1, 1)
            self.comboboxes[old_fact_key] = combobox
            index += 1
            combobox.currentTextChanged.connect(self.combobox_updated)

    def combobox_updated(self):
        self.ok_button.setEnabled(False)
        self.correspondence.clear()
        for old_fact_key, old_fact_key_name in \
            self.old_card_type.fact_keys_and_names:
            new_fact_key_name = \
                self.comboboxes[old_fact_key].currentText()
            if new_fact_key_name != _("<none>"):
                self.ok_button.setEnabled(True)
                new_fact_key = \
                     self.new_card_type.fact_key_with_name(new_fact_key_name)
                if new_fact_key in self.correspondence.values():
                    QtWidgets.QMessageBox.critical(self, _("Mnemosyne"),
                        _("No duplicate in new fact keys allowed."))
                    self.ok_button.setEnabled(False)
                    return
                self.correspondence[old_fact_key] = new_fact_key
        if self.check_required_fact_keys:
            for fact_key in self.new_card_type.required_fact_keys:
                if fact_key not in self.correspondence.values():
                    self.ok_button.setEnabled(False)
                    if len(self.correspondence) == \
                       len(self.old_card_type.fact_keys()):
                        QtWidgets.QMessageBox.critical(self, _("Mnemosyne"),
                            _("A required field is missing."))
                    return

    def accept(self):
        self.correspondence.clear()
        for old_fact_key, old_fact_key_name in \
            self.old_card_type.fact_keys_and_names:
            new_fact_key_name = \
                self.comboboxes[old_fact_key].currentText()
            if new_fact_key_name != _("<none>"):
                new_fact_key = \
                     self.new_card_type.fact_key_with_name(new_fact_key_name)
                self.correspondence[old_fact_key] = new_fact_key
        QtWidgets.QDialog.accept(self)
