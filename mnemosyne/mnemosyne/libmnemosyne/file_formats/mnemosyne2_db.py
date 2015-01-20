#
# mnemosyne2_db.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.file_format import FileFormat
from mnemosyne.libmnemosyne.file_formats.mnemosyne2_cards import Mnemosyne2Cards


class Mnemosyne2Db(FileFormat):

    description = _("Mnemosyne 2.x *.db files")
    extension = ".db"
    filename_filter = _("Mnemosyne 2.x database for merging (*.db)")
    import_possible = True
    export_possible = False

    def do_import(self, filename, extra_tag_names=None):
        db = self.database()
        if filename.endswith("config.db"):
            self.main_widget().show_error(\
                _("The configuration database is not used to store cards."))
            return     
        data_dir = self.config().data_dir
        receiving_database_filename = \
            expand_path(self.config()["last_database"], data_dir)
        # Load database to be merged and export to temporary *.cards file.
        db.load(filename)
        cards_format = Mnemosyne2Cards(self.component_manager)
        tmp_cards_filename = os.path.join(data_dir, "TMP.cards")
        cards_format.do_export(tmp_cards_filename, used_for_merging_dbs=True)
        old_deactivated_card_type_fact_view_ids = \
            db.current_criterion().deactivated_card_type_fact_view_ids
        # Import the *.cards file into the receiving database.
        db.load(receiving_database_filename)
        log_index_before_import = db.current_log_index()
        cards_format.do_import(\
            tmp_cards_filename, extra_tag_names, show_metadata=False)
        db.merge_logs_from_other_database(filename, log_index_before_import)
        os.remove(tmp_cards_filename)
        db.current_criterion().deactivated_card_type_fact_view_ids.update(\
            old_deactivated_card_type_fact_view_ids)
        db.set_current_criterion(db.current_criterion())      
        