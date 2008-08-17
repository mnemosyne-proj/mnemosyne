#
# default_main_controller.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component_manager import get_database
from mnemosyne.libmnemosyne.ui_controller_main import UiControllerMain

class DefaultMainController(UiControllerMain):

    def __init__(self):
        UiControllerMain.__init__(self, name="Default main Controller")

    def create_new_cards(self, fact_data, card_type, grade, cat_names):

        """Create a new set of related cards, using the kind of information
        that is easily obtainable through a GUI.

        """

        db = get_database()
        if db.has_fact_with_data(fact_data):
            QMessageBox.information(None,
                                self.trUtf8("Mnemosyne"),
                                self.trUtf8("Card is already in database.\n")\
                                .append(self.trUtf8("Duplicate not added.")),
                                self.trUtf8("&OK"))
        fact = Fact(fact_data, cat_names, card_type)
        duplicates = db.duplicates_for_fact(fact)
        if len(duplicates) != 0:
            status = QMessageBox.question(None,
                   self.trUtf8("Mnemosyne"),
                   self.trUtf8("There are different answers for")\
                     .append(self.trUtf8(" this question:\n\n"))\
                     .append(answers),
                   self.trUtf8("&Merge and edit"),
                   self.trUtf8("&Add as is"),
                   self.trUtf8("&Do not add"), 0, -1)
            if status == 0: # Merge and edit.
                merged_fact_data = copy.copy(fact.data)
                for key in f:
                    if key != field:
                        merged_fact_data[key] += "/" + f[key]

                for duplicate in duplicates:
                    delete_fact_and_its_cards(duplicate)
                print merged_fact_data
                #dlg = EditItemDlg(new_item, self)
                #dlg.exec_loop()
                #get fact from that
            if status == 2: # Don't add.
                return
        db.add_fact(fact)
        for fact_view in self.fact_views:
            card = Card(grade, fact, fact_view)
            card.set_initial_grade(grade)
            db.add_card(card)


    def update_cards(self):
        raise NotImplementedError