#
# default_main_controller.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

import copy

from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.ui_controller_main import UiControllerMain


class DefaultMainController(UiControllerMain):

    def __init__(self):
        UiControllerMain.__init__(self, name="Default main Controller")

    def create_new_cards(self, fact_data, card_type, grade, cat_names):

        """Create a new set of related cards"""

        db = database()
        if db.has_fact_with_data(fact_data):
            self.widget.information_box(\
              _("Card is already in database.\nDuplicate not added."), _("OK"))
        fact = Fact(fact_data, cat_names, card_type)
        duplicates = db.duplicates_for_fact(fact)
        if len(duplicates) != 0:
            answer = self.widget.question_box(\
              _("There is already data present for:\n\n") +
              "".join(fact[k] for k in card_type.required_fields()),
              _("&Merge and edit"), _("&Add as is"), _("&Do not add"))
            if answer == 0: # Merge and edit.
                merged_fact_data = copy.copy(fact.data)
                for duplicate in duplicates:
                    for key in fact_data:
                        if key not in card_type.required_fields():
                            merged_fact_data[key] += "/" + duplicate[key]
                    db.delete_fact_and_its_cards(duplicate)
                print merged_fact_data
                # TODO: edit merged data.
                #dlg = EditItemDlg(new_item, self)
                #dlg.exec_loop()
                #get fact from that
            if answer == 2: # Don't add.
                return
        db.add_fact(fact)
        for fact_view in card_type.fact_views:
            card = Card(fact, fact_view)
            card.set_initial_grade(grade)
            db.add_card(card)

    def update_cards(self):
        raise NotImplementedError
