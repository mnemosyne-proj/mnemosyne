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

    """A collection of logic used by the GUI.  The logic related to the
    review process is split out in a separated controller class, to
    allow that to be swapped out easily.

    There are two classes of functions here: 'show_XXX_dialog', which needs
    to be called by the GUI to set everything up to show a certain dialog,
    and then the other functions, which the implementation of the actual
    dialog can use to perform GUI-independent operations.

    See also 'How to write a new frontend' in the docs.

    """    

    def heartbeat(self):

        """To be called once a day, to make sure, even if the user leaves the
        program open indefinitely, that backups get taken, that the cards
        scheduled for the day get dumped to the log and that the the logs get
        uploaded.

        """
        
        self.flush_sync_server()        
        self.database().backup()
        self.log().saved_database()
        self.log().loaded_database()        
        self.log().dump_to_science_log()
        self.log().deactivate()
        self.log().activate()
        
    def update_title(self):
        title = _("Mnemosyne")
        database_name = self.database().display_name()
        if database_name != self.database().default_name:
            title += " - " + database_name
        self.main_widget().set_window_title(title)

    def show_add_cards_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("add_cards_dialog")\
            (self.component_manager).activate()
        # This dialog calls 'create_new_cards' at some point.
        self.database().save()
        review_controller = self.review_controller()
        review_controller.reload_counters()
        if review_controller.card is None:
            review_controller.show_new_question()
        else:
            review_controller.update_status_bar_counters()
        self.stopwatch().unpause()
        
    def create_new_cards(self, fact_data, card_type, grade, tag_names,
                         check_for_duplicates=True, save=True):

        """Create a new set of sister cards. If the grade is 2 or higher,
        we perform a initial review with that grade and move the cards into
        the long term retention process. For other grades, we treat the card
        as still unseen and keep its grade at -1. This puts the card on equal
        footing with ungraded cards created during the import process. These
        ungraded cards are pulled in at the end of the review process, either
        in the order they were added, on in random order.

        """

        assert grade in [-1, 2, 3, 4, 5] # Use -1 for yet to learn cards.
        assert card_type.is_data_valid(fact_data)
        db = self.database()
        tags = db.get_or_create_tags_with_names(tag_names)
        fact = Fact(fact_data)
        if check_for_duplicates:
            duplicates = db.duplicates_for_fact(fact, card_type)
            if len(duplicates) != 0:
                for duplicate in duplicates:
                    # Duplicates only checks equality of unique keys.
                    if duplicate.data == fact_data:
                        self.main_widget().show_information(\
                    _("Card is already in database.\nDuplicate not added."))
                        return
                answer = self.main_widget().show_question(\
                  _("There is already data present for:\n\n") +
                  "".join(fact[k] for k in card_type.required_fields),
                  _("&Merge and edit"), _("&Add as is"), _("&Do not add"))
                if answer == 0: # Merge and edit.
                    db.add_fact(fact)
                    for card in card_type.create_sister_cards(fact):
                        card.tags = tags
                        db.add_card(card)
                        if grade >= 2:
                            self.scheduler().set_initial_grade(card, grade)
                            db.update_card(card, repetition_only=True)
                    merged_fact_data = copy.copy(fact.data)
                    for duplicate in duplicates:
                        for key in fact_data:
                            if key not in card_type.required_fields \
                                and key in duplicate.data:
                                merged_fact_data[key] += " / " + duplicate[key]
                    self.delete_facts_and_their_cards(duplicates)
                    card = db.cards_from_fact(fact)[0]
                    card.fact.data = merged_fact_data
                    self.component_manager.current("edit_card_dialog")\
                        (card, self.component_manager, allow_cancel=False).\
                        activate()
                    return
                if answer == 2:  # Don't add.
                    return
        db.add_fact(fact)
        # Create cards.
        cards = []
        for card in card_type.create_sister_cards(fact):
            card.tags = tags
            db.add_card(card)
            if grade >= 2:
                self.scheduler().set_initial_grade(card, grade)
                db.update_card(card, repetition_only=True)
            cards.append(card)
        if save:
            db.save()
        if self.review_controller().learning_ahead == True:
            self.review_controller().reset()
        return cards

    def show_edit_card_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        review_controller = self.review_controller()
        self.component_manager.current("edit_card_dialog")\
            (review_controller.card, self.component_manager).activate()
        # This dialog calls 'edit_sister_cards' at some point.
        review_controller.reload_counters()    
        # Our current card could have disappeared from the database here,
        # e.g. when converting a front-to-back card to a cloze card, which
        # deletes the old cards and their learning history.
        if review_controller.card is None:
            review_controller.show_new_question()
        else:
            review_controller.card = self.database().card(\
                review_controller.card._id, is_id_internal=True)
            # Our current card could have picked up a forbidden tag.
            if review_controller.card.active == False: 
                review_controller.show_new_question()
            review_controller.update_dialog(redraw_all=True)
        self.stopwatch().unpause()
        
    def _change_card_type(self, fact, old_card_type, new_card_type,
                          correspondence, new_fact_data, warn=True):

        """This is an internal function, used by 'edit_sister_cards' and
        'change_card_type'. It should not be called from the outside by
        itself, otherwise the database will not be saved.

        """

        if old_card_type == new_card_type:
            return 0
        db = self.database()
        cards_from_fact = db.cards_from_fact(fact)
        assert cards_from_fact[0].card_type == old_card_type
        assert new_card_type.is_data_valid(new_fact_data)
        converter = self.component_manager.current\
              ("card_type_converter", used_for=(old_card_type.__class__,
                                                new_card_type.__class__))
        if not converter:
            # Perhaps they have a common ancestor.
            parents_old = old_card_type.id.split("::")
            parents_new = new_card_type.id.split("::")
            if parents_old[0] == parents_new[0]: 
                edited_cards = cards_from_fact
                new_fact_view_for = {}
                for index, old_fact_view in enumerate(old_card_type.fact_views):
                    new_fact_view_for[old_fact_view] = \
                        new_card_type.fact_views[index]
                for card in edited_cards:
                    card.card_type = new_card_type
                    card.fact_view = new_fact_view_for[card.fact_view]
                    db.update_card(card)
            else:
                if warn:
                    answer = self.main_widget().show_question(\
         _("Can't preserve history when converting between these card types.")\
                 + " " + _("The learning history of the cards will be reset."),
                 _("&OK"), _("&Cancel"), "")
                    if answer == 1:  # Cancel.
                        return -1  
                # Go ahead with conversion
                is_currently_asked = \
                   self.review_controller().card in cards_from_fact
                tag_names = cards_from_fact[0].tag_string().split(", ")
                self.delete_facts_and_their_cards([fact])                        
                new_card = self.create_new_cards(new_fact_data,
                    new_card_type, grade=-1, tag_names=tag_names)[0]
                if is_currently_asked:
                    self.review_controller().card = new_card
                return 0
        else:
            for card in cards_from_fact:
                card.card_type = new_card_type
                card.fact = fact
            new_cards, edited_cards, deleted_cards = converter.convert(\
                cards_from_fact, old_card_type, new_card_type, correspondence)
            if warn and len(deleted_cards) != 0:
                answer = self.main_widget().show_question(\
          _("This will delete cards and their history.") + " " +\
          _("Are you sure you want to do this,") + " " +\
          _("and not just deactivate cards in the 'Activate cards' dialog?"),
                 _("&Proceed and delete"), _("&Cancel"), "")
                if answer == 1:  # Cancel.
                    return -1
            for card in deleted_cards:
                if self.review_controller().card == card:
                    self.review_controller().card = None
                self.scheduler().remove_from_queue_if_present(card)
                db.delete_card(card)
            for card in new_cards:
                card.tags = cards_from_fact[0].tags
                db.add_card(card)
            for card in edited_cards:
                db.update_card(card)
            if new_cards and self.review_controller().learning_ahead:
                self.review_controller().reset()
            return 0
        
    def edit_sister_cards(self, fact, new_fact_data, old_card_type,
            new_card_type, new_tag_names, correspondence):        
        db = self.database()
        sch = self.scheduler()
        assert new_card_type.is_data_valid(new_fact_data)
        # If the old fact contained media, we need to check for orphans.
        clean_orphaned_static_media_files_needed = \
            db.fact_contains_static_media_files(fact)
        # Change card type first.
        result = self._change_card_type(fact, old_card_type, new_card_type,
            correspondence, new_fact_data)
        if result == -1:  # Aborted.
            return -1  
        # Update fact and create or delete cards.
        new_cards, edited_cards, deleted_cards = \
            new_card_type.edit_sister_cards(fact, new_fact_data)
        fact.data = new_fact_data
        db.update_fact(fact)
        for card in deleted_cards:
            if self.review_controller().card == card:
                self.review_controller().card = None
            sch.remove_from_queue_if_present(card)
            db.delete_card(card)
        for card in new_cards:
            db.add_card(card)
        if new_cards and self.review_controller().learning_ahead == True:
            self.review_controller().reset()
        # Apply new tags and modification time to cards and save them back to
        # the database. Note that this makes sure there is an EDITED_CARD log
        # entry for each sister card, which is needed when syncing with a
        # partner that does not have the concept of facts.
        old_tags = set()
        tags = db.get_or_create_tags_with_names(new_tag_names)    
        modification_time = int(time.time())
        for card in self.database().cards_from_fact(fact):
            card.modification_time = modification_time
            old_tags = old_tags.union(card.tags)
            card.tags = tags
            db.update_card(card)
        for tag in old_tags:
            db.delete_tag_if_unused(tag)
        if clean_orphaned_static_media_files_needed:
            db.clean_orphaned_static_media_files()        
        db.save()       
        return 0

    def change_card_type(self, facts, old_card_type, new_card_type,
                         correspondence):

        """Note: all facts should have the same card type."""
        
        db = self.database()
        clean_orphaned_static_media_files_needed = False  
        for fact in facts:
            if db.fact_contains_static_media_files(fact):
                clean_orphaned_static_media_files_needed = True
        warn = True
        w = self.main_widget()
        w.set_progress_text(_("Converting cards..."))
        w.set_progress_range(0, len(facts))
        w.set_progress_update_interval(len(facts)/50)
        count = 0
        w.set_progress_value(0)
        for fact in facts:
            if correspondence:
                new_fact_data = {}
                for old_key, new_key in correspondence.iteritems():
                    new_fact_data[new_key] = fact[old_key]
                assert new_card_type.is_data_valid(new_fact_data)
                fact.data = new_fact_data
                db.update_fact(fact)
            else:
                new_fact_data = fact.data
            result = self._change_card_type(fact, old_card_type,
                new_card_type, correspondence, new_fact_data, warn)
            if result == -1:
                return
            warn = False
            count += 1
            w.set_progress_value(count)
        if clean_orphaned_static_media_files_needed:
            db.clean_orphaned_static_media_files()        
        db.save()
        w.close_progress()

    def delete_current_card(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        db = self.database()
        review_controller = self.review_controller()
        fact = review_controller.card.fact
        no_of_cards = len(db.cards_from_fact(fact))
        if no_of_cards == 1:
            question = _("Delete this card?")
        elif no_of_cards == 2:
            question = _("Delete this card and 1 sister card?") + " "  +\
                      _("Are you sure you want to do this,") + " " +\
          _("and not just deactivate cards in the 'Activate cards' dialog?")
        else:
            question = _("Delete this card and") + " " + str(no_of_cards - 1) \
                       + " " + _("sister cards?") + " " +\
                       _("Are you sure you want to do this,") + " " +\
          _("and not just deactivate cards in the 'Activate cards' dialog?")
        answer = self.main_widget().show_question(question, _("&Delete"),
                                          _("&Cancel"), "")
        if answer == 1:  # Cancel.
            self.stopwatch().unpause()
            return
        self.delete_facts_and_their_cards([fact])
        review_controller.reload_counters()
        review_controller.show_new_question()
        self.stopwatch().unpause()

    def delete_facts_and_their_cards(self, facts):
        db = self.database()
        clean_orphaned_static_media_files_needed = False  
        for fact in facts:
            if db.fact_contains_static_media_files(fact):
                clean_orphaned_static_media_files_needed = True
            for card in db.cards_from_fact(fact):
                self.scheduler().remove_from_queue_if_present(card)
                db.delete_card(card)
            db.delete_fact(fact)
        if clean_orphaned_static_media_files_needed:
            db.clean_orphaned_static_media_files()
        db.save()

    def clone_card_type(self, card_type, clone_name):
        from mnemosyne.libmnemosyne.utils import mangle    
        clone_id = card_type.id + "::" + clone_name
        if clone_id in [card_t.id for card_t in self.card_types()]:
            self.main_widget().show_error(_("Card type name already exists."))
            return None
        card_type_class = type(mangle(clone_name), (card_type.__class__, ),
            {"name": clone_name, "id": clone_id})
        cloned_card_type = card_type_class(self.component_manager)
        cloned_card_type.fact_views = []
        for fact_view in card_type.fact_views:
            cloned_fact_view = copy.copy(fact_view)
            cloned_fact_view.id = clone_id + "." + fact_view.id.rsplit(".", 1)[1]
            cloned_card_type.fact_views.append(cloned_fact_view)
            self.database().add_fact_view(cloned_fact_view)         
        self.database().add_card_type(cloned_card_type)
        self.config().clone_card_type_properties(card_type, cloned_card_type)
        self.database().save()
        return cloned_card_type
    
    def delete_card_type(self, card_type):
        # TODO: check if card type in use.
        fact_views = card_type.fact_views
        self.database().delete_card_type(card_type)
        # Correct ordering for the sync protocol is deleting the fact views
        # last.
        for fact_view in fact_views:
            self.database().delete_fact_view(fact_view)
        self.database().save()
   
    def show_new_file_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        db = self.database()
        suffix = db.suffix
        filename = self.main_widget().get_filename_to_save(\
            path=self.config().data_dir, filter=_("Mnemosyne databases") + \
            " (*%s)" % suffix, caption=_("New"))
        if not filename:
            self.stopwatch().unpause()
            return
        if not filename.endswith(suffix):
            filename += suffix
        db.backup()
        db.unload()
        # Confirmation on overwrite has happened in the file dialog code.
        if os.path.exists(filename + "_media"):
            import shutil
            shutil.rmtree(filename + "_media")
        db.new(filename)
        db.load(self.config()["path"])
        self.log().loaded_database()
        self.review_controller().reset()
        self.review_controller().update_dialog()
        self.update_title()
        self.stopwatch().unpause()

    def show_open_file_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        db = self.database()
        data_dir = self.config().data_dir
        old_path = expand_path(self.config()["path"], data_dir)
        filename = self.main_widget().get_filename_to_open(path=old_path,
            filter=_("Mnemosyne databases") + " (*%s)" % db.suffix)
        if not filename:
            self.stopwatch().unpause()
            return
        if filename.startswith(os.path.join(data_dir, "backups")):
            result = self.main_widget().show_question(\
                _("Do you want to restore from this backup?"),
                _("Yes"), _("No"), "")
            if result == 0:  # Yes.
                # Note that we don't save the current database first in this
                # case, as the user wants to throw it away. This mainly
                # prohibits dumping to the science log.
                db.restore(filename)
                self.review_controller().reset()
                self.update_title()
            self.stopwatch().unpause()
            return  
        try:
            self.log().saved_database()
            db.backup()
            db.unload()
        except RuntimeError, error:
            self.main_widget().show_error(unicode(error))
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

    def save_file(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        try:
            self.database().save()
            self.log().saved_database()
        except RuntimeError, error:
            self.main_widget().show_error(unicode(error))
        self.stopwatch().unpause()

    def show_save_file_as_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        suffix = self.database().suffix
        old_path = expand_path(self.config()["path"], self.config().data_dir)
        filename = self.main_widget().get_filename_to_save(path=old_path,
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
            self.main_widget().show_error(unicode(error))
            self.stopwatch().unpause()
            return
        self.review_controller().update_dialog()
        self.update_title()
        self.stopwatch().unpause()

    def show_insert_img_dialog(self, filter):

        """Show a file dialog filtered on the supported filetypes, get a
        filename, massage it, and return it to the widget to be inserted.
        There is more media file logic inside the database code too, as the
        user could also just type in the html tags as opposed to passing
        through the file selector here. The reason we don't do all the
        operations in the database code, is that we want to display a nice
        short relative path back in the edit field.

        """

        from mnemosyne.libmnemosyne.utils import copy_file_to_dir
        data_dir, media_dir = self.config().data_dir, self.database().media_dir()
        path = expand_path(self.config()["import_img_dir"], data_dir)
        filter = _("Image files") + " " + filter
        filename = self.main_widget().get_filename_to_open(\
            path, filter, _("Insert image"))
        if not filename:
            return ""
        else:
            self.config()["import_img_dir"] = contract_path(\
                os.path.dirname(filename), data_dir)
            filename = copy_file_to_dir(filename, media_dir)
            return contract_path(filename, media_dir)
        
    def show_insert_sound_dialog(self, filter):
        from mnemosyne.libmnemosyne.utils import copy_file_to_dir
        data_dir, media_dir = self.config().data_dir, self.database().media_dir()
        path = expand_path(self.config()["import_sound_dir"], data_dir)
        filter = _("Sound files") + " " + filter
        filename = self.main_widget().get_filename_to_open(\
            path, filter, _("Insert sound"))
        if not filename:
            return ""
        else:
            self.config()["import_sound_dir"] = contract_path(\
                os.path.dirname(filename), data_dir)
            filename = copy_file_to_dir(filename, media_dir)
            return filename
        
    def show_insert_video_dialog(self, filter):
        from mnemosyne.libmnemosyne.utils import copy_file_to_dir
        data_dir, media_dir = self.config().data_dir, self.database().media_dir()
        path = expand_path(self.config()["import_video_dir"], data_dir)
        filter = _("Video files") + " " + filter
        filename = self.main_widget().get_filename_to_open(\
            path, filter, _("Insert video"))
        if not filename:
            return ""
        else:
            self.config()["import_video_dir"] = contract_path(\
                os.path.dirname(filename), data_dir)
            filename = copy_file_to_dir(filename, media_dir)
            return filename
        
    def show_activate_cards_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("activate_cards_dialog")\
            (self.component_manager).activate()
        review_controller = self.review_controller()
        review_controller.reset_but_try_to_keep_current_card()
        review_controller.update_status_bar_counters()
        self.stopwatch().unpause()
        
    def show_browse_cards_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("browse_cards_dialog")\
            (self.component_manager).activate()
        review_controller = self.review_controller()
        review_controller.reset_but_try_to_keep_current_card()
        review_controller.card = self.database().card(\
            review_controller.card._id, is_id_internal=True)
        review_controller.update_dialog(redraw_all=True)
        self.stopwatch().unpause()
        
    def show_card_appearance_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("card_appearance_dialog")\
            (self.component_manager).activate()
        self.review_controller().update_dialog(redraw_all=True)
        self.stopwatch().unpause()
        
    def show_activate_plugins_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("activate_plugins_dialog")\
            (self.component_manager).activate()
        self.review_controller().update_dialog(redraw_all=True)
        self.stopwatch().unpause()

    def show_manage_card_types_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("manage_card_types_dialog")\
            (self.component_manager).activate()
        self.stopwatch().unpause()
        
    def show_statistics_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("statistics_dialog")\
            (self.component_manager).activate()
        self.stopwatch().unpause()
        
    def show_configuration_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("configuration_dialog")\
            (self.component_manager).activate()
        self.review_controller().reset_but_try_to_keep_current_card()
        self.stopwatch().unpause()
        
    def show_import_file_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        path = expand_path(self.config()["import_dir"], self.config().data_dir)

        # TMP hardcoded single fileformat.
        filename = self.main_widget().get_filename_to_open(path=path,
            filter=_("Mnemosyne 1.x databases") + " (*.mem)")
        if not filename:
            self.stopwatch().unpause()
            return
        self.component_manager.current("file_format").do_import(filename)
        self.database().save()
        self.log().saved_database()
        review_controller = self.review_controller()
        review_controller.reload_counters()
        if review_controller.card is None:
            review_controller.show_new_question()
        else:
            review_controller.update_status_bar_counters()
        self.stopwatch().unpause()

    def show_export_file_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        
        self.stopwatch().unpause()

    def show_sync_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.database().save()        
        self.component_manager.current("sync_dialog")\
            (self.component_manager).activate()
        self.database().save()
        self.log().saved_database()
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().update_dialog(redraw_all=True)
        self.stopwatch().unpause()

    def sync(self, server, port, username, password, ui=None):      
        if ui is None:
            ui = self.main_widget()
        from openSM2sync.client import Client
        client = Client(self.config().machine_id(), self.database(), ui)
        client.program_name = "Mnemosyne"
        import mnemosyne.version  
        client.program_version = mnemosyne.version.version
        client.capabilities = "mnemosyne_dynamic_cards"
        client.check_for_edited_local_media_files = \
            self.config()["check_for_edited_local_media_files"]
        client.interested_in_old_reps = \
            self.config()["interested_in_old_reps"]
        client.store_pregenerated_data = \
            self.database().store_pregenerated_data
        client.do_backup = self.config()["backup_before_sync"]
        client.upload_science_logs = self.config()["upload_science_logs"]
        try:
            client.sync(server, port, username, password)
        finally:
            client.database.release_connection()        

    def show_download_source_dialog(self):

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
        self.flush_sync_server()
        self.main_widget().show_information(\
            _("For instructions on how to download Mnemosyne's source,") + \
            " " + _("go to http://www.mnemosyne-proj.org"))
        self.stopwatch().unpause()        
