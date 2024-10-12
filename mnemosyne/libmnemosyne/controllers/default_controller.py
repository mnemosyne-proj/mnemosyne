#
# default_controller.py <Peter.Bienstman@gmail.com>
#

import os
import sys
import copy
import time

from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.controller import Controller
from mnemosyne.libmnemosyne.utils import remove_empty_dirs_in
from mnemosyne.libmnemosyne.utils import expand_path, contract_path
from mnemosyne.libmnemosyne.card_type_converter import CardTypeConverter

HOUR = 60 * 60 # Seconds in an hour.
DAY = 24 * HOUR # Seconds in a day.


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

    def activate(self):
        self.study_mode = None
        Controller.activate(self)
        self.next_rollover = self.database().start_of_day_n_days_ago(n=-1)

    def heartbeat(self, db_maintenance=True):

        """Making sure, even if the user leaves the program open indefinitely,
        that backups get taken, that the cards scheduled for the day get dumped
        to the log and that the the logs get uploaded, and that the new cards
        for the day are brought into the queue.

        """

        # FIXME: For some reason, datetime.datetime.now() does not respect
        # DST here, although it does work in a standalone Python program...

        if time.time() > self.next_rollover:
            for f in self.component_manager.all("hook", "at_rollover"):
                f.run()
            if self.config().server_only:
                self.database().backup()
                self.log().dump_to_science_log()
            else:
                self.flush_sync_server()
                if not self.database() or not self.database().is_loaded() or \
                    not self.database().is_accessible():
                    # Make sure we don't continue if e.g. the GUI or another
                    # thread holds the database.
                    return
                self.database().backup()
                self.log().saved_database()
                self.log().loaded_database()
                self.log().future_schedule()
                self.log().dump_to_science_log()
                self.log().deactivate()
                self.log().activate()
                self.config().save()
                self.reset_study_mode()
            previous_rollover = self.next_rollover
            next_rollover = self.database().start_of_day_n_days_ago(n=-1)
            # Avoid rare issue with DST.
            if abs(next_rollover - previous_rollover) < HOUR:
                next_rollover += DAY
            self.next_rollover = next_rollover
        if db_maintenance and \
           (time.time() > self.config()["last_db_maintenance"] + 90 * DAY):
            self.component_manager.current("database_maintenance").run()
            self.config()["last_db_maintenance"] = time.time()
            self.config().save()

    def do_db_maintenance(self):
        if time.time() < self.config()["last_db_maintenance"] + 30 * DAY:
            self.main_widget().show_information(\
          _("No need to do database maintenance more than once per month."))
            return
        else:
            self.component_manager.current("database_maintenance").run()
            self.config()["last_db_maintenance"] = time.time()
            self.config().save()

    def update_title(self):
        title = _("Mnemosyne")
        db = self.database()
        database_name = db.display_name()
        if database_name and database_name != db.default_name:
            title += " - " + database_name
        if db.current_criterion() and \
            db.current_criterion().name and \
            db.current_criterion().name != db.default_criterion_name:
            title += " - " + db.current_criterion().name
        self.main_widget().set_window_title(title)

    def set_study_mode(self, study_mode):
        if self.study_mode == study_mode:
            return
        if self.study_mode is not None:
            self.study_mode.deactivate()
        study_mode.activate()
        self.study_mode = study_mode
        self.config()["study_mode"] = study_mode.id

    def reset_study_mode(self):
        self.study_mode.deactivate()
        self.study_mode.activate()

    def show_add_cards_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("add_cards_dialog")\
            (component_manager=self.component_manager).activate()
        # This dialog calls 'create_new_cards' at some point.
        self.database().save()
        review_controller = self.review_controller()
        review_controller.reload_counters()
        if review_controller.card is None:
            review_controller.show_new_question()
        else:
            review_controller.update_status_bar_counters()
        self.stopwatch().unpause()

    def _retain_only_child_tags(self, tag_names):

        """In case e.g. tag_names is ["a", "a::b"], return only ["a::b"]."""

        parent_tag_names = []
        for tag_name in tag_names:
            partial_tag = ""
            for node in tag_name.split("::")[:-1]:
                if partial_tag:
                    partial_tag += "::"
                partial_tag += node
                if partial_tag in tag_names:
                    parent_tag_names.append(partial_tag)
        return sorted(list(set(tag_names) - set(parent_tag_names)))

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
        assert card_type.is_fact_data_valid(fact_data)
        db = self.database()
        tag_names = self._retain_only_child_tags(tag_names)
        tags = db.get_or_create_tags_with_names(tag_names)
        fact = Fact(fact_data)
        if check_for_duplicates:
            duplicates = db.duplicates_for_fact(fact, card_type)
            if len(duplicates) != 0:
                answer = None
                for duplicate in duplicates:
                    # Duplicates only checks equality of unique keys.
                    if duplicate.data == fact_data:
                        answer = self.main_widget().show_question(\
                            _("Identical card is already in database."),
                            _("&Do not add"), _("&Add anyway"), "")
                        break
                if answer is None:
                    question = \
                        _("There is already data present for this card:\n\n")
                    existing_fact_data = {}
                    for fact_key in card_type.fact_keys():
                        existing_fact_data[fact_key] = ""
                    for duplicate in duplicates:
                        if duplicate.data == fact.data:
                            continue
                        for fact_key in fact_data:
                            if fact_key in duplicate.data and \
                                duplicate[fact_key] not in \
                                existing_fact_data[fact_key]:
                                if len(existing_fact_data[fact_key]) != 0:
                                    existing_fact_data[fact_key] += " / "
                                existing_fact_data[fact_key] +=  \
                                    duplicate[fact_key]
                    for fact_key, fact_key_name in \
                        card_type.fact_keys_and_names:
                        question += _(fact_key_name) + ": " + \
                            existing_fact_data[fact_key] + "\n"
                    answer = self.main_widget().show_question(question,
                    _("&Do not add"), _("&Add anyway"), _("&Merge and edit"))
                if answer == 0:  # Do not add.
                    return
                if answer == 2:  # Merge and edit.
                    db.add_fact(fact)
                    for duplicate in duplicates:
                        for card in db.cards_from_fact(duplicate):
                            tags.update(card.tags)
                    cards = card_type.create_sister_cards(fact)
                    for card in cards:
                        card.tags = tags
                        db.add_card(card)
                    if grade >= 2:
                        self.scheduler().set_initial_grade(cards, grade)
                        for card in cards:
                            db.update_card(card, repetition_only=True)
                    merged_fact_data = copy.copy(fact.data)
                    for duplicate in duplicates:
                        for fact_key in fact_data:
                            if fact_key in duplicate.data and \
                                duplicate[fact_key] not in \
                                    merged_fact_data[fact_key]:
                                merged_fact_data[fact_key] += " / " \
                                    + duplicate[fact_key]
                    self.delete_facts_and_their_cards(duplicates)
                    card = db.cards_from_fact(fact)[0]
                    card.fact.data = merged_fact_data
                    card.tags = tags
                    self.component_manager.current("edit_card_dialog")\
                        (card, component_manager=self.component_manager,
                         allow_cancel=False).activate()
                    return db.cards_from_fact(fact)
        # Create cards.
        cards = card_type.create_sister_cards(fact)
        db.add_fact(fact)
        for card in cards:
            card.tags = tags
            db.add_card(card)
        if grade >= 2:
            self.scheduler().set_initial_grade(cards, grade)
            for card in cards:
                db.update_card(card, repetition_only=True)
        if save:
            db.save()
        return cards

    def show_edit_card_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        review_controller = self.review_controller()
        # This dialog calls 'edit_card_and_sisters' at some point.
        state = review_controller.state()
        accepted = self.component_manager.current("edit_card_dialog")\
            (review_controller.card,
             component_manager=self.component_manager).activate()
        if not accepted:
            self.stopwatch().unpause()
            return
        review_controller.reload_counters()
        # Our current card could have disappeared from the database here,
        # e.g. when converting a front-to-back card to a cloze card, which
        # deletes the old cards and their learning history.
        if review_controller.card is None:
            review_controller.show_new_question()
        else:
            review_controller.set_state(state)
            review_controller.card = self.database().card(\
                review_controller.card._id, is_id_internal=True)
            # Our current card could have picked up a forbidden tag.
            if review_controller.card.active == False:
                review_controller.show_new_question()
            review_controller.update_dialog(redraw_all=True)
        self.stopwatch().unpause()

    def _change_card_type(self, fact, old_card_type, new_card_type,
                          correspondence, new_fact_data, warn=True):

        """This is an internal function, used by 'edit_card_and_sisters' and
        'change_card_type'. It should not be called from the outside by
        itself, otherwise the database will not be saved.

        Returns -2 for error, -1 for cancel and 0 for success.

        """

        if old_card_type == new_card_type:
            return 0
        db = self.database()
        cards_from_fact = db.cards_from_fact(fact)
        assert cards_from_fact[0].card_type == old_card_type
        if not new_card_type.is_fact_data_valid(new_fact_data):
            self.main_widget().show_error(\
        _("Card data not correctly formatted for conversion.\n\nSkipping ") +\
                "|".join(list(fact.data.values())) + ".\n")
            return -2
        # For conversion, we need to look at the top ancestor.
        ancestor_id_old = old_card_type.id.split("::", maxsplit=1)[0]
        ancestor_id_new = new_card_type.id.split("::", maxsplit=1)[0]
        converter = None
        if ancestor_id_old != ancestor_id_new:
            converter = self.component_manager.current\
              ("card_type_converter", CardTypeConverter.card_type_converter_key\
               (self.card_type_with_id(ancestor_id_old),
                self.card_type_with_id(ancestor_id_new)))
        if not converter:
            if ancestor_id_old == ancestor_id_new:
                edited_cards = cards_from_fact
                new_fact_view_for = {}
                for index, old_fact_view in enumerate(old_card_type.fact_views):
                    new_fact_view_for[old_fact_view] = \
                        new_card_type.fact_views[index]
                for card in edited_cards:
                    card.card_type = new_card_type
                    card.fact_view = new_fact_view_for[card.fact_view]
                    db.update_card(card)
                return 0
            else:
                if warn:
                    has_history = False
                    for card in cards_from_fact:
                        if card.acq_reps > 0:
                            has_history = True
                            break
                    if has_history:
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
                # Don't use progress bars in the next call, as nested
                # progress bars (e.g. from change_card_type) are not
                # supported.
                self.delete_facts_and_their_cards([fact], progress_bar=False)
                new_cards = self.create_new_cards(new_fact_data,
                    new_card_type, grade=-1, tag_names=tag_names)
                # User cancelled in create_new_cards.
                if new_cards is None:
                    return -1
                # We've created a new fact here. Make sure the calling function
                # has the information to reload the fact.
                fact._id = new_cards[0].fact._id
                fact.id = new_cards[0].fact.id
                if is_currently_asked:
                    self.review_controller().card = new_cards[0]
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
                self.reset_study_mode()
            return 0

    def edit_card_and_sisters(self, card, new_fact_data, new_card_type,
            new_tag_names, correspondence):
        db = self.database()
        sch = self.scheduler()
        assert new_card_type.is_fact_data_valid(new_fact_data)
        # Determine the current tags in use for the sister cards. This
        # needs to be done before e.g. editing a cloze card creates new
        # cards which are as yet untagged.
        fact = db.fact(card.fact._id, is_id_internal=True)
        current_sister_cards = self.database().cards_from_fact(fact)
        current_tag_strings = set([sister_card.tag_string() \
            for sister_card in current_sister_cards])
        # Change the card type if needed. This does not take into account
        # changes to fact yet, which will come just afterwards.
        result = self._change_card_type(card.fact, card.card_type,
            new_card_type, correspondence, new_fact_data)
        if result in [-2, -1]:  # Error, aborted.
            return result
        # When there was no card type conversion possible, the cards had to
        # be recreated from the new fact data. In that case, it is needed to
        # reload the fact from the database.
        fact = db.fact(card.fact._id, is_id_internal=True)
        # Update fact and create, delete and update cards.
        new_cards, edited_cards, deleted_cards = \
            new_card_type.edit_fact(fact, new_fact_data)
        fact.data = new_fact_data
        db.update_fact(fact)
        for deleted_card in deleted_cards:
            if self.review_controller().card == deleted_card:
                self.review_controller().card = None
            sch.remove_from_queue_if_present(deleted_card)
            db.delete_card(deleted_card)
        for new_card in new_cards:
            db.add_card(new_card)
        for edited_card in edited_cards:
            db.update_card(edited_card)
        if new_cards and self.review_controller().learning_ahead == True:
            self.reset_study_mode()
        # Apply new tags and modification time to cards and save them back to
        # the database. Note that this makes sure there is an EDITED_CARD log
        # entry for each sister card, which is needed when syncing with a
        # partner that does not have the concept of facts.
        tag_for_current_card_only = False
        if len(current_tag_strings) > 1:
            tag_for_current_card_only = bool(self.main_widget().show_question(
_("This card has different tags than its sister cards. Update tags for current card only or for all sister cards?"),
            _("Current card only"), _("All sister cards"), "") == 0)
        old_tags = set()
        new_tag_names = self._retain_only_child_tags(new_tag_names)
        tags = db.get_or_create_tags_with_names(new_tag_names)
        modification_time = int(time.time())
        for sister_card in self.database().cards_from_fact(fact):
            sister_card.modification_time = modification_time
            if sister_card == card or not tag_for_current_card_only:
                old_tags = old_tags.union(sister_card.tags)
                sister_card.tags = tags
            db.update_card(sister_card)
        for tag in old_tags:
            db.delete_tag_if_unused(tag)
        db.save()
        return 0

    def change_card_type(self, facts, old_card_type, new_card_type,
                         correspondence):

        """Note: all facts should have the same card type."""

        db = self.database()
        warn = True
        w = self.main_widget()
        w.set_progress_text(_("Converting cards..."))
        w.set_progress_range(len(facts))
        w.set_progress_update_interval(len(facts)/50)
        for fact in facts:
            if correspondence:
                new_fact_data = {}
                for old_fact_key, new_fact_key in correspondence.items():
                    if old_fact_key in fact:
                        new_fact_data[new_fact_key] = fact[old_fact_key]
                if new_card_type.is_fact_data_valid(new_fact_data):
                    fact.data = new_fact_data
            else:
                new_fact_data = copy.copy(fact.data)
            result = self._change_card_type(fact, old_card_type,
                    new_card_type, correspondence, new_fact_data, warn)
            if result == -1:  # Cancel.
                w.close_progress()
                return
            if correspondence and result != -2:  # Error.
                db.update_fact(fact)
            warn = False
            w.increase_progress(1)
        db.save()
        w.close_progress()

    def star_current_card(self):
        review_controller = self.review_controller()
        if not review_controller.card:
            return
        self.stopwatch().pause()
        self.flush_sync_server()
        if self.config()["star_help_shown"] == False:
            self.main_widget().show_information(\
_("This will add a tag 'Starred' to the current card, so that you can find it back easily, e.g. to edit it on a desktop."))
            self.config()["star_help_shown"] = True
        db = self.database()
        tag = db.get_or_create_tag_with_name(_("Starred"))
        _sister_card_ids = [card._id for card in \
            self.database().cards_from_fact(review_controller.card.fact)]
        db.add_tag_to_cards_with_internal_ids(tag, _sister_card_ids)
        review_controller.card = \
            db.card(review_controller.card._id, is_id_internal=True)
        review_controller.update_dialog(redraw_all=True)
        self.stopwatch().unpause()

    def delete_current_card(self):
        review_controller = self.review_controller()
        if not review_controller.card:
            return
        self.stopwatch().pause()
        self.flush_sync_server()
        db = self.database()
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
        answer = self.main_widget().show_question(question, _("&Cancel"),
                                          _("&Delete"), "")
        if answer == 0:  # Cancel.
            self.stopwatch().unpause()
            return
        self.delete_facts_and_their_cards([fact])
        review_controller.reload_counters()
        review_controller.show_new_question()
        self.stopwatch().unpause()

    def delete_facts_and_their_cards(self, facts, progress_bar=True):
        assert len(facts) == len([fact.id for fact in facts])
        db = self.database()
        w = self.main_widget()
        if progress_bar:
            w.set_progress_text(_("Deleting cards..."))
            w.set_progress_range(len(facts))
            w.set_progress_update_interval(50)
        for fact in facts:
            for card in db.cards_from_fact(fact):
                self.scheduler().remove_from_queue_if_present(card)
                db.delete_card(card, check_for_unused_tags=False)
            db.delete_fact(fact)
            if progress_bar:
                w.increase_progress(1)
        tags = db.tags()
        if progress_bar:
            w.set_progress_text(_("Checking for unused tags..."))
            w.set_progress_range(len(tags))
        tags = db.tags()
        for tag in tags:
            db.delete_tag_if_unused(tag)
            if progress_bar:
                w.increase_progress(1)
        db.save()
        if progress_bar:
            w.close_progress()

    def reset_current_card(self):
        review_controller = self.review_controller()
        if not review_controller.card:
            return
        self.stopwatch().pause()
        self.flush_sync_server()
        db = self.database()
        fact = review_controller.card.fact
        no_of_cards = len(db.cards_from_fact(fact))
        if no_of_cards == 1:
            question = _("Reset learning history of this card?")
        elif no_of_cards == 2:
            question = _("Reset learning history of this card and 1 sister card?")
        else:
            question = _("Reset learning history of this card and") + \
                " " + str(no_of_cards - 1) + " " + _("sister cards?")
        answer = self.main_widget().show_question(question, _("&Cancel"),
                                          _("&Reset"), "")
        if answer == 0:  # Cancel.
            self.stopwatch().unpause()
            return
        self.reset_facts_and_their_cards([fact])
        review_controller.reload_counters()
        review_controller.show_new_question()
        self.stopwatch().unpause()

    def reset_facts_and_their_cards(self, facts, progress_bar=True):
        assert len(facts) == len([fact.id for fact in facts])
        db = self.database()
        w = self.main_widget()
        if progress_bar:
            w.set_progress_text(_("Resetting cards..."))
            w.set_progress_range(len(facts))
            w.set_progress_update_interval(50)
        for fact in facts:
            for card in db.cards_from_fact(fact):
                card.grade = -2 # Marker for reset event.
                self.log().repetition(card, scheduled_interval=0,
                actual_interval=0, thinking_time=0)
                card.reset_learning_data()
                self.log().repetition(card, scheduled_interval=0,
                actual_interval=0, thinking_time=0)
                db.update_card(card)
            if progress_bar:
                w.increase_progress(1)
        db.save()
        if progress_bar:
            w.close_progress()

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
        if not self.database().is_user_card_type(card_type) or \
            self.database().is_in_use(card_type):
            self.main_widget().show_error(\
    _("Card type %s is in use or is a system card type, cannot delete it.") \
    % (card_type.name, ))
            return
        if self.database().has_clones(card_type):
            self.main_widget().show_error(\
    _("Card type %s has clones, cannot delete it.") \
    % (card_type.name, ))
            return
        fact_views = card_type.fact_views
        self.config().delete_card_type_properties(card_type)
        self.database().delete_card_type(card_type)
        # Correct ordering for the sync protocol is deleting the fact views
        # last.
        for fact_view in fact_views:
            self.database().delete_fact_view(fact_view)
        self.database().save()

    def rename_card_type(self, card_type, new_name):
        if not self.database().is_user_card_type(card_type):
            self.main_widget().show_error(\
            _("Cannot rename a system card type."))
            return
        for card_type_ in self.card_types():
            if card_type_.name == new_name:
                self.main_widget().show_error(\
                _("This card type name is already in use."))
                return
        card_type.name = new_name
        self.database().update_card_type(card_type)
        self.database().save()

    single_database_help = \
_("It is recommended to put all your cards in a single database. Using tags to determine which cards to study is much more convenient than having to load and unload several databases.")

    def show_new_file_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        if self.config()["single_database_help_shown"] == False:
            self.main_widget().show_information(self.single_database_help)
            self.config()["single_database_help_shown"] = True
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
        self.main_widget().set_progress_text(_("Creating new database..."))
        db.backup()
        db.unload()
        # Confirmation on overwrite has happened in the file dialog code.
        if os.path.exists(filename + "_media"):
            import shutil
            shutil.rmtree(filename + "_media")
        db.new(filename)
        self.main_widget().close_progress()
        db.load(self.config()["last_database"])
        self.log().loaded_database()
        self.reset_study_mode()
        self.review_controller().update_dialog()
        self.update_title()
        self.stopwatch().unpause()

    def show_open_file_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        db = self.database()
        data_dir = self.config().data_dir
        old_path = expand_path(self.config()["last_database"], data_dir)
        filename = self.main_widget().get_filename_to_open(path=old_path,
            filter=_("Mnemosyne databases") + " (*%s)" % db.suffix)
        if not filename:
            self.stopwatch().unpause()
            return
        if filename.endswith(".cards"):
            self.stopwatch().unpause()
            self.main_widget().show_information(\
_("'*.cards' files are not separate databases, but need to be imported in your current database through 'File - Import'."))
            return
        if filename.endswith("config.db"):
            self.stopwatch().unpause()
            self.main_widget().show_information(\
                _("The configuration database is not used to store cards."))
            return
        if os.path.normpath(filename).startswith(\
            os.path.normpath(os.path.join(data_dir, "backups"))):
            result = self.main_widget().show_question(\
                _("Do you want to replace your current database with one restored from this backup?\nNote that this will result in conflicts during the next sync, which need to be resolved by a full sync."),
                _("Yes"), _("No"), "")
            if result == 0:  # Yes.
                # Note that we don't save the current database first in this
                # case, as the user wants to throw it away. This mainly
                # prohibits dumping to the science log.
                db.restore(filename)
                self.reset_study_mode()
                self.update_title()
            self.stopwatch().unpause()
            return
        if self.database().is_loaded():
            try:
                self.log().saved_database()
                db.backup()
                db.unload()
            except RuntimeError as error:
                self.main_widget().show_error(str(error))
                self.stopwatch().unpause()
                return
        try:
            db.load(filename)
            self.log().loaded_database()
            self.log().future_schedule()
        except Exception as error:
            self.main_widget().show_error(str(error))
            db.abandon()
            db.load(old_path)
            self.stopwatch().unpause()
            return
        self.reset_study_mode()
        self.update_title()
        self.stopwatch().unpause()

    def save_file(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        if self.config()["save_database_help_shown"] == False:
            self.main_widget().show_information(\
_("Your database will be autosaved before exiting. Also, it is saved every couple of repetitions, as set in the configuration options."))
            self.config()["save_database_help_shown"] = True
        try:
            self.database().save()
            self.log().saved_database()
            self.main_widget().show_information(_("Database saved."))
        except RuntimeError as error:
            self.main_widget().show_error(str(error))
        self.stopwatch().unpause()

    def show_save_file_as_dialog(self):
        self.stopwatch().pause()
        if self.config()["single_database_help_shown"] == False:
            self.main_widget().show_information(_(self.single_database_help))
            self.config()["single_database_help_shown"] = True
        self.flush_sync_server()
        suffix = self.database().suffix
        old_path = expand_path(self.config()["last_database"],
                               self.config().data_dir)
        old_media_dir = self.database().media_dir()
        filename = self.main_widget().get_filename_to_save(path=old_path,
            filter=_("Mnemosyne databases") + " (*%s)" % suffix)
        if not filename:
            self.stopwatch().unpause()
            return
        if filename.endswith("config.db"):
            self.main_widget().show_information(\
_("The configuration database cannot be used to store cards."))
            self.stopwatch().unpause()
            return
        if not filename.endswith(suffix):
            filename += suffix
        try:
            self.database().save(filename)
            new_media_dir = self.database().media_dir()
            if old_media_dir == new_media_dir:
                return
            import shutil
            if os.path.exists(new_media_dir):
                shutil.rmtree(new_media_dir)
            shutil.copytree(old_media_dir, new_media_dir)
            self.log().saved_database()
        except RuntimeError as error:
            self.main_widget().show_error(str(error))
            self.stopwatch().unpause()
            return
        self.review_controller().update_dialog()
        self.update_title()
        self.stopwatch().unpause()

    def show_compact_database_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("compact_database_dialog")\
            (component_manager=self.component_manager).activate()
        self.review_controller().reset_but_try_to_keep_current_card()
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
        data_dir, media_dir = \
            self.config().data_dir, self.database().media_dir()
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

    def show_insert_flash_dialog(self, filter):
        from mnemosyne.libmnemosyne.utils import copy_file_to_dir
        data_dir, media_dir = self.config().data_dir, self.database().media_dir()
        path = expand_path(self.config()["import_flash_dir"], data_dir)
        filter = _("Flash files") + " " + filter
        filename = self.main_widget().get_filename_to_open(\
            path, filter, _("Insert Flash"))
        if not filename:
            return ""
        else:
            self.config()["import_flash_dir"] = contract_path(\
                os.path.dirname(filename), data_dir)
            filename = copy_file_to_dir(filename, media_dir)
            return filename

    def show_browse_cards_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        review_controller = self.review_controller()
        self.component_manager.current("browse_cards_dialog")\
            (component_manager=self.component_manager).activate()
        review_controller.reset_but_try_to_keep_current_card()
        review_controller.update_dialog(redraw_all=True)
        self.stopwatch().unpause()

    def show_activate_cards_dialog(self):
        self.show_activate_cards_dialog_pre()
        self.show_activate_cards_dialog_post()

    def show_activate_cards_dialog_pre(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("activate_cards_dialog")\
            (component_manager=self.component_manager).activate()

    def show_activate_cards_dialog_post(self):
        review_controller = self.review_controller()
        review_controller.reset_but_try_to_keep_current_card()
        review_controller.reload_counters()
        review_controller.update_status_bar_counters()
        self.update_title()
        self.stopwatch().unpause()

    def find_duplicates(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        if self.config()["find_duplicates_help_shown"] == False:
            self.main_widget().show_information(\
_("This will tag all the cards in a given card type which have the same question. That way you can reformulate them to make the answer unambiguous. Note that this will not tag duplicates in different card types, e.g. card types for 'French' and 'Spanish'."))
            self.config()["find_duplicates_help_shown"] = True
        self.database().tag_all_duplicates()
        review_controller = self.review_controller()
        review_controller.reset_but_try_to_keep_current_card()
        review_controller.reload_counters()
        review_controller.update_status_bar_counters()
        self.stopwatch().unpause()

    def show_manage_plugins_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("manage_plugins_dialog")\
            (component_manager=self.component_manager).activate()
        self.review_controller().update_dialog(redraw_all=True)
        self.stopwatch().unpause()

    def install_plugin(self):
        filename = self.main_widget().get_filename_to_open(\
            self.config()["import_plugin_dir"],
            _("Plugins") + " " + "(*.plugin)", _("Install plugin"))
        if not filename:
            return ""
        self.config()["import_plugin_dir"] = os.path.dirname(filename)
        plugin_dir = os.path.join(self.config().data_dir, "plugins")
        import zipfile
        plugin_file = zipfile.ZipFile(filename, "r")
        # Filter out safety risks.
        filenames = [filename for filename in plugin_file.namelist() \
            if not filename.startswith("/") and not ".." in filename]
        # Find actual plugin.
        plugin_file.extractall(plugin_dir, filenames)
        import re
        re_plugin = re.compile(r""".*class (.+?)\(Plugin""",
            re.DOTALL | re.IGNORECASE)
        plugin_filename, plugin_class_name = None, None
        for filename in filenames:
            if filename.endswith(".py"):
                text = open(os.path.join(plugin_dir, filename), "r").read()
                match = re_plugin.match(text)
                if match is not None:
                    plugin_filename = filename
                    plugin_class_name = match.group(1)
                    break
        if plugin_class_name is None:
            self.main_widget().show_error(_("No plugin found!"))
            return
        # Write manifest to allow uninstalling.
        manifest = open(os.path.join(plugin_dir,
            plugin_class_name + ".manifest"), "w")
        for filename in filenames:
            if not os.path.isdir(os.path.join(plugin_dir, filename)):
                print(filename, file=manifest)
        # Make sure we don't register a plugin twice.
        for plugin in self.plugins():
            if plugin.__class__.__name__ == plugin_class_name:
                return
        # Register plugin.
        try:
            module_name = plugin_filename[:-3]
            # Schedule module for reloading. Needed to catch the case of
            # deleting a plugin and then immediately reinstalling it.
            if module_name in sys.modules:
                del sys.modules[module_name]
            __import__(module_name)
        except Exception as e:
            print(e)
            from mnemosyne.libmnemosyne.utils import traceback_string
            msg = _("Error when running plugin:") \
                + "\n" + traceback_string()
            self.main_widget().show_error(msg)
            for plugin in self.plugins():
                if plugin.__class__.__name__ == plugin_class_name:
                    self.component_manager.unregister(plugin)

    def delete_plugin(self, plugin):
        plugin.deactivate()
        self.component_manager.unregister(plugin)
        plugin_dir = os.path.join(self.config().data_dir, "plugins")
        manifest_filename = os.path.join(plugin_dir,
            plugin.__class__.__name__ + ".manifest")
        manifest = open(manifest_filename, "r")
        plugin_dir = os.path.join(self.config().data_dir, "plugins")
        for filename in manifest:
            filename = os.path.join(plugin_dir, filename.rstrip())
            os.remove(filename)
            if filename.endswith(".py") and os.path.exists(filename + "c"):
                os.remove(filename + "c")
        manifest.close()
        del plugin
        os.remove(manifest_filename)
        remove_empty_dirs_in(plugin_dir)

    def show_manage_card_types_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("manage_card_types_dialog")\
            (component_manager=self.component_manager).activate()
        self.stopwatch().unpause()

    def show_statistics_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("statistics_dialog")\
            (component_manager=self.component_manager).activate()
        self.stopwatch().unpause()

    def show_configuration_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("configuration_dialog")\
            (component_manager=self.component_manager).activate()
        self.config().save()
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().update_dialog(redraw_all=True)
        self.stopwatch().unpause()

    def show_import_file_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("import_dialog")\
            (component_manager=self.component_manager).activate()
        self.database().save()
        self.log().saved_database()
        review_controller = self.review_controller()
        review_controller.reload_counters()
        # Importing can edit the current card.
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().update_dialog(redraw_all=True)
        self.stopwatch().unpause()

    def show_export_file_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("export_dialog")\
            (component_manager=self.component_manager).activate()
        self.stopwatch().unpause()

    def show_sync_dialog(self):
        self.show_sync_dialog_pre()
        self.show_sync_dialog_post()

    def show_sync_dialog_pre(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.database().save()
        self.component_manager.current("sync_dialog")\
        (component_manager=self.component_manager).activate()

    def show_sync_dialog_post(self):
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

    def show_getting_started_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("getting_started_dialog")\
            (component_manager=self.component_manager).activate()
        self.stopwatch().unpause()

    def show_tip_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("tip_dialog")\
            (component_manager=self.component_manager).activate()
        self.stopwatch().unpause()

    def show_about_dialog(self):
        self.stopwatch().pause()
        self.flush_sync_server()
        self.component_manager.current("about_dialog")\
            (component_manager=self.component_manager).activate()
        self.stopwatch().unpause()
