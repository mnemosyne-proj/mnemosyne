# -*- coding: utf-8 -*-
#
# edit_M_sided_card_template_wdgt.py <Peter.Bienstman@gmail.com>
#

import copy

from PyQt6 import QtCore, QtWidgets

from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.pyqt_ui.ui_edit_M_sided_card_template_wdgt import \
     Ui_EditMSidedCardTemplateWdgt
from mnemosyne.libmnemosyne.ui_components.dialogs import \
     EditMSidedCardTemplateWidget


class EditMSidedCardTemplateWdgt(QtWidgets.QDialog,
                                 EditMSidedCardTemplateWidget,
                                 Ui_EditMSidedCardTemplateWdgt):

    def __init__(self, card_type, fact_view, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.card_type = card_type
        self.fact_view = fact_view
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        # Qt designer does not accept these special symbols.
        self.label1_2.setText("→")
        self.label1_3.setText("→")
        self.labelc1.setText("↗")
        self.labelc2.setText("↘")
        # Fill templates.
        self.front_template.setPlainText(self.fact_view.extra_data["qfmt"])
        self.back_template.setPlainText(self.fact_view.extra_data["afmt"])
        self.css.setPlainText(self.card_type.extra_data["css"])
        self.update_preview()
        # We only connect the signals now, because otherwise the multiple
        # updates in the lines above seem to cause html updates to go missing.
        self.front_template.textChanged.connect(self.front_template_changed)
        self.back_template.textChanged.connect(self.back_template_changed)
        self.css.textChanged.connect(self.css_changed)

    def front_template_changed(self):
        return self.update_preview(self.front_template)

    def back_template_changed(self):
        return self.update_preview(self.back_template)

    def css_changed(self):
        return self.update_preview(self.css)

    def update_preview(self, focus_widget=None):
        fact_data = {}
        for fact_key, name in self.card_type.fact_keys_and_names:
            if name == "Text" and \
               "{{cloze:Text}}" in self.front_template.toPlainText():
                fact_data[fact_key] = "This is a {{c1::sample}} cloze deletion."
            else:
                fact_data[fact_key] = "(" + name + ")"
        fact = Fact(fact_data)
        fact_view = copy.deepcopy(self.fact_view)
        fact_view.extra_data["qfmt"] = self.front_template.toPlainText()
        fact_view.extra_data["afmt"] = self.back_template.toPlainText()
        # We cannot deepcopy a card type because of card_type.name = _("foo").
        card_type = copy.copy(self.card_type)
        card_type.extra_data = copy.copy(self.card_type.extra_data)
        card_type.extra_data["css"] = self.css.toPlainText()
        card = Card(card_type, fact, fact_view)
        card.extra_data["ord"] = 0
        self.front_preview.setHtml(card.question())
        self.back_preview.setHtml(card.answer())
        # The html widget seems to grab the focus, so we need to restore the
        # focus to the editor if needed.
        if focus_widget:
            focus_widget.setFocus()

    def apply(self):
        # Check that the user didn't change the number of clozes.
        if self.fact_view.extra_data["qfmt"].count("{{cloze:Text}}") != \
           self.front_template.toPlainText().count("{{cloze:Text}}") or \
           self.fact_view.extra_data["afmt"].count("{{cloze:Text}}") != \
           self.back_template.toPlainText().count("{{cloze:Text}}"):
            self.main_widget().show_error(_(\
    "Changing the number of clozes in Anki cards is currently not supported."))
            return False
        # Apply changes.
        self.fact_view.extra_data["qfmt"] = self.front_template.toPlainText()
        self.fact_view.extra_data["afmt"] = self.back_template.toPlainText()
        self.card_type.extra_data["css"] = self.css.toPlainText()
        self.database().update_fact_view(self.fact_view)
        self.database().update_card_type(self.card_type)
        return True

