#
# default_main_controller.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

import copy

from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.stopwatch import stopwatch
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import ui_controller_review
from mnemosyne.libmnemosyne.ui_controller_main import UiControllerMain


class DefaultMainController(UiControllerMain):

    def __init__(self):
        UiControllerMain.__init__(self, name="Default main Controller")

    def add_cards(self):
        stopwatch.pause()
        self.widget.run_add_cards_dialog()
        review_controller = ui_controller_review()
        if review_controller.card == None:
            review_controller.new_question()
        else:
            self.widget.update_status_bar()
        stopwatch.unpause()

    def create_new_cards(self, fact_data, card_type, grade, cat_names):

        """Create a new set of related cards"""

        db = database()
        if db.has_fact_with_data(fact_data):
            self.widget.information_box(\
              _("Card is already in database.\nDuplicate not added."), _("OK"))
            return
        fact = Fact(fact_data, card_type)        
        for cat_name in cat_names:
            fact.cat.append(db.get_or_create_category_with_name(cat_name))
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
                    db.delete_fact_and_related_data(duplicate)
                print merged_fact_data
                # TODO: edit merged data.
                #dlg = EditItemDlg(new_item, self)
                #dlg.exec_loop()
                #get fact from that
            if answer == 2: # Don't add.
                return
        db.add_fact(fact)
        card_type.create_related_cards(fact, grade)

