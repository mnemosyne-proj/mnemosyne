#
# qt_worker_thread.py <Peter.Bienstman@gmail.com>
#

import sys

from PyQt6 import QtCore

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import traceback_string


answer = None
mutex = QtCore.QMutex()
dialog_closed = QtCore.QWaitCondition()


class QtWorkerThread(QtCore.QThread):

    """Note that in Qt, we cannot do GUI updates in the worker thread, so we
    use the signal/slot mechanism to notify the main thread to do the
    necessary GUI operations.

    """

    work_started_signal = QtCore.pyqtSignal()
    work_ended_signal = QtCore.pyqtSignal()
    information_signal = QtCore.pyqtSignal(str)
    error_signal = QtCore.pyqtSignal(str)
    question_signal = QtCore.pyqtSignal(str, str, str, str)
    set_progress_text_signal = QtCore.pyqtSignal(str)
    set_progress_range_signal = QtCore.pyqtSignal(int)
    set_progress_update_interval_signal = QtCore.pyqtSignal(int)
    increase_progress_signal = QtCore.pyqtSignal(int)
    set_progress_value_signal = QtCore.pyqtSignal(int)
    close_progress_signal = QtCore.pyqtSignal()

    def __init__(self, mnemosyne):
        super().__init__()
        self.mnemosyne = mnemosyne
        # A fast moving progress bar seems to cause crashes on Windows.
        self.show_numeric_progress_bar = (sys.platform != "win32")

    def do_work(self):
        pass  # Override this with the actual task.

    def run(self):
        try:
            # Libmnemosyne itself could also generate dialog messages, so
            # we temporarily override the main_widget with the threaded
            # routines in this class.
            self.mnemosyne.component_manager.components\
                [None]["main_widget"].append(self)
            self.do_work()
        except Exception as e:
            self.show_error(str(e) + "\n" + traceback_string())
        finally:
            self.mnemosyne.database().release_connection()
            self.mnemosyne.component_manager.components\
                [None]["main_widget"].pop()
        self.work_ended_signal.emit()

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


class QtGuiThread(Component, QtCore.QObject):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.worker_thread = None  # Assign a QtWorkerThread here.
        # Since we will overwrite the true main widget in the worker thread,
        # we need to save it here.
        self.true_main_widget = self.main_widget()

    def run_worker_thread(self):
        self.database().release_connection()
        self.worker_thread.information_signal.connect(\
            self.threaded_show_information)
        self.worker_thread.error_signal.connect(\
            self.threaded_show_error)
        self.worker_thread.question_signal.connect(\
            self.threaded_show_question)
        self.worker_thread.set_progress_text_signal.connect(\
            self.true_main_widget.set_progress_text)
        self.worker_thread.set_progress_range_signal.connect(\
            self.true_main_widget.set_progress_range)
        self.worker_thread.set_progress_update_interval_signal.connect(\
            self.true_main_widget.set_progress_update_interval)
        self.worker_thread.increase_progress_signal.connect(\
            self.true_main_widget.increase_progress)
        self.worker_thread.set_progress_value_signal.connect(\
            self.true_main_widget.set_progress_value)
        self.worker_thread.close_progress_signal.connect(\
            self.true_main_widget.close_progress)
        self.worker_thread.work_ended_signal.connect(self.work_ended)
        self.worker_thread.start()

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

    def work_ended(self):
        pass  # Override if necessary.
