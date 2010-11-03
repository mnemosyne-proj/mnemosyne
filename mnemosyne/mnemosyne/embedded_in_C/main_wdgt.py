#
# main_wdgt.py <Peter.Bienstman@UGent.be>
#

import _main_wdgt as _
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class MainWdgt(MainWidget):

    def set_window_title(self, text):
        _.set_window_title(text.encode("utf-8"))
        
    def show_information(self, text):
        _.show_information(text.encode("utf-8"))
        
    def show_question(self, text, option0, option1, option2=""):
        return _.show_question(text.encode("utf-8"),
            option0.encode("utf-8"), option1.encode("utf-8"),
            option2.encode("utf-8"))
    
    def show_error(self, text):
        _.show_information(text.encode("utf-8"))

    def get_filename_to_open(self, path, filter, caption=""):
        return _.get_filename_to_open(path.encode("utf-8"),
            filter.encode("utf-8"), caption.encode("utf-8"))
    
    def get_filename_to_save(self, path, filter, caption=""):
        return _.get_filename_to_save(path.encode("utf-8"),
            filter.encode("utf-8"), caption.encode("utf-8"))
   
    def set_status_bar_message(self, text):
        _.set_status_bar_message(text.encode("utf-8"))
    
    def set_progress_text(self, text):
        _.set_progress_text(text.encode("utf-8"))
                
    def set_progress_range(self, minimum, maximum):
        _.set_progress_range(minimum, maximum)
        
    def set_progress_update_interval(self, update_interval):
        _.set_progress_update_interval(update_interval)
        
    def set_progress_value(self, value):
        _.set_progress_value(value)
        
    def close_progress(self):
        _.close_progress()

    def enable_edit_current_card(self, is_enabled):
        _.enable_edit_current_card(is_enabled)

    def enable_delete_current_card(self, is_enabled):
        _.enable_delete_current_card(is_enabled)

    def enable_browse_cards(self, is_enabled):      
        _.enable_browse_cards(is_enabled)
