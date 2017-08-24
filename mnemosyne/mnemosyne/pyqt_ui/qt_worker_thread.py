#
# qt_worker_thread.py <Peter.Bienstman@UGent.be>
#

import os
import sys

from PyQt5 import QtCore

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import traceback_string


answer = None
mutex = QtCore.QMutex()
dialog_closed = QtCore.QWaitCondition()


class WorkerThread(QtCore.QThread):

    """Note that in Qt, we cannot do GUI updates in the worker thread, so we
    use the signal/slot mechanism to notify the main thread to do the
    necessary GUI operations.

    """

    sync_started_signal = QtCore.pyqtSignal()
    sync_ended_signal = QtCore.pyqtSignal()
    information_signal = QtCore.pyqtSignal(str)
    error_signal = QtCore.pyqtSignal(str)
    question_signal = QtCore.pyqtSignal(str, str, str, str)
    set_progress_text_signal = QtCore.pyqtSignal(str)
    set_progress_range_signal = QtCore.pyqtSignal(int)
    set_progress_update_interval_signal = QtCore.pyqtSignal(int)
    increase_progress_signal = QtCore.pyqtSignal(int)
    set_progress_value_signal = QtCore.pyqtSignal(int)
    close_progress_signal = QtCore.pyqtSignal()

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


class GUIThread(Component, QtCore.QObject):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.thread = None
        # Since we will overwrite the true main widget in the thread, we need
        # to save it here.
        self.true_main_widget = self.main_widget()

    def connect_signals(self):
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
