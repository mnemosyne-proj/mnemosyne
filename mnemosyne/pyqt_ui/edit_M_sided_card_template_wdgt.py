# -*- coding: utf-8 -*-
#
# edit_M_sided_card_template_wdgt.py <Peter.Bienstman@UGent.be>
#

import copy

from PyQt5 import QtCore, QtWidgets

from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.fact import Fact
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
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        # Qt designer does not accept these special symbols.
        self.label1_2.setText("→")
        self.label1_3.setText("→")
        self.labelc1.setText("↗")
        self.labelc2.setText("↘")
        # Fill templates.
        self.redrawing = True
        self.front_template.setPlainText(self.fact_view.extra_data["qfmt"])
        self.back_template.setPlainText(self.fact_view.extra_data["afmt"])
        self.css.setPlainText(self.card_type.extra_data["css"])
        self.redrawing = False
        self.update_preview()
        # TODO: move to designer?
        self.front_template.textChanged.connect(self.update_preview)
        self.css.textChanged.connect(self.update_preview)
        self.back_template.textChanged.connect(self.update_preview)

    def update_preview(self):
        if self.redrawing:
            return
        print("update_preview")
        print(self.css.toPlainText())
        fact_data = {}
        for fact_key, name in self.card_type.fact_keys_and_names:
            fact_data[fact_key] = name
        fact = Fact(fact_data)
        fact_view = copy.deepcopy(self.fact_view)
        fact_view.extra_data["qfmt"] = self.front_template.toPlainText()
        fact_view.extra_data["afmt"] = self.back_template.toPlainText()
        # We cannot deepcopy a card type because of card_type.name = _("foo").
        card_type = copy.copy(self.card_type)
        card_type.extra_data = copy.copy(self.card_type.extra_data)
        card_type.extra_data["css"] = self.css.toPlainText()
        card = Card(card_type, fact, fact_view)
        card.extra_data["ord"] = 0 # TODO: check
        self.front_preview.setHtml(card.question())
        self.back_preview.setHtml(card.answer())

    def apply(self):
        pass
        # check if number of cards did not change.
        # TODO: <br>\n

