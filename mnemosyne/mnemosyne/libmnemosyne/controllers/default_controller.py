#
# default_controller.py <Peter.Bienstman@UGent.be>
#

import os
import copy
import time

from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.controller import Controller
from mnemosyne.libmnemosyne.utils import expand_path, contract_path


class DefaultController(Controller):

    def heartbeat(self):

        """To be called once a day, to make sure, even if the user leaves the
        program open indefinitely, that backups get taken, that the cards
        scheduled for the day get dumped to the log and that the the logs get
        uploaded.

        """
        
        self.database().backup()
        self.log().saved_database()
        self.log().loaded_database()        
        self.log().dump_to_txt_log()
        self.log().deactivate()
        self.log().activate()
        
    def update_title(self):
        database_name = os.path.basename(self.config()["path"]).\
            split(self.database().suffix)[0]
        title = _("Mnemosyne")
        if database_name != _("default"):
            title += " - " + database_name
        self.main_widget().set_window_title(title)

    def add_cards(self):
        self.stopwatch().pause()
        self.component_manager.get_current("add_cards_dialog")\
            (self.component_manager).activate()
        self.database().save()
        review_controller = self.review_controller()
        review_controller.reload_counters()
        if review_controller.card is None:
            review_controller.new_question()
        else:
            review_controller.update_status_bar()
        self.stopwatch().unpause()

    def edit_current_card(self):
        self.stopwatch().pause()
        review_controller = self.review_controller()
        fact = review_controller.card.fact
        self.component_manager.get_current("edit_fact_dialog")\
            (fact, self.component_manager).activate()
        review_controller.reload_counters()
        # Our current card could have disappeared from the database here,
        # e.g. when converting a front-to-back card to a cloze card, which
        # deletes the old cards and their learning history.
        if review_controller.card is None:
            review_controller.new_question()
        else:
            review_controller.card = self.database().get_card(\
                review_controller.card._id, id_is_internal=True)
            review_controller.update_dialog(redraw_all=True)
        self.stopwatch().unpause()
        
    def create_new_cards(self, fact_data, card_type, grade, tag_names,
                         check_for_duplicates=True, save=True):

        """Create a new set of related cards. If the grade is 2 or higher,
        we perform a initial review with that grade and move the cards into
        the long term retention process. For other grades, we treat the card
        as still unseen and keep its grade at -1. This puts the card on equal
        footing with ungraded cards created during the import process. These
        ungraded cards are pulled in at the end of the review process, either
        in the order they were added, on in random order.

        """

        if grade in [0,1]:
            raise AttributeError, "Use -1 as grade for unlearned cards."
        db = self.database()
        fact = Fact(fact_data, card_type)
        if check_for_duplicates:
            duplicates = db.duplicates_for_fact(fact)
            if len(duplicates) != 0:
                for duplicate in duplicates:
                    # Duplicates only checks equality of unique keys.
                    if duplicate.data == fact_data:
                        self.main_widget().information_box(\
                    _("Card is already in database.\nDuplicate not added."))
                    return                
                answer = self.main_widget().question_box(\
                  _("There is already data present for:\n\N") +
                  "".join(fact[k] for k in card_type.required_fields),
                  _("&Merge and edit"), _("&Add as is"), _("&Do not add"))
                if answer == 0: # Merge and edit.
                    db.add_fact(fact)
                    for card in card_type.create_related_cards(fact):
                        if grade >= 2:
                            self.scheduler().set_initial_grade(card, grade)
                        db.add_card(card)  
                    merged_fact_data = copy.copy(fact.data)
                    for duplicate in duplicates:
                        for key in fact_data:
                            if key not in card_type.required_fields:
                                merged_fact_data[key] += " / " + duplicate[key]
                        db.delete_fact_and_related_data(duplicate)
                    fact.data = merged_fact_data
                    self.component_manager.get_current("edit_fact_dialog")\
                      (fact, self.component_manager, allow_cancel=False).\
                      activate()
                    return
                if answer == 2:  # Don't add.
                    return
        db.add_fact(fact)
        tags = set()
        for tag_name in tag_names:
            tags.add(db.get_or_create_tag_with_name(tag_name))
        cards = []
        criterion = db.current_activity_criterion()
        for card in card_type.create_related_cards(fact):
            self.log().added_card(card)
            if grade >= 2:
                self.scheduler().set_initial_grade(card, grade)
            card.tags = tags
            criterion.apply_to_card(card)
            db.add_card(card)
            cards.append(card)
        if save:
            db.save()
        if self.review_controller().learning_ahead == True:
            self.review_controller().reset()
        return cards

    def update_related_cards(self, fact, new_fact_data, new_card_type, \
                             new_tag_names, correspondence):
        # Change card type.
        db = self.database()
        sch = self.scheduler()
        old_card_type = fact.card_type
        if old_card_type != new_card_type:
            converter = self.component_manager.get_current\
                  ("card_type_converter", used_for=(old_card_type.__class__,
                                                    new_card_type.__class__))
            if not converter:
                # Perhaps they have a common ancestor.
                parents_old = old_card_type.id.split("::")
                parents_new = new_card_type.id.split("::")
                if parents_old[0] == parents_new[0]: 
                    fact.card_type = new_card_type
                    updated_cards = db.cards_from_fact(fact)      
                else:
                    answer = self.main_widget().question_box(\
         _("Can't preserve history when converting between these card types.")\
                 + " " + _("The learning history of the cards will be reset."),
                      _("&OK"), _("&Cancel"), "")
                    if answer == 1:   # Cancel.
                        return -1
                    else:
                        db.delete_fact_and_related_data(fact)
                        card = self.create_new_cards(new_fact_data,
                          new_card_type, grade=-1, tag_names=new_tag_names)[0]
                        self.review_controller().card = card
                        return 0
            else:
                # Make sure the converter operates on card objects which
                # already know their new type, otherwise we could get
                # conflicting ids.
                fact.card_type = new_card_type
                cards_to_be_updated = db.cards_from_fact(fact)
                for card in cards_to_be_updated:
                    card.fact = fact
                # Do the conversion.
                new_cards, updated_cards, deleted_cards = \
                   converter.convert(cards_to_be_updated, old_card_type,
                                     new_card_type, correspondence)
                if len(deleted_cards) != 0:
                    answer = self.main_widget().question_box(\
          _("This will delete cards and their history.") + " " +\
          _("Are you sure you want to do this,") + " " +\
          _("and not just deactivate cards in the 'Activate cards' dialog?"),
                      _("&Proceed and delete"), _("&Cancel"), "")
                    if answer == 1:  # Cancel.
                        return -1
                for card in deleted_cards:
                    if self.review_controller().card == card:
                        self.review_controller().card = None
                    sch.remove_from_queue_if_present(card)
                    db.delete_card(card)
                for card in new_cards:
                    db.add_card(card)
                for card in updated_cards:
                    db.update_card(card)
                if new_cards and self.review_controller().learning_ahead:
                    self.review_controller().reset()
                    
        # Update facts and cards.
        new_cards, updated_cards, deleted_cards = \
            fact.card_type.update_related_cards(fact, new_fact_data)
        fact.modification_time = int(time.time())
        fact.data = new_fact_data
        db.update_fact(fact)
        for card in deleted_cards:
            if self.review_controller().card == card:
                self.review_controller().card = None
            sch.remove_from_queue_if_present(card)
            db.delete_card(card)
        for card in new_cards:
            db.add_card(card)
        for card in updated_cards:
            db.update_card(card)
        if new_cards and self.review_controller().learning_ahead == True:
            self.review_controller().reset()
            
        # Update tags.
        old_tags = set()
        tags = set()
        for tag_name in new_tag_names:
            tags.add(db.get_or_create_tag_with_name(tag_name))
        for card in self.database().cards_from_fact(fact):
            old_tags = old_tags.union(card.tags)
            card.tags = tags
            db.update_card(card)
        for tag in old_tags:
            db.remove_tag_if_unused(tag)
        db.save()

        # Update active flags.
        criterion = db.current_activity_criterion()
        for card in self.database().cards_from_fact(fact):
            criterion.apply_to_card(card)
            db.update_card(card)
                
        return 0

    def delete_current_fact(self):
        self.stopwatch().pause()
        db = self.database()
        review_controller = self.review_controller()
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
        answer = self.main_widget().question_box(question, _("&Delete"),
                                          _("&Cancel"), "")
        if answer == 1:  # Cancel.
            self.stopwatch().unpause()
            return
        db.delete_fact_and_related_data(fact)
        db.save()
        review_controller.reload_counters()
        review_controller.new_question()
        self.stopwatch().unpause()

    def clone_card_type(self, card_type, clone_name):
        from mnemosyne.libmnemosyne.utils import mangle
        
        clone_id = card_type.id + "::" + clone_name
        if clone_id in [card_t.id for card_t in self.card_types()]:
            self.main_widget().error_box(_("Card type name already exists."))
            return None
        card_type_class = type(mangle(clone_name), (card_type.__class__, ),
            {"name": clone_name, "id": clone_id})
        cloned_card_type = card_type_class(self.component_manager)
        self.database().add_card_type(cloned_card_type)
        self.component_manager.register(cloned_card_type)
        self.database().save()
        return cloned_card_type
    
    def file_new(self):
        self.stopwatch().pause()
        db = self.database()
        suffix = db.suffix
        filename = self.main_widget().save_file_dialog(\
            path=self.config().basedir, filter=_("Mnemosyne databases") + \
            " (*%s)" % suffix, caption=_("New"))
        if not filename:
            self.stopwatch().unpause()
            return
        if not filename.endswith(suffix):
            filename += suffix
        db.backup()
        db.unload()
        # Confirmation on overwrite has happened in the file dialog code.
        if os.path.exists(filename):
            import shutil
            shutil.rmtree(filename + "_media")
        db.new(filename)
        db.load(self.config()["path"])
        self.log().loaded_database()
        self.review_controller().reset()
        self.review_controller().update_dialog()
        self.update_title()
        self.stopwatch().unpause()

    def file_open(self):
        self.stopwatch().pause()
        db = self.database()
        basedir = self.config().basedir
        old_path = expand_path(self.config()["path"], basedir)
        filename = self.main_widget().open_file_dialog(path=old_path,
            filter=_("Mnemosyne databases") + " (*%s)" % db.suffix)
        if not filename:
            self.stopwatch().unpause()
            return
        if filename.startswith(os.path.join(basedir, "backups")):
            result = self.main_widget().question_box(\
                _("Do you want to restore from this backup?"),
                _("Yes"), _("No"), "")
            if result == 0:  # Yes.
                db.abandon()
                db_path = expand_path(self.config()["path"], basedir)
                import shutil
                shutil.copy(filename, db_path)
                db.load(db_path)
                self.review_controller().reset()
                self.update_title()
            self.stopwatch().unpause()
            return  
        try:
            self.log().saved_database()
            db.backup()
            db.unload()
        except RuntimeError, error:
            self.main_widget().error_box(unicode(error))
            self.stopwatch().unpause()
            return            
        try:
            db.load(filename)
            self.log().loaded_database()
        except Exception, e:
            self.main_widget().show_exception(e)
            self.stopwatch().unpause()
            return
        self.review_controller().reset()
        self.update_title()
        self.stopwatch().unpause()

    def file_save(self):
        self.stopwatch().pause()
        try:
            self.database().save()
            self.log().saved_database()
        except RuntimeError, error:
            self.main_widget().error_box(unicode(error))
        self.stopwatch().unpause()

    def file_save_as(self):
        self.stopwatch().pause()
        suffix = self.database().suffix
        old_path = expand_path(self.config()["path"], self.config().basedir)
        filename = self.main_widget().save_file_dialog(path=old_path,
            filter=_("Mnemosyne databases") + " (*%s)" % suffix)
        if not filename:
            self.stopwatch().unpause()
            return
        if not filename.endswith(suffix):
            filename += suffix
        try:
            self.database().save(filename)
            self.log().saved_database()
        except RuntimeError, error:
            self.main_widget().error_box(unicode(error))
            self.stopwatch().unpause()
            return
        self.review_controller().update_dialog()
        self.update_title()
        self.stopwatch().unpause()

    def insert_img(self, filter):

        """Show a file dialog filtered on the supported filetypes, get a
        filename, massage it, and return it to the widget to be inserted.
        There is more media file logic inside the database code too, as the
        user could also just type in the html tags as opposed to passing
        through the fileselector here.

        """

        from mnemosyne.libmnemosyne.utils import copy_file_to_dir
        basedir, mediadir = self.config().basedir, self.config().mediadir()
        path = expand_path(self.config()["import_img_dir"], basedir)
        filter = _("Image files") + " " + filter
        filename = self.main_widget().open_file_dialog(\
            path, filter, _("Insert image"))
        if not filename:
            return ""
        else:
            self.config()["import_img_dir"] = contract_path(\
                os.path.dirname(filename), basedir)
            filename = copy_file_to_dir(filename, mediadir)
            return contract_path(filename, mediadir)
        
    def insert_sound(self, filter):
        from mnemosyne.libmnemosyne.utils import copy_file_to_dir
        basedir, mediadir = self.config().basedir, self.config().mediadir()
        path = expand_path(self.config()["import_sound_dir"], basedir)
        filter = _("Sound files") + " " + filter
        filename = self.main_widget().open_file_dialog(\
            path, filter, _("Insert sound"))
        if not filename:
            return ""
        else:
            self.config()["import_sound_dir"] = contract_path(\
                os.path.dirname(filename), basedir)
            filename = copy_file_to_dir(filename, mediadir)
            return filename
        
    def insert_video(self, filter):
        from mnemosyne.libmnemosyne.utils import copy_file_to_dir
        basedir, mediadir = self.config().basedir, self.config().mediadir()
        path = expand_path(self.config()["import_video_dir"], basedir)
        filter = _("Video files") + " " + filter
        filename = self.main_widget().open_file_dialog(\
            path, filter, _("Insert video"))
        if not filename:
            return ""
        else:
            self.config()["import_video_dir"] = contract_path(\
                os.path.dirname(filename), basedir)
            filename = copy_file_to_dir(filename, mediadir)
            return filename
        
    def activate_cards(self):
        self.stopwatch().pause()
        self.component_manager.get_current("activate_cards_dialog")\
            (self.component_manager).activate()
        review_controller = self.review_controller()
        review_controller.reset_but_try_to_keep_current_card()
        review_controller.update_status_bar()
        self.stopwatch().unpause()
        
    def browse_cards(self):
        self.stopwatch().pause()
        self.component_manager.get_current("browse_cards_dialog")\
            (self.component_manager).activate()
        self.stopwatch().unpause()
        
    def card_appearance(self):
        self.stopwatch().pause()
        self.component_manager.get_current("card_appearance_dialog")\
            (self.component_manager).activate()
        self.review_controller().update_dialog(redraw_all=True)
        self.stopwatch().unpause()
        
    def activate_plugins(self):
        self.stopwatch().pause()
        self.component_manager.get_current("activate_plugins_dialog")\
            (self.component_manager).activate()
        self.review_controller().update_dialog(redraw_all=True)
        self.stopwatch().unpause()

    def manage_card_types(self):
        self.stopwatch().pause()
        self.component_manager.get_current("manage_card_types_dialog")\
            (self.component_manager).activate()
        self.stopwatch().unpause()
        
    def show_statistics(self):
        self.stopwatch().pause()
        self.component_manager.get_current("statistics_dialog")\
            (self.component_manager).activate()
        self.stopwatch().unpause()
        
    def configure(self):
        self.stopwatch().pause()
        self.component_manager.get_current("configuration_dialog")\
            (self.component_manager).activate()
        self.review_controller().reset_but_try_to_keep_current_card()
        self.stopwatch().unpause()
        
    def import_file(self):
        self.stopwatch().pause()
        path = expand_path(self.config()["import_dir"], self.config().basedir)

        # TMP hardcoded single fileformat.
        filename = self.main_widget().open_file_dialog(path=path,
            filter=_("Mnemosyne 1.x databases") + " (*.mem)")
        if not filename:
            self.stopwatch().unpause()
            return
        self.component_manager.get_current("file_format").do_import(filename)
        self.database().save()
        review_controller = self.review_controller()
        review_controller.reload_counters()
        if review_controller.card is None:
            review_controller.new_question()
        else:
            review_controller.update_status_bar()
        self.stopwatch().unpause()

    def export_file(self):
        self.stopwatch().pause()

        self.stopwatch().unpause()

    def download_source(self):

        """The following code is here to be able to enforce the AGPL licence.
        
        If you run Mnemosyne as a service over the network, you need to provide
        users the option to download your modified version of libmnemosyne and
        the Mnemosyne HTML server.

        The recommended way to do this is to provide a link at the bottom of
        the webpage saying "Flash cards by Mnemosyne", with "Mnemosyne" a link
        taking you to a page with download instructions for the copy of
        Mnemosyne you are using.

        Even if you are using an unmodified version of Mnemosyne, you should
        still host a copy of that source code on your site, in order to set an
        example for people who do modify the source.

        """
        
        self.stopwatch().pause()
        self.self.main_widget().information_box(\
            _("For instructions on how to download Mnemosyne's source,") + \
            + " " + _("go to http://www.mnemosyne-proj.org"))
        self.stopwatch().unpause()        
