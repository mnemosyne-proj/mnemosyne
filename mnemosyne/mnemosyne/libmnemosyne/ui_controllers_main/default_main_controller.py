#
# default_main_controller.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

import copy
import datetime

from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.stopwatch import stopwatch
from mnemosyne.libmnemosyne.exceptions import MnemosyneError
from mnemosyne.libmnemosyne.component_manager import scheduler
from mnemosyne.libmnemosyne.component_manager import database, config
from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.component_manager import ui_controller_review
from mnemosyne.libmnemosyne.ui_controller_main import UiControllerMain


class DefaultMainController(UiControllerMain):

    def __init__(self):
        UiControllerMain.__init__(self)

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

    def create_new_cards(self, fact_data, card_type, grade, cat_names,
                         warn=True):

        """Create a new set of related cards."""

        # Allow this function to be overridden by a function hook.
        f = component_manager.get_current("function_hook", "create_new_cards")
        if f:
            return f.run()
        
        db = database()
        if db.has_fact_with_data(fact_data, card_type):
            if warn:
                self.widget.information_box(\
              _("Card is already in database.\nDuplicate not added."), _("OK"))
            return
        fact = Fact(fact_data, card_type)
        categories = []
        for cat_name in cat_names:
            categories.append(db.get_or_create_category_with_name(cat_name))
        duplicates = db.duplicates_for_fact(fact)
        if warn and len(duplicates) != 0:
            answer = self.widget.question_box(\
              _("There is already data present for:\n\N") +
              "".join(fact[k] for k in card_type.required_fields()),
              _("&Merge and edit"), _("&Add as is"), _("&Do not add"))
            if answer == 0: # Merge and edit.
                db.add_fact(fact)
                for card in card_type.create_related_cards(fact):
                    if grade != -1:
                        scheduler().set_initial_grade(card, grade)
                    db.add_card(card)  
                merged_fact_data = copy.copy(fact.data)
                for duplicate in duplicates:
                    for key in fact_data:
                        if key not in card_type.required_fields():
                            merged_fact_data[key] += " / " + duplicate[key]
                    db.delete_fact_and_related_data(duplicate)
                fact.data = merged_fact_data              
                self.widget.run_edit_fact_dialog(fact, allow_cancel=False)
                return
            if answer == 2: # Don't add.
                return
        db.add_fact(fact)
        cards = []
        for card in card_type.create_related_cards(fact):
            if grade != -1:
                scheduler().set_initial_grade(card, grade)
            card.categories = categories
            db.add_card(card)
            cards.append(card)
        db.save()
        if ui_controller_review().learning_ahead == True:
            ui_controller_review().reset()
        return cards # For testability.

    def update_related_cards(self, fact, new_fact_data, new_card_type, \
                             new_cat_names, correspondence, warn=True):
        # Allow this function to be overridden by a function hook.
        f = component_manager.get_current("function_hook", "update_related_cards")
        if f:
            return f.run()
        
        # Change card type.
        db = database()
        old_card_type = fact.card_type       
        if old_card_type != new_card_type:
            old_card_type_id_uncloned = old_card_type.id.split("_CLONED", 1)[0]
            new_card_type_id_uncloned = new_card_type.id.split("_CLONED", 1)[0] 
            converter = component_manager.get_current\
                  ("card_type_converter", used_for=(old_card_type.__class__,
                                                    new_card_type.__class__))
            if old_card_type_id_uncloned == new_card_type_id_uncloned:
                fact.card_type = new_card_type
                updated_cards = db.cards_from_fact(fact)      
            elif not converter:
                if warn:
                    answer = self.widget.question_box(\
          _("Can't preserve history when converting between these card types.")\
                  + " " + _("The learning history of the cards will be reset."),
                  _("&OK"), _("&Cancel"), "")
                else:
                    answer = 0
                if answer == 1: # Cancel.
                    return -1
                else:
                    db.delete_fact_and_related_data(fact)
                    self.create_new_cards(new_fact_data, new_card_type,
                                          grade=-1, cat_names=new_cat_names)
                    return 0
            else:
                # Make sure the converter operates on card objects which
                # already know their new type, otherwise we could get
                # conflicting id's.
                fact.card_type = new_card_type
                cards_to_be_updated = db.cards_from_fact(fact)
                for card in cards_to_be_updated:
                    card.fact = fact
                # Do the conversion.
                new_cards, updated_cards, deleted_cards = \
                   converter.convert(cards_to_be_updated, old_card_type,
                                     new_card_type, correspondence)
                if len(deleted_cards) != 0:
                    if warn:
                        answer = self.widget.question_box(\
          _("This will delete cards and their history.") + " " +\
          _("Are you sure you want to do this,") + " " +\
          _("and not just deactivate cards in the 'Activate cards' dialog?"),
                      _("&Proceed and delete"), _("&Cancel"), "")
                    else:
                        answer = 0
                    if answer == 1: # Cancel.
                        return -1
                for card in deleted_cards:
                    db.delete_card(card)
                for card in new_cards:
                    db.add_card(card)
                for card in updated_cards:
                    db.update_card(card)
                if new_cards and ui_controller_review().learning_ahead == True:
                    ui_controller_review().reset()
                    
        # Update facts and cards.
        new_cards, updated_cards, deleted_cards = \
            fact.card_type.update_related_cards(fact, new_fact_data)
        fact.modification_date = database().days_since_start()
        fact.data = new_fact_data
        db.update_fact(fact)
        for card in deleted_cards:
            db.delete_card(card)
        for card in new_cards:
            db.add_card(card)
        for card in updated_cards:
            db.update_card(card)
        if new_cards and ui_controller_review().learning_ahead == True:
            ui_controller_review().reset()
            
        # Update categories.
        old_cats = set()
        categories = []
        for cat_name in new_cat_names:
            categories.append(db.get_or_create_category_with_name(cat_name))
        for card in database().cards_from_fact(fact):
            old_cats = old_cats.union(set(card.categories))
            card.categories = categories
            db.update_card(card)
        for cat in old_cats:
            db.remove_category_if_unused(cat)
        db.save()

        # Update card present in UI.
        review_controller = ui_controller_review()
        if review_controller.card:
            review_controller.card = \
                database().get_card(review_controller.card.id)
            review_controller.update_dialog(redraw_all=True)
        return 0

    def delete_current_fact(self):
        stopwatch.pause()
        db = database()
        review_controller = ui_controller_review()
        fact = review_controller.card.fact
        no_of_cards = len(db.cards_from_fact(fact))
        if no_of_cards == 1:
            question = _("Delete this card?")
        elif no_of_cards == 2:
            question = _("Delete this card and 1 related card?") + " "  +\
                      _("Are you sure you want to do this,") + " " +\
          _("and not just deactivate cards in the 'Activate cards' dialog?")
        else:
            question = _("Delete this card and") + " " + str(no_of_cards - 1) \
                       + " " + _("related cards?") + " " +\
                       _("Are you sure you want to do this,") + " " +\
          _("and not just deactivate cards in the 'Activate cards' dialog?")
        answer = self.widget.question_box(question, _("&Delete"),
                                          _("&Cancel"), "")
        if answer == 1: # Cancel.
            return
        db.delete_fact_and_related_data(fact)
        db.save()
        review_controller.new_question()
        self.widget.update_status_bar()
        review_controller.update_dialog(redraw_all=True)
        stopwatch.unpause()

    def file_new(self):
        stopwatch.pause()
        db = database()
        suffix = db.suffix
        out = self.widget.save_file_dialog(path=config().basedir,
                            filter=_("Mnemosyne databases (*%s)" % suffix),
                            caption=_("New"))
        if not out:
            stopwatch.unpause()
            return
        if not out.endswith(suffix):
            out += suffix
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
            filter=_("Mnemosyne databases (*%s)" % database().suffix))
        if not out:
            stopwatch.unpause()
            return
        try:
            database().unload()
        except MnemosyneError, e:
            self.widget.show_exception(e)
            stopwatch.unpause()
            return            
        ui_controller_review().clear()
        try:
            database().load(out)
        except MnemosyneError, e:
            self.widget.show_exception(e)
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
            self.widget.show_exception(e)
        stopwatch.unpause()

    def file_save_as(self):
        stopwatch.pause()
        suffix = database().suffix
        old_path = expand_path(config()["path"])
        out = self.widget.save_file_dialog(path=old_path,
            filter=_("Mnemosyne databases (*%s)" % suffix))
        if not out:
            stopwatch.unpause()
            return
        if not out.endswith(suffix):
            out += suffix
        try:
            database().save(out)
        except MnemosyneError, e:
            self.widget.show_exception(e)
            stopwatch.unpause()
            return
        ui_controller_review().update_dialog()
        stopwatch.unpause()

    def card_appearance(self):
        stopwatch.pause()
        self.widget.run_card_appearance_dialog()
        ui_controller_review().update_dialog(redraw_all=True)
        stopwatch.unpause()
        
    def activate_plugins(self):
        stopwatch.pause()
        self.widget.run_activate_plugins_dialog()
        ui_controller_review().update_dialog(redraw_all=True)
        stopwatch.unpause()

    def manage_card_types(self):
        stopwatch.pause()
        self.widget.run_manage_card_types_dialog()
        stopwatch.unpause()
