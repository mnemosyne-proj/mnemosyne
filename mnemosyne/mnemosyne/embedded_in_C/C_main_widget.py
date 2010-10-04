#
# C_main_widget.py <Peter.Bienstman@UGent.be>
#

import _C_main_widget
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class C_MainWidget(MainWidget):

    def set_status_bar_message(self, message):
        _C_main_widget._set_status_bar_message(message)

    def show_information(self, message):
        _C_main_widget._show_information(message)
        
    def show_question(self, question, option0, option1, option2=""):
        return  _C_main_widget._show_question\
            (question, option0, option1, option2)
    
    def show_error(self, message):
        _C_main_widget._show_information(error)
        
    def set_progress_text(self, text):
        _C_main_widget._set_progress_text(text)
                
    def set_progress_range(self, minimum, maximum):
        _C_main_widget._set_progress_range(minimum, maximum)
        
    def set_progress_update_interval(self, update_interval):
        _C_main_widget._set_progress_update_interval(update_interval)
        
    def set_progress_value(self, value):
        _C_main_widget._set_progress_value(value)
        
    def close_progress(self):
        _C_main_widget._close_progress()
        
    def enable_edit_current_card(self, enable):
        _C_main_widget._enable_edit_current_card(enable)

    def enable_delete_current_card(self, enable):
        _C_main_widget._enable_delete_current_card(enable)

    def enable_browse_cards(self, enable):      
        _C_main_widget._enable_browse_cards(enable)

    def get_filename_to_save(self, path, filter, caption=""):
        return _C_main_widget._get_filename_to_save(path, filter, caption)

    def get_filename_to_open(self, path, filter, caption=""):
        return _C_main_widget._get_filename_to_open(path, filter, caption)
    
    def set_window_title(self, title):
        _C_main_widget._set_window_title(title)