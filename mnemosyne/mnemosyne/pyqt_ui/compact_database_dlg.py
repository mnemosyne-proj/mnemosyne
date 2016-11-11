#
# compact_database_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.ui_compact_database_dlg import \
    Ui_CompactDatabaseDlg
from mnemosyne.pyqt_ui.delete_unused_media_files_dlg import \
    DeleteUnusedMediaFilesDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import \
    CompactDatabaseDialog


class CompactThread(QtCore.QThread):

    """We do this in a separate thread so that the GUI still stays responsive.

    """

    information_signal = QtCore.pyqtSignal(str)
    error_signal = QtCore.pyqtSignal(str)
    question_signal = QtCore.pyqtSignal(str, str, str, str)
    set_progress_text_signal = QtCore.pyqtSignal(str)
    set_progress_range_signal = QtCore.pyqtSignal(int)
    set_progress_update_interval_signal = QtCore.pyqtSignal(int)
    increase_progress_signal = QtCore.pyqtSignal(int)
    set_progress_value_signal = QtCore.pyqtSignal(int)
    close_progress_signal = QtCore.pyqtSignal()
    compact_finished_signal = QtCore.pyqtSignal()

    def __init__(self, mnemosyne, defragment_database, archive_old_logs):
        super().__init__()
        self.mnemosyne = mnemosyne
        self.defragment_database = defragment_database
        self.archive_old_logs = archive_old_logs

    def run(self):
        try:
            # Libmnemosyne itself could also generate dialog messages, so
            # we temporarily override the main_widget with the threaded
            # routines in this class.
            self.mnemosyne.component_manager.components\
                [None]["main_widget"].append(self)
            if self.archive_old_logs:
                self.mnemosyne.database().archive_old_logs()            
            if self.defragment_database:
                self.mnemosyne.database().defragment()
        finally:
            self.mnemosyne.database().release_connection()
            self.mnemosyne.component_manager.components\
                [None]["main_widget"].pop()            
        self.compact_finished_signal.emit()
        
    def show_information(self, message):
        global answer
        mutex.lock()
        answer = None
        self.information_signal.emit(message)
        if not answer:
            dialog_closed.wait(mutex)
        mutex.unlock()

    def show_error(self, error):
        global answer
        mutex.lock()
        answer = None
        self.error_signal.emit(error)
        if not answer:
            dialog_closed.wait(mutex)
        mutex.unlock()

    def show_question(self, question, option0, option1, option2):
        global answer
        mutex.lock()
        answer = None
        self.question_signal.emit(question, option0, option1, option2)
        if not answer:
            dialog_closed.wait(mutex)
        mutex.unlock()
        return answer

    def set_progress_text(self, text):
        self.set_progress_text_signal.emit(text)

    def set_progress_range(self, maximum):
        self.set_progress_range_signal.emit(maximum)

    def set_progress_update_interval(self, value):
        self.set_progress_update_interval_signal.emit(value)

    def increase_progress(self, value):
        self.increase_progress_signal.emit(value)

    def set_progress_value(self, value):
        self.set_progress_value_signal.emit(value)

    def close_progress(self):
        self.close_progress_signal.emit()        


class CompactDatabaseDlg(QtWidgets.QDialog, CompactDatabaseDialog, 
                         Ui_CompactDatabaseDlg):

    def __init__(self, started_automatically=False, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        self.started_automatically = started_automatically
        # Since we will overwrite the true main widget in the thread, we need
        # to save it here.
        self.true_main_widget = self.main_widget()

    def activate(self):
        self.exec_()

    def accept(self):
        defragment_database = \
            (self.defragment_database.checkState() == QtCore.Qt.Checked)
        delete_unused_media_files = \
           (self.delete_unused_media_files.checkState() == QtCore.Qt.Checked)
        archive_old_logs = \
            (self.archive_old_logs.checkState() == QtCore.Qt.Checked) 
        if not (defragment_database or delete_unused_media_files or \
                archive_old_logs):
            QtWidgets.QDialog.accept(self)
        if delete_unused_media_files:
            unused_media_files = self.database().unused_media_files()
            if len(unused_media_files) != 0:
                DeleteUnusedMediaFilesDlg(\
                    self.component_manager, unused_media_files).activate()
        if defragment_database or archive_old_logs:
            self.compact_in_thread(defragment_database, archive_old_logs)
        else:
            QtWidgets.QDialog.accept(self)
            
    def compact_in_thread(self, defragment_database, archive_old_logs):
        self.main_widget().set_progress_text(_("Compacting database..."))
        self.database().release_connection()
        self.thread = CompactThread(\
            self, defragment_database, archive_old_logs)
        self.thread.information_signal.connect(\
            self.threaded_show_information)
        self.thread.error_signal.connect(\
            self.threaded_show_error)
        self.thread.question_signal.connect(\
            self.threaded_show_question)
        self.thread.set_progress_text_signal.connect(\
            self.true_main_widget.set_progress_text)
        self.thread.set_progress_range_signal.connect(\
            self.true_main_widget.set_progress_range)
        self.thread.set_progress_update_interval_signal.connect(\
            self.true_main_widget.set_progress_update_interval)
        self.thread.increase_progress_signal.connect(\
            self.true_main_widget.increase_progress)
        self.thread.set_progress_value_signal.connect(\
            self.true_main_widget.set_progress_value)
        self.thread.close_progress_signal.connect(\
            self.true_main_widget.close_progress)            
        self.thread.compact_finished_signal.connect(self.finish_compact)
        self.thread.start()            

    def finish_compact(self):
        self.true_main_widget.close_progress()
        if not self.started_automatically:
            self.true_main_widget.show_information(_("Done!"))
            QtWidgets.QDialog.accept(self)
       
    def threaded_show_information(self, message):
        global answer
        mutex.lock()
        self.true_main_widget.show_information(message)
        answer = True
        dialog_closed.wakeAll()
        mutex.unlock()

    def threaded_show_error(self, error):
        global answer
        mutex.lock()
        self.true_main_widget.show_error(error)
        answer = True
        dialog_closed.wakeAll()
        mutex.unlock()

    def threaded_show_question(self, question, option0, option1, option2):
        global answer
        mutex.lock()
        answer = self.true_main_widget.show_question(question, option0,
            option1, option2)
        dialog_closed.wakeAll()
        mutex.unlock()
    

class PyQtDatabaseMaintenance(Component):
    
    component_type = "database_maintenance" 
    
    def run(self):
        CompactDatabaseDlg(started_automatically=True, 
                           component_manager=self.component_manager).\
            compact_in_thread(defragment_database=True, archive_old_logs=True)
      