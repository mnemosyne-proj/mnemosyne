#
# compact_database_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_compact_database_dlg import \
    Ui_CompactDatabaseDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import \
    CompactDatabaseDialog


class CompactThread(QtCore.QThread):

    """We do this in a separate thread so that the GUI still stays responsive.

    """

    compact_finished_signal = QtCore.pyqtSignal()

    def __init__(self, mnemosyne, compact_database, delete_unused_media_files):
        QtCore.QThread.__init__(self)
        self.mnemosyne = mnemosyne
        self.compact_database = compact_database
        self.delete_unused_media_files = delete_unused_media_files

    def run(self):
        try:
            if self.delete_unused_media_files:
                self.mnemosyne.database().delete_unused_media_files()
            if self.compact_database:
                self.mnemosyne.database().compact()
        finally:
            self.mnemosyne.database().release_connection()
        self.compact_finished_signal.emit()


class CompactDatabaseDlg(QtGui.QDialog, Ui_CompactDatabaseDlg,
    CompactDatabaseDialog):

    def __init__(self, component_manager):
        CompactDatabaseDialog.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)

    def activate(self):
        self.exec_()

    def accept(self):
        compact_database = \
            (self.compact_database.checkState() == QtCore.Qt.Checked)
        delete_unused_media_files = \
            (self.delete_unused_media_files.checkState() == QtCore.Qt.Checked)
        if not (compact_database or delete_unused_media_files):
            QtGui.QDialog.accept(self)
        self.main_widget().set_progress_text(_("Compacting database..."))
        self.database().release_connection()
        self.thread = CompactThread(self,
            compact_database, delete_unused_media_files)
        self.thread.compact_finished_signal.connect(self.finish_compact)
        self.thread.start()

    def finish_compact(self):
        self.main_widget().close_progress()
        QtGui.QDialog.accept(self)