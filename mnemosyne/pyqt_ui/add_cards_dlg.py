#
# add_cards_dlg.py <Peter.Bienstman@gmail.com>
#

import copy

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.ui_add_cards_dlg import Ui_AddCardsDlg
from mnemosyne.pyqt_ui.preview_cards_dlg import PreviewCardsDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import AddCardsDialog
from mnemosyne.pyqt_ui.card_type_wdgt_generic import GenericCardTypeWdgt
from mnemosyne.pyqt_ui.convert_card_type_keys_dlg import \
     ConvertCardTypeKeysDlg
from mnemosyne.pyqt_ui.tip_after_starting_n_times import \
     TipAfterStartingNTimes


class AddEditCards(TipAfterStartingNTimes):

    """Code shared between the add and the edit dialogs."""

    started_n_times_counter = "started_add_edit_cards_n_times"
    tip_after_n_times = \
        {3: _("You can add multiple tags to a card by separating tags with a comma in the 'Tag(s)' input field."),
         6: _("You can organise tags in a hierarchy by using :: as separator, e.g. My book::Lesson 1."),
         9: _("You can add images and sounds to your cards. Right-click on an input field when editing a card to bring up a pop-up menu to do so."),
         12: _("If for a certain card type cloned from Vocabulary you don't need a pronunciation field, you can hide it by right-clicking on it and using the pop-up menu."),
         15: _("You can use Tab to move between the fields. For 'Add cards', use Ctrl+Enter for 'Yet to learn', and Ctrl+2, etc. for the grades. For 'Edit card', use Ctrl-Enter to close."),
         18: _("If you use 'Edit cards', changes are made to all the sister cards simultaneously."),
         21: _("If your card type has a language associated to it, you can right click to insert text-to-speech or translations.")}

    def activate(self):
        AddCardsDialog.activate(self)
        self.show_tip_after_starting_n_times()
        status = self.exec()
        return (status == QtWidgets.QDialog.DialogCode.Accepted)

    def initialise_card_types_combobox(self, current_card_type_name):
        # We calculate card_type_by_name here because these names can change
        # if the user chooses another translation.
        self.card_type_by_name = {}
        self.card_type = None
        self.card_type_index = 0
        self.card_type_widget = None
        self.previous_tags = None
        self.previous_card_type_name = current_card_type_name
        db_sorted_card_types = self.database().sorted_card_types()
        for card_type in db_sorted_card_types:
            if card_type.hidden_from_UI == True:
                continue
            # Adding M-sided cards or converting to them is not (yet) supported.
            if _(card_type.name) != current_card_type_name \
               and card_type.id.startswith("7"):
                continue
            if _(card_type.name) == current_card_type_name:
                self.card_type = card_type
                self.card_type_index = self.card_types_widget.count()
            self.card_type_by_name[_(card_type.name)] = card_type
            self.card_types_widget.addItem(_(card_type.name))
        if not self.card_type:
            self.card_type = db_sorted_card_types[0]
            self.card_type_index = 0
        self.card_types_widget.setCurrentIndex(self.card_type_index)
        # Now that the combobox is filled, we can connect the signal.
        self.card_types_widget.currentTextChanged[str].\
            connect(self.card_type_changed)
        self.correspondence = {}  # Used when changing card types.
        self.update_card_widget()

    def update_card_widget(self, keep_data_from_previous_widget=True):
        # Determine data to put into card widget. Since we want to share this
        # code between the 'add' and the 'edit' dialogs, we put the reference
        # to self.card (which only exists in the 'edit' dialog) inside a try
        # statement.
        if self.card_type_widget:  # Get data from previous card widget.
            prefill_fact_data = self.card_type_widget.fact_data()
            self.card_type_widget.close()
            self.card_type_widget = None
        else:
            try:  # Get data from fact passed to the 'edit' dialog.
                prefill_fact_data = self.card.fact.data
            except:  # Start from scratch in the 'add' dialog.
                prefill_fact_data = None
        # Transform keys in dictionary if the card type has changed, but don't
        # edit the fact just yet.
        if prefill_fact_data and self.correspondence:
            old_prefill_fact_data = copy.copy(prefill_fact_data)
            prefill_fact_data = {}
            for fact_key in old_prefill_fact_data:
                if fact_key in self.correspondence:
                    value = old_prefill_fact_data[fact_key]
                    prefill_fact_data[self.correspondence[fact_key]] = value
        # If we just want to force a new card in the dialog, e.g. by pressing
        # PageUp or PageDown in the card browser, don't bother with trying to
        # keep old data.
        if not keep_data_from_previous_widget:
            prefill_fact_data = self.card.fact.data
        # Show new card type widget.
        card_type_name = self.card_types_widget.currentText()
        self.card_type = self.card_type_by_name[card_type_name]
        try:
            self.card_type_widget = self.component_manager.current \
                ("card_type_widget", used_for=self.card_type.__class__) \
                (card_type=self.card_type, parent=self,
                 component_manager=self.component_manager)
        except Exception as e:
            if not self.card_type_widget:
                self.card_type_widget = self.component_manager.current \
                    ("generic_card_type_widget")(card_type=self.card_type,
                    parent=self, component_manager=self.component_manager)
        self.card_type_widget.set_fact_data(prefill_fact_data)
        self.card_type_widget.show()
        self.vbox_layout.insertWidget(1, self.card_type_widget)

    def update_tags_combobox(self, current_tag_name):
        all_current_tag_names = current_tag_name.split(", ")
        existing_current_tag_names = []
        self.tags.clear()
        for tag in self.database().tags():
            if tag.name != "__UNTAGGED__":
                self.tags.addItem(tag.name)
            if tag.name in all_current_tag_names:
                existing_current_tag_names.append(tag.name)
        current_tag_name = ", ".join(existing_current_tag_names)
        # For the 'special' tags, we add them at the top.
        self.tags.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.InsertAtTop)
        if "," in current_tag_name:
            self.tags.addItem(current_tag_name)
        if current_tag_name == "":
            self.tags.addItem(current_tag_name)
        for i in range(self.tags.count()):
            if self.tags.itemText(i) == current_tag_name:
                self.tags.setCurrentIndex(i)
                break
        self.previous_tags = self.tags.currentText()
        self.tags.refresh_completion_model()

    def card_type_changed(self, new_card_type_name):
        new_card_type_name = new_card_type_name
        new_card_type = self.card_type_by_name[new_card_type_name]
        if self.card_type.fact_keys().issubset(new_card_type.fact_keys()) or \
            self.card_type_widget.is_empty():
            self.update_card_widget()
            return
        dlg = ConvertCardTypeKeysDlg(self.card_type, new_card_type,
            self.correspondence, check_required_fact_keys=False, parent=self)
        if dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            # Set correspondence so as not to erase previous data.
            self.correspondence = {}
            for key in self.card_type.fact_keys():
                self.correspondence[key] = key
            self.card_types_widget.setCurrentIndex(self.card_type_index)
            return
        else:
            self.update_card_widget()

    def preview(self):
        fact_data = self.card_type_widget.fact_data()
        fact = Fact(fact_data)
        cards = self.card_type.create_sister_cards(fact)
        tag_text = self.tags.currentText()
        dlg = PreviewCardsDlg(cards, tag_text,
            component_manager=self.component_manager, parent=self)
        dlg.exec()

    def __del__(self):
        # Make sure that Python knows Qt has deleted this widget.
        self.card_type_widget = None


class AddCardsDlg(QtWidgets.QDialog, AddEditCards,
                  AddCardsDialog, Ui_AddCardsDlg):

    def __init__(self, card_type=None, fact_data=None, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        if card_type:
            last_used_card_type = card_type
        else:
            last_used_card_type_id = self.config()["last_used_card_type_id"]
            try:
                last_used_card_type = self.card_type_with_id(\
                    last_used_card_type_id)
            except:
                # First time use, or card type was deleted.
                last_used_card_type = self.card_type_with_id("1")
        self.initialise_card_types_combobox(last_used_card_type.name)
        if last_used_card_type.id not in \
            self.config()["last_used_tags_for_card_type_id"]:
            self.config()["last_used_tags_for_card_type_id"]\
                [last_used_card_type.id] = ""
        if not self.config()["is_last_used_tags_per_card_type"]:
            self.update_tags_combobox(self.config()["last_used_tags"])
        else:
            self.update_tags_combobox(self.config()\
                ["last_used_tags_for_card_type_id"][last_used_card_type.id])
        if fact_data:
            self.card_type_widget.set_fact_data(fact_data)
        self.grades = QtWidgets.QButtonGroup()
        # Negative indexes have special meanings in Qt, so we can't use -1 for
        # 'yet to learn'.
        self.grades.addButton(self.yet_to_learn_button, 0)
        self.grades.addButton(self.grade_2_button, 2)
        self.grades.addButton(self.grade_3_button, 3)
        self.grades.addButton(self.grade_4_button, 4)
        self.grades.addButton(self.grade_5_button, 5)
        self.grades.idClicked[int].connect(self.create_new_cards)
        if not (card_type and fact_data):
            self.set_valid(False)
        state = self.config()["add_cards_dlg_state"]
        if state:
            self.restoreGeometry(state)

    def card_type_changed(self, new_card_type_name):
        # We only store the last used tags when creating a new card,
        # not when editing.
        new_card_type = self.card_type_by_name[new_card_type_name]
        self.config()["last_used_card_type_id"] = new_card_type.id
        if new_card_type.id not in \
            self.config()["last_used_tags_for_card_type_id"]:
            self.config()["last_used_tags_for_card_type_id"]\
                [new_card_type.id] = ""
        if not self.config()["is_last_used_tags_per_card_type"]:
            if not self.tags.currentText():
                self.update_tags_combobox(self.config()["last_used_tags"])
        else:
            if not self.tags.currentText() \
                or self.card_type_widget.is_empty():
                self.update_tags_combobox(self.config()\
                    ["last_used_tags_for_card_type_id"][new_card_type.id])
        AddEditCards.card_type_changed(self, new_card_type_name)

    def keyPressEvent(self, event):
        if self.yet_to_learn_button.isEnabled() and event.modifiers() in \
            [QtCore.Qt.KeyboardModifier.ControlModifier, QtCore.Qt.KeyboardModifier.AltModifier]:
            if event.key() in [QtCore.Qt.Key.Key_Enter, QtCore.Qt.Key.Key_Return,
                QtCore.Qt.Key.Key_Y, QtCore.Qt.Key.Key_0, QtCore.Qt.Key.Key_1]:
                # Qt bug: works for Enter, Return, but not 0 or 1.
                self.create_new_cards(-1)
            elif event.key() == QtCore.Qt.Key.Key_2:
                self.create_new_cards(2)
            elif event.key() == QtCore.Qt.Key.Key_3:
                self.create_new_cards(3)
            elif event.key() == QtCore.Qt.Key.Key_4:
                self.create_new_cards(4)
            elif event.key() == QtCore.Qt.Key.Key_5:
                self.create_new_cards(5)
            elif event.key() == QtCore.Qt.Key.Key_P:
                self.preview()
            elif event.key() == QtCore.Qt.Key.Key_E:
                self.reject()
        else:
            QtWidgets.QDialog.keyPressEvent(self, event)

    def set_valid(self, valid):
        self.grade_buttons.setEnabled(valid)
        self.preview_button.setEnabled(valid)

    def create_new_cards(self, grade):
        if grade == 0:
            grade = -1
        fact_data = self.card_type_widget.fact_data()
        tag_names = [c.strip() for c in \
                     self.tags.currentText().split(',')]
        card_type_name = self.card_types_widget.currentText()
        card_type = self.card_type_by_name[card_type_name]
        c = self.controller()
        c.create_new_cards(fact_data, card_type, grade, tag_names, save=True)
        tag_text = ", ".join(tag_names)
        self.update_tags_combobox(tag_text)
        self.config()["last_used_tags"] = tag_text
        self.config()["last_used_tags_for_card_type_id"][card_type.id] \
            = tag_text
        self.card_type_widget.clear()

    def reject(self):
        # Generated when pressing escape or clicking the exit button.
        self._store_state()
        if not self.card_type_widget.is_empty() and \
            self.card_type_widget.is_changed():
            status = self.main_widget().show_question(\
                _("Abandon current card?"), _("&Yes"), _("&No"), "")
            if status == 0:
                QtWidgets.QDialog.reject(self)
                return
        else:
            QtWidgets.QDialog.reject(self)

    def _store_state(self):
        self.config()["add_cards_dlg_state"] = self.saveGeometry()

    def closeEvent(self, event):
        # Generated when clicking the window's close button.
        self._store_state()
        event.ignore()
        self.reject()

    def accept(self):
        # 'accept' does not generate a close event.
        self._store_state()
        return QtWidgets.QDialog.accept(self)
