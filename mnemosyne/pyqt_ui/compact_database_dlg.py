#
# compact_database_dlg.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.qt_worker_thread import \
    QtWorkerThread, QtGuiThread
from mnemosyne.pyqt_ui.ui_compact_database_dlg import \
    Ui_CompactDatabaseDlg
from mnemosyne.pyqt_ui.delete_unused_media_files_dlg import \
    DeleteUnusedMediaFilesDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import \
    CompactDatabaseDialog


class CompactThread(QtWorkerThread):

    def __init__(self, defragment_database, archive_old_logs, **kwds):
        super().__init__(**kwds)
        self.defragment_database = defragment_database
        self.archive_old_logs = archive_old_logs

    def do_work(self):
        if self.archive_old_logs:
            self.mnemosyne.database().archive_old_logs()
        if self.defragment_database:
            self.mnemosyne.database().defragment()


class CompactDatabaseDlg(QtWidgets.QDialog, QtGuiThread, CompactDatabaseDialog,
                         Ui_CompactDatabaseDlg):

    def __init__(self, started_automatically=False, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.started_automatically = started_automatically

    def activate(self):
        CompactDatabaseDialog.activate(self)
        self.exec()

    def accept(self):
        defragment_database = \
            (self.defragment_database.checkState() == QtCore.Qt.CheckState.Checked)
        delete_unused_media_files = \
           (self.delete_unused_media_files.checkState() == QtCore.Qt.CheckState.Checked)
        archive_old_logs = \
            (self.archive_old_logs.checkState() == QtCore.Qt.CheckState.Checked)
        if not (defragment_database or delete_unused_media_files or \
                archive_old_logs):
            QtWidgets.QDialog.accept(self)
        if delete_unused_media_files:
            unused_media_files = self.database().unused_media_files()
            if len(unused_media_files) != 0:
                DeleteUnusedMediaFilesDlg(\
                    component_manager=self.component_manager,
                    unused_media_files=unused_media_files).activate()
        if defragment_database or archive_old_logs:
            self.compact_in_thread(defragment_database, archive_old_logs)
        else:
            QtWidgets.QDialog.accept(self)

    def compact_in_thread(self, defragment_database, archive_old_logs):
        self.main_widget().set_progress_text(_("Compacting database..."))
        self.worker_thread = CompactThread(\
            defragment_database, archive_old_logs, mnemosyne=self)
        self.run_worker_thread()

    def work_ended(self):
        self.main_widget().close_progress()
        if not self.started_automatically:
            self.main_widget().show_information(_("Done!"))
            QtWidgets.QDialog.accept(self)


class PyQtDatabaseMaintenance(Component):

    component_type = "database_maintenance"

    def run(self):
        CompactDatabaseDlg(started_automatically=True,
                           component_manager=self.component_manager).\
            compact_in_thread(defragment_database=True, archive_old_logs=True)

