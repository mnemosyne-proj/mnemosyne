#
# mnemosyne2_db.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.file_format import FileFormat
from mnemosyne.libmnemosyne.file_formats.mnemosyne2_cards import Mnemosyne2Cards


class Mnemosyne2Db(FileFormat):

    description = _("Mnemosyne 2.x *.db files")
    extension = ".db"
    filename_filter = _("Mnemosyne 2.x database for merging (*.db)")
    import_possible = True
    export_possible = False

    def do_import(self, filename, extra_tag_names=None):
        if filename.endswith("config.db"):
            self.main_widget().show_information(\
                _("The configuration database is not used to store cards."))
            return     
        data_dir = self.config().data_dir
        receiving_database_filename = \
            expand_path(self.config()["last_database"], data_dir)
        # Load database to be merged and export to temporary *.cards file.
        self.database().load(filename)
        cards_format = Mnemosyne2Cards(self.component_manager)
        tmp_cards_filename = os.path.join(data_dir, "TMP.cards")
        cards_format.do_export(tmp_cards_filename, export_learning_data=True)
        # Import the *.cards file into the receiving database.
        self.database().load(receiving_database_filename)
        log_index_before_import = self.database().current_log_index()
        cards_format.do_import(tmp_cards_filename)
        self.database().merge_logs_from_other_database\
            (filename, log_index_before_import)
        os.remove(tmp_cards_filename)
        