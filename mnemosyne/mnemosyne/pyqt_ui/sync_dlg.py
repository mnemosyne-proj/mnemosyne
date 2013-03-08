#
# sync_dlg.py <Peter.Bienstman@UGent.be>
#

import sys

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_sync_dlg import Ui_SyncDlg
from mnemosyne.libmnemosyne.utils import traceback_string
from mnemosyne.libmnemosyne.ui_components.dialogs import SyncDialog


# Thread synchronisation machinery to communicate the result of a question
# box to the sync thread.

answer = None
mutex = QtCore.QMutex()
dialog_closed = QtCore.QWaitCondition()


class SyncThread(QtCore.QThread):

    """We do the syncing in a separate thread so that the GUI still stays
    responsive when waiting for the server.

    Note that in Qt, we cannot do GUI updates in the server thread, so we
    use the signal/slot mechanism to notify the main thread to do the
    necessary GUI operations.

    """

    information_signal = QtCore.pyqtSignal(QtCore.QString)
    error_signal = QtCore.pyqtSignal(QtCore.QString)
    question_signal = QtCore.pyqtSignal(QtCore.QString, QtCore.QString,
        QtCore.QString, QtCore.QString)
    set_progress_text_signal = QtCore.pyqtSignal(QtCore.QString)
    set_progress_range_signal = QtCore.pyqtSignal(int)
    set_progress_update_interval_signal = QtCore.pyqtSignal(int)
    increase_progress_signal = QtCore.pyqtSignal(int)
    set_progress_value_signal = QtCore.pyqtSignal(int)
    close_progress_signal = QtCore.pyqtSignal()

    def __init__(self, mnemosyne, server, port, username, password):
        QtCore.QThread.__init__(self)
        self.mnemosyne = mnemosyne
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        # A fast moving progress bar seems to cause crashes on Windows.
        self.show_numeric_progress_bar = (sys.platform != "win32")

    def run(self):
        try:
            self.mnemosyne.controller().sync(self.server, self.port,
                self.username, self.password, ui=self)
        finally:
            self.mnemosyne.database().release_connection()

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
        print 'emitting error'
        self.error_signal.emit(error)
        if not answer:
            print 'waiting for anser'
            dialog_closed.wait(mutex)
        print 'done'
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
        if self.show_numeric_progress_bar:
            self.set_progress_range_signal.emit(maximum)

    def set_progress_update_interval(self, value):
        if self.show_numeric_progress_bar:
            self.set_progress_update_interval_signal.emit(value)

    def increase_progress(self, value):
        if self.show_numeric_progress_bar:
            self.increase_progress_signal.emit(value)

    def set_progress_value(self, value):
        if self.show_numeric_progress_bar:
            self.set_progress_value_signal.emit(value)

    def close_progress(self):
        self.close_progress_signal.emit()


class SyncDlg(QtGui.QDialog, Ui_SyncDlg, SyncDialog):

    def __init__(self, component_manager):
        SyncDialog.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        if not self.config()["sync_help_shown"]:
            self.main_widget().show_information(\
               _("Here, you can sync this machine with a remote server. Of course, that remote computer needs to have a server running, which can be started from the configuration screen on that remote machine.\n\nHowever, if you want to sync a mobile device with this machine here, you shouldn't use the menu option you just selected. In that case, this computer needs to be the server. So, first enable a sync server here, and then start the sync from the mobile device."))
            self.config()["sync_help_shown"] = True
        self.server.setText(self.config()["server_for_sync_as_client"])
        self.port.setValue(self.config()["port_for_sync_as_client"])
        self.username.setText(self.config()["username_for_sync_as_client"])
        self.password.setText(self.config()["password_for_sync_as_client"])
        self.check_for_edited_local_media_files.setChecked(\
            self.config()["check_for_edited_local_media_files"])
        if self.config()["server_for_sync_as_client"]:
            self.ok_button.setFocus()
        self.can_reject = True

    def activate(self):
        self.exec_()

    def accept(self):
        # Store input for later use.
        server = unicode(self.server.text())
        port = self.port.value()
        username = unicode(self.username.text())
        password = unicode(self.password.text())
        self.config()["server_for_sync_as_client"] = server
        self.config()["port_for_sync_as_client"] = port
        self.config()["username_for_sync_as_client"] = username
        self.config()["password_for_sync_as_client"] = password
        self.config()["check_for_edited_local_media_files"] = \
            self.check_for_edited_local_media_files.isChecked()
        # Prevent user from interrupting a sync.
        self.can_reject = False
        self.ok_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        # Do the actual sync in a separate thread.
        self.database().release_connection()
        self.thread = SyncThread(self, server, port, username, password)
        self.thread.information_signal.connect(\
            self.threaded_show_information)
        self.thread.error_signal.connect(\
            self.threaded_show_error)
        self.thread.question_signal.connect(\
            self.threaded_show_question)
        self.thread.set_progress_text_signal.connect(\
            self.main_widget().set_progress_text)
        self.thread.set_progress_range_signal.connect(\
            self.main_widget().set_progress_range)
        self.thread.set_progress_update_interval_signal.connect(\
            self.main_widget().set_progress_update_interval)
        self.thread.increase_progress_signal.connect(\
            self.main_widget().increase_progress)
        self.thread.set_progress_value_signal.connect(\
            self.main_widget().set_progress_value)
        self.thread.close_progress_signal.connect(\
            self.main_widget().close_progress)
        self.thread.finished.connect(self.finish_sync)
        self.thread.start()

    def reject(self):
        if self.can_reject:
            QtGui.QDialog.reject(self)

    def finish_sync(self):
        QtGui.QDialog.accept(self)

    def threaded_show_information(self, message):
        global answer
        mutex.lock()
        self.main_widget().show_information(message)
        answer = True
        dialog_closed.wakeAll()
        mutex.unlock()

    def threaded_show_error(self, error):
        print 'threaded show error'
        global answer
        mutex.lock()
        self.main_widget().show_error(error)
        answer = True
        dialog_closed.wakeAll()
        mutex.unlock()

    def threaded_show_question(self, question, option0, option1, option2):
        global answer
        mutex.lock()
        answer = self.main_widget().show_question(question, option0,
            option1, option2)
        dialog_closed.wakeAll()
        mutex.unlock()
