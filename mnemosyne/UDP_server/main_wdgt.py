#
# main_wdgt.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.UDP_server.UDP_widget import UDP_Widget
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class MainWdgt(MainWidget, UDP_Widget):

    def __init__(self, component_manager):
        MainWidget.__init__(self, component_manager)

    def set_window_title(self, text):
        self.callback(text)

    def show_information(self, text):
        self.callback(text)

    def show_question(self, text, option0, option1, option2):
        self.callback(text, option0, option1, option2)
        return int(self.read_from_socket())

    def show_error(self, text):
        self.callback(text)

    def get_filename_to_open(self, path, filter, caption=""):
        self.callback(path, filter, caption)
        return self.read_from_socket()

    def get_filename_to_save(self, path, filter, caption=""):
        self.callback(path, filter, caption)
        return self.read_from_socket()

    def set_status_bar_message(self, text):
        self.callback(text)

    def set_progress_text(self, text):
        self.callback(text)

    def set_progress_range(self, maximum):
        self.callback(maximum)

    def set_progress_update_interval(self, update_interval):
        self.callback(update_interval)

    def increase_progress(self, value):
        self.callback(value)

    def set_progress_value(self, value):
        self.callback(value)

    def close_progress(self):
        self.callback()

    def enable_edit_current_card(self, is_enabled):
        self.callback(is_enabled)

    def enable_delete_current_card(self, is_enabled):
        self.callback(is_enabled)

    def enable_browse_cards(self, is_enabled):
        self.callback(is_enabled)

