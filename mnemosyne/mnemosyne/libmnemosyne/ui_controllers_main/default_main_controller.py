#
# default_main_controller.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

import copy

from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.stopwatch import stopwatch
from mnemosyne.libmnemosyne.exceptions import MnemosyneError
from mnemosyne.libmnemosyne.component_manager import database, config
from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.component_manager import ui_controller_review
from mnemosyne.libmnemosyne.ui_controller_main import UiControllerMain


class DefaultMainController(UiControllerMain):

    def __init__(self):
        UiControllerMain.__init__(self, name="Default main controller")

    def add_cards(self):
        stopwatch.pause()
        self.widget.run_add_cards_dialog()
        review_controller = ui_controller_review()
        if review_controller.card == None:
            review_controller.new_question()
        else:
            self.widget.update_status_bar()
        stopwatch.unpause()

    def edit_current_card(self):
        stopwatch.pause()
        review_controller = ui_controller_review()
        self.widget.run_edit_fact_dialog(review_controller.card.fact)
        if review_controller.card == None:
            self.widget.update_status_bar()
            review_controller.new_question()         
        review_controller.update_dialog(redraw_all=True)
        stopwatch.unpause()

    def create_new_cards(self, fact_data, card_type, grade, cat_names):

        """Create a new set of related cards."""

        # Allow this function to be overridden by a function hook.
        f = component_manager.get_current("function_hook", "create_new_cards")
        if f:
            return f.run()
        
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
        for card in card_type.create_related_cards(fact, grade):
            db.add_card(card)

    def update_related_cards(self, fact, new_fact_data, new_card_type, \
                             new_cat_names):
        # Allow this function to be overridden by a function hook.
        f = component_manager.get_current("function_hook", "update_related_cards")
        if f:
            return f.run()

        # Change card type.
        db = database()
        old_card_type = fact.card_type
        if old_card_type != new_card_type:
            converter = component_manager.get_current\
                  ("card_type_converter", used_for=(old_card_type,
                                                    new_card_type))
            if not converter:
                answer = self.widget.question_box(\
          _("Can't preserve history when converting between these card types.")\
                  + " " + _("The learning history of the cards will be reset."),
                  _("&OK"), _("&Cancel"), "")
                if answer == 1: # Cancel.
                    return
                else:
                    db.delete_fact_and_related_data(fact)
                    self.create_new_cards(new_fact_data, new_card_type,
                                          grade=0, cat_names=new_cat_names)
                    return
            else:
                converter.convert(db.cards_from_fact(fact))
                fact.card_type = new_card_type
        # Update categories, facts and cards.
        old_cats = fact.cat
        fact.cat = []
        for cat_name in new_cat_names:
            fact.cat.append(db.get_or_create_category_with_name(cat_name))
        for cat in old_cats:
            db.remove_category_if_unused(cat)
        new_cards, updated_cards = fact.card_type.update_related_cards(fact, \
                                                new_fact_data)
        db.update_fact(fact)
        for card in new_cards:
            db.add_card(card)
        for card in updated_cards:
            db.update_card(card)
        return
        # TODO: duplicate checking.
        if db.has_fact_with_data(fact_data):
            self.widget.information_box(\
              _("Card is already in database.\nDuplicate not added."), _("OK"))
            return
        fact = Fact(fact_data, card_type)
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
        for card in card_type.create_related_cards(fact, grade):
            db.add_card(card)

    def file_new(self):
        stopwatch.pause()
        out = self.widget.save_file_dialog(path=config().basedir,
                            filter=_("Mnemosyne databases (*.mem)"),
                            caption=_("New"))
        if not out:
            stopwatch.unpause()
            return
        if not out.endswith(".mem"):
            out += ".mem"
        db = database()
        db.unload()
        db.new(out)
        db.load(config()["path"])
        ui_controller_review().clear()
        ui_controller_review().update_dialog()
        stopwatch.unpause()

    def file_open(self):
        stopwatch.pause()
        old_path = expand_path(config()["path"])
        out = self.widget.open_file_dialog(path=old_path,
                            filter=_("Mnemosyne databases (*.mem)"))
        if not out:
            stopwatch.unpause()
            return
        try:
            database().unload()
        except MnemosyneError, e:
            self.widget.error_box(e)
            stopwatch.unpause()
            return            
        ui_controller_review().clear()
        try:
            database().load(out)
        except MnemosyneError, e:
            self.widget.error_box(e)
            stopwatch.unpause()
            return
        ui_controller_review().new_question()
        stopwatch.unpause()

    def file_save(self):
        stopwatch.pause()
        path = config()["path"]
        try:
            database().save(path)
        except MnemosyneError, e:
            self.widget.error_box(e)
        stopwatch.unpause()

    def file_save_as(self):
        stopwatch.pause()
        old_path = expand_path(config()["path"])
        out = self.widget.save_file_dialog(path=old_path,
                            filter=_("Mnemosyne databases (*.mem)"))
        if not out:
            stopwatch.unpause()
            return
        if not out.endswith(".mem"):
            out += ".mem"
        try:
            database().save(out)
        except MnemosyneError, e:
            self.widget.error_box(e)
            stopwatch.unpause()
            return
        ui_controller_review().update_dialog()
        stopwatch.unpause()
