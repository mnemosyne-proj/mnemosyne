#
# database_maintenance.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.database import DatabaseMaintenance


class AndroidDatabaseMaintenance(DatabaseMaintenance):

    def run(self):
        # Use shown_question here, since this is implemented to block.
        answer = self.main_widget().show_question(\
_("About to archive old logs to improve running speed. Depending on the size of your database and the speed of your device, this can take 10 minutes or more. Please leave Mnemosyne running in the foreground."),
        _("OK, proceed"), "", "")
        if answer == 0:
            DatabaseMaintenance.run(self)

