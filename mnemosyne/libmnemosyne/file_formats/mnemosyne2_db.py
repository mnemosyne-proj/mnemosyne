#
# mnemosyne2_db.py <Peter.Bienstman@gmail.com>
#

import os

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.file_format import FileFormat
from mnemosyne.libmnemosyne.file_formats.mnemosyne2_cards import Mnemosyne2Cards


class Mnemosyne2Db(FileFormat):

    description = _("Mnemosyne 2.x *.db files")
    extension = ".db"
    filename_filter = _("Mnemosyne 2.x database for merging (*.db)")
    import_possible = True
    export_possible = False

    def do_import(self, filename, extra_tag_names=""):
        db = self.database()
        if filename.endswith("config.db"):
            self.main_widget().show_error(\
                _("The configuration database is not used to store cards."))
            return
        data_dir = self.config().data_dir
        receiving_database_filename = \
            expand_path(self.config()["last_database"], data_dir)
        db.dump_to_science_log()
        # Heuristic to check if we haven't imported this database before.
        current_tag_ids = set([tag.id for tag in db.tags()])
        self.log().active = False
        db.load(filename)
        self.log().active = True
        tag_ids_to_import = set([tag.id for tag in db.tags()])
        if len(tag_ids_to_import.intersection(current_tag_ids)) >= 2:
            answer = self.main_widget().show_question(\
_("It looks like you've imported this database before. Importing it twice will generate duplicate log entries, which will skew your statistics. Do you want to continue?"),
_("Abort"), _("Continue"), "")
            if answer == 0:
                db.load(receiving_database_filename)
                self.log().active = True
                return
        # Export to temporary *.cards file.
        cards_format = Mnemosyne2Cards(self.component_manager)
        tmp_cards_filename = os.path.join(data_dir, "TMP.cards")
        cards_format.do_export(tmp_cards_filename, used_for_merging_dbs=True)
        old_deactivated_card_type_fact_view_ids = \
            db.current_criterion().deactivated_card_type_fact_view_ids
        user_card_types = [card_type for card_type in db.card_types_in_use() \
            if db.is_user_card_type(card_type)]
        # Get config info to be merged.
        old_config_dir = self.config().config_dir
        self.config().config_dir = os.path.dirname(filename)
        self.log().active = False
        self.config().load()
        config_to_merge = self.config().copy()
        self.config().config_dir = old_config_dir
        self.config().load()
        self.log().active = True
        # Import the *.cards file into the receiving database.
        db.load(receiving_database_filename)
        log_index_before_import = db.current_log_index()
        db.importing_with_learning_data = True
        cards_format.do_import(\
            tmp_cards_filename, extra_tag_names, show_metadata=False)
        db.importing_with_learning_data = False
        db.merge_logs_from_other_database(filename, log_index_before_import)
        os.remove(tmp_cards_filename)
        db.current_criterion().deactivated_card_type_fact_view_ids.update(\
            old_deactivated_card_type_fact_view_ids)
        db.set_current_criterion(db.current_criterion())
        for property_name in ["background_colour", "font", "font_colour",
            "alignment", "hide_pronunciation_field"]:
            self.log().edited_setting(property_name)
            for card_type in user_card_types:
                if card_type.id in config_to_merge[property_name]:
                    self.config()[property_name][card_type.id] = \
                        config_to_merge[property_name][card_type.id]
        db.skip_science_log()