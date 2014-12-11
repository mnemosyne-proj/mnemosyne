#
# mnemosyne2_db.py <Peter.Bienstman@UGent.be>
#


from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.file_format import FileFormat


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
        old_path = expand_path(self.config()["last_database"], data_dir)
        self.database().load(filename)
        
        # export it to cards file with export_learning_data=true
        # reload original database
        # make note of latest entry in logs
        # import cards file
        # delete all log entries created during import
        # copy all log entries from db to be merged in this db.
        