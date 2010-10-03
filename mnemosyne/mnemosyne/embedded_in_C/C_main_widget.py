#
# C_main_widget.py <Peter.Bienstman@UGent.be>
#

import _C_main_widget
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class C_MainWidget(MainWidget):

    # TMP

    def callback(self, *args):
        pass

    def read_from_socket(self):
        pass

    def status_bar_message(self, message):
        self.callback(message)

    def show_information(self, message):
        self.callback(message)
        
    def show_question(self, question, option0, option1, option2=""):
        a = _C_main_widget._show_question(question, option0, option1, option2)
        print 'got', a
        return a
    
    def show_error(self, message):
        self.callback(message)
        
    def set_progress_text(self, text):
        self.callback(text)
        
    def set_progress_range(self, minimum, maximum):
        self.callback(minimum, maximum)
        
    def set_progress_update_interval(self, update_interval):
        self.callback(update_interval)
        
    def set_progress_value(self, value):
        self.callback(value)
        
    def close_progress(self):
        self.callback()
        
    def enable_edit_current_card(self, enable):
        self.callback(enable)        

    def enable_delete_current_card(self, enable):
        self.callback(enable)

    def enable_browse_cards(self, enable):      
        self.callback(enable)

    def save_file_dialog(self, path, filter, caption=""):
        self.callback(path, filter, caption)
        return self.read_from_socket()       
    
    def open_file_dialog(self, path, filter, caption=""):
        self.callback(path, filter, caption)
        return self.read_from_socket()

    def set_window_title(self, title):
        _C_main_widget._set_window_title(title)

