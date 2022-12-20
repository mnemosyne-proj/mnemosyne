#
# qt_web_server.py <Peter.Bienstman@gmail.com>
#

import os
import sys
import socket

from PyQt6 import QtCore

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.web_server.web_server import WebServer
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import traceback_string

# The following is some thread synchronisation machinery to ensure that
# either the web server thread or the main thread is doing database
# operations.

answer = None
mutex = QtCore.QMutex()
dialog_closed = QtCore.QWaitCondition()
database_released = QtCore.QWaitCondition()



class ServerThread(QtCore.QThread, WebServer):

    """When a review request comes in, the main thread will release the
    database connection, which will be recreated in the server thread. After
    the review is finished, the server thread will release the database
    connection again.

    Also note that in Qt, we cannot do GUI updates in the server thread, so we
    use the signal/slot mechanism to notify the main thread to do the
    necessary GUI operations.

    """

    # TODO: migrate to qt_worker_thread mechanism.

    review_started_signal = QtCore.pyqtSignal()
    review_ended_signal = QtCore.pyqtSignal()
    information_signal = QtCore.pyqtSignal(str)
    error_signal = QtCore.pyqtSignal(str)
    question_signal = QtCore.pyqtSignal(str, str, str, str)
    set_progress_text_signal = QtCore.pyqtSignal(str)
    set_progress_range_signal = QtCore.pyqtSignal(int)
    set_progress_update_interval_signal = QtCore.pyqtSignal(int)
    increase_progress_signal = QtCore.pyqtSignal(int)
    set_progress_value_signal = QtCore.pyqtSignal(int)
    close_progress_signal = QtCore.pyqtSignal()

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.server_has_connection = False

    def run(self):
        try:
            self.activate()
            self.serve_until_stopped()
        except socket.error:
            self.show_error(_("Unable to start web server."))
        except Exception as e:
            self.show_error(str(e) + "\n" + traceback_string())
        # Clean up after stopping.
        if self.server_has_connection:
            self.database().release_connection()
        self.server_has_connection = False
        if self in self.component_manager.components[None]["main_widget"]:
            self.component_manager.components[None]["main_widget"].pop()
        database_released.wakeAll()

    def load_mnemosyne(self):
        # Load Mnemosyne and its database in the review server thread.
        self.set_progress_text(_("Remote review in progress..."))
        mutex.lock()
        # Libmnemosyne itself could also generate dialog messages, so
        # we temporarily override the main_widget with the threaded
        # routines in this class.
        self.component_manager.components[None]["main_widget"].append(self)
        self.review_started_signal.emit()
        if not self.server_has_connection:
            database_released.wait(mutex)
        WebServer.load_mnemosyne(self)
        self.server_has_connection = True
        mutex.unlock()

    def unload_mnemosyne(self):
        # Close Mnemosyne and its database in the review server thread.
        self.close_progress()
        mutex.lock()
        server_had_connection = self.server_has_connection
        if self.server_has_connection:
            WebServer.unload_mnemosyne(self)
            self.server_has_connection = False
            database_released.wakeAll()
        if self in self.component_manager.components[None]["main_widget"]:
            self.component_manager.components[None]["main_widget"].pop()
        mutex.unlock()
        if server_had_connection:
            # Reload database in the main program.
            self.review_ended_signal.emit()

    def flush(self):
        mutex.lock()
        if not self.server_has_connection:
            database_released.wait(mutex)
        self.server_has_connection = True
        mutex.unlock()

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


class QtWebServer(Component, QtCore.QObject):

    component_type = "web_server"

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.thread = None
        # Since we will overwrite the true main widget in the thread, we need
        # to save it here.
        self.true_main_widget = self.main_widget()

    def activate(self):
        Component.activate(self)
        if self.config()["run_web_server"]:
            # Restart the thread to have the new settings take effect.
            self.deactivate()
            try:
                self.thread = ServerThread(
                    port=self.config()["web_server_port"],
                    data_dir=self.config().data_dir,
                    config_dir=self.config().config_dir,
                    filename=self.config()["last_database"],
                    component_manager=self.component_manager)
            except socket.error as exception:
                (errno, e) = exception.args
                if errno == 98:
                    self.main_widget().show_error(\
                        _("Unable to start web server.") + " " + \
    _("There still seems to be an old server running on the requested port.")\
                        + " " + _("Terminate that process and try again."))
                    self.thread = None
                    return
                elif errno == 13:
                    self.main_widget().show_error(\
                        _("Unable to start web server.") + " " + \
    _("You don't have the permission to use the requested port."))
                    self.thread = None
                    return
                else:
                    raise e
            self.thread.review_started_signal.connect(\
                self.unload_database)
            self.thread.review_ended_signal.connect(\
                self.load_database)
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
            self.thread.start()

    def unload_database(self):
        # Unload database in main thread.
        mutex.lock()
        # Since this function can get called by libmnemosyne outside of the
        # review protocol, 'thread.server_has_connection' is not necessarily
        # accurate, so we can't rely on its value to determine whether we have
        # the ownership to release the connection. Therefore, we always
        # attempt to release the connection, and if it fails because the server
        # already has access, we just ignore this.
        try:
            self.database().release_connection()
        except: # Database locked in server thread.
            pass
        self.thread.server_has_connection = True
        database_released.wakeAll()
        mutex.unlock()

    def load_database(self):
        # Load database in main thread.
        self.stopwatch().pause()
        mutex.lock()
        try:
            self.database().load(self.config()["last_database"])
        except Exception as e: # Database locked in server thread.
            database_released.wait(mutex)
            self.database().load(self.config()["last_database"])
        self.log().loaded_database()
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().update_dialog(redraw_all=True)
        self.thread.server_has_connection = False
        mutex.unlock()
        self.stopwatch().unpause()

    def flush(self):
        # Don't flush the server if not needed, as loading and unloading the
        # database can be expensive.
        if not self.thread:
            return
        mutex.lock()
        is_idle = self.thread.is_idle()
        mutex.unlock()
        if is_idle: # No need to unload the database if server is not active.
            return
        self.unload_database()
        self.thread.flush()
        self.load_database()

    def deactivate(self):
        if not self.thread:
            return
        self.unload_database()
        self.thread.stop()
        self.thread.wait()
        self.thread = None
        Component.deactivate(self)

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
