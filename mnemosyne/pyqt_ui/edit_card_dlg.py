#
# edit_card_dlg.py <Peter.Bienstman@gmail.com>
#

import re

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.pyqt_ui.add_cards_dlg import AddEditCards
from mnemosyne.pyqt_ui.ui_edit_card_dlg import Ui_EditCardDlg
from mnemosyne.pyqt_ui.preview_cards_dlg import PreviewCardsDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import EditCardDialog


class EditCardDlg(QtWidgets.QDialog, AddEditCards,
                  EditCardDialog, Ui_EditCardDlg):

    page_up_down_signal = QtCore.pyqtSignal(int)
    UP = 0
    DOWN = 1

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == QtCore.Qt.Key.Key_PageUp:
                self.page_up_down_signal.emit(self.UP)
                return True
            elif event.key() == QtCore.Qt.Key.Key_PageDown:
                self.page_up_down_signal.emit(self.DOWN)
                return True
            else:
                return False
        return False

    def __init__(self, card, allow_cancel=True,
                 started_from_card_browser=False, parent=None, **kwds):
        super().__init__(**kwds)
        # Note: even though this is in essence an EditFactDlg, we don't use
        # 'fact' as argument, as 'fact' does not know anything about card
        # types.
        if parent is None:
            parent = self.main_widget()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.started_from_card_browser = started_from_card_browser
        self.before_apply_hook = None
        self.after_apply_hook = None
        self.allow_cancel = allow_cancel
        if not allow_cancel:
            self.exit_button.setVisible(False)
        self.card = card
        self.initialise_card_types_combobox(_(self.card.card_type.name))
        self.update_tags_combobox(self.card.tag_string())
        state = self.config()["edit_card_dlg_state"]
        if state:
            self.restoreGeometry(state)
        self.review_widget().stop_media()
        # Make sure we can capture PageUp/PageDown keys before any of the
        # children (e.g. comboboxes) do so.
        if self.started_from_card_browser:
            for child in self.children():
                child.installEventFilter(self)

    def update_card_widget(self, keep_data_from_previous_widget=True):
        AddEditCards.update_card_widget(self, keep_data_from_previous_widget)
        # Install event filters if we need to capture PageUp/PageDown.
        if self.started_from_card_browser:
            for child in self.card_type_widget.children():
                # Make sure we don't install the filter twice.
                child.removeEventFilter(self)
                child.installEventFilter(self)

    def set_new_card(self, card):
        # Called from card browser.
        self.card = card
        self.card_types_widget.currentTextChanged[str].\
            disconnect(self.card_type_changed)
        for i in range(self.card_types_widget.count()):
            if self.card_types_widget.itemText(i) \
                == _(card.card_type.name):
                self.card_types_widget.setCurrentIndex(i)
                break
        self.card_types_widget.currentTextChanged[str].\
            connect(self.card_type_changed)
        self.update_card_widget(keep_data_from_previous_widget=False)
        self.update_tags_combobox(self.card.tag_string())

    def _store_state(self):
        self.config()["edit_card_dlg_state"] = self.saveGeometry()

    def closeEvent(self, event):
        # Generated when clicking the window's close button.
        self._store_state()
        if self.allow_cancel:
            event.ignore()
            self.reject()
        else:
            self.main_widget().show_information(\
                _("You are not allowed to cancel the merging."))
            event.ignore()

    def keyPressEvent(self, event):
        # Note: for the following to work reliably, there should be no
        # shortcuts defined in the ui file.
        if event.key() == QtCore.Qt.Key.Key_Escape or (event.modifiers() in \
            [QtCore.Qt.KeyboardModifier.ControlModifier, QtCore.Qt.KeyboardModifier.AltModifier] and \
            event.key() == QtCore.Qt.Key.Key_E):
            if self.allow_cancel:
                self.reject()
            else:
                self.main_widget().show_information(\
                    _("You are not allowed to cancel the merging."))
                event.ignore()
        elif self.OK_button.isEnabled() and event.modifiers() in \
            [QtCore.Qt.KeyboardModifier.ControlModifier, QtCore.Qt.KeyboardModifier.AltModifier]:
            if event.key() in [QtCore.Qt.Key.Key_Enter, QtCore.Qt.Key.Key_Return,
                QtCore.Qt.Key.Key_O]:
                self.accept()
            elif event.key() == QtCore.Qt.Key.Key_P:
                self.preview()
        else:
            QtWidgets.QDialog.keyPressEvent(self, event)

    def set_valid(self, valid):
        self.OK_button.setEnabled(valid)
        self.preview_button.setEnabled(valid)

    def number_of_anki_clozes_changed(self):
        if not self.card.card_type.id.startswith("7"):
            return False
        re_cloze = "\{\{c[0-9]+::.*?\}\}"
        for fact_key in self.card.card_type.fact_keys():
            if fact_key in self.card_type_widget.fact_data():
                new_content = self.card_type_widget.fact_data()[fact_key]
                if fact_key in self.card.fact.data:
                    previous_content = self.card.fact.data[fact_key]
                else:
                    previous_content = ""
                previous_clozes = re.findall(re_cloze, previous_content)
                new_clozes = re.findall(re_cloze, new_content)
                if len(previous_clozes) != len(new_clozes):
                    return True
        return False

    def is_changed(self):
        if self.previous_card_type_name != \
           self.card_types_widget.currentText():
            return True
        if self.previous_tags != self.tags.currentText():
            return True
        changed = False
        for fact_key in self.card.card_type.fact_keys():
            if fact_key in self.card_type_widget.fact_data():
                new_content = self.card_type_widget.fact_data()[fact_key]
                if fact_key in self.card.fact.data:
                    previous_content = self.card.fact.data[fact_key]
                else:
                    previous_content = ""
                if new_content != previous_content:
                    return True
        return False

    def apply_changes(self):
        if not self.is_changed():
            return 0  # OK.
        new_fact_data = self.card_type_widget.fact_data()
        new_tag_names = [tag.strip() for tag in \
            self.tags.currentText().split(',')]
        new_card_type_name = self.card_types_widget.currentText()
        new_card_type = self.card_type_by_name[new_card_type_name]
        if new_fact_data == self.card.fact.data and \
            ", ".join(new_tag_names) == self.card.tag_string() and \
            new_card_type == self.card.card_type and self.allow_cancel == True:
                # No need to update the dialog, except when we're merging
                # a card when 'allow_cancel' is False.
                QtWidgets.QDialog.reject(self)
                return -1
        # If this is called from the card browser, call this hook to unload
        # the Qt database.
        if self.before_apply_hook:
            self.before_apply_hook()
        status = self.controller().edit_card_and_sisters(self.card,
            new_fact_data, new_card_type, new_tag_names, self.correspondence)
        if self.after_apply_hook:
            self.after_apply_hook()
        return status  # 0 for OK.

    def preview(self):
        if self.number_of_anki_clozes_changed():
            self.main_widget().show_error(_(\
    "Changing the number of clozes in Anki cards is currently not supported."))
            return
        new_fact_data = self.card_type_widget.fact_data()
        new_card_type_name = self.card_types_widget.currentText()
        new_card_type = self.card_type_by_name[new_card_type_name]
        # For previewing existing cards we try to pull them from the database,
        # rather than creating dummy cards from scratch, as we do in
        # 'Add cards". That way, we are sure we create cards with all the
        # required extra_data.
        # When we change the card type, we can't do that, however.
        if self.card.card_type == new_card_type:
            cards = self.database().cards_from_fact(self.card.fact)
            for card in cards:
                card.fact.update(new_fact_data)
        else:
            fact = Fact(new_fact_data)
            cards = new_card_type.create_sister_cards(fact)
        tag_text = self.tags.currentText()
        dlg = PreviewCardsDlg(cards, tag_text,
            component_manager=self.component_manager, parent=self)
        dlg.exec()

    def accept(self):
        if self.number_of_anki_clozes_changed():
            self.main_widget().show_error(_(\
    "Changing the number of clozes in Anki cards is currently not supported."))
            return
        self._store_state()
        status = self.apply_changes()
        if status == 0:
            self.config()["edit_widget_size"] = (self.width(), self.height())
            QtWidgets.QDialog.accept(self)

    def reject(self):  # Override 'add cards' behaviour.
        self._store_state()
        if self.is_changed() == True:
            status = self.main_widget().show_question(\
                _("Abandon changes to current card?"), _("&Yes"), _("&No"), "")
            if status == 0:
                QtWidgets.QDialog.reject(self)
                return
        else:
           QtWidgets.QDialog.reject(self)
