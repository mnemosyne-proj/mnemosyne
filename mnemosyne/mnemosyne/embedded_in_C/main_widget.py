#
# main_widget.py <Peter.Bienstman@UGent.be>
#

import _main_widget as _
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget \
     as GenericMainWidget


class MainWidget(GenericMainWidget):

    def set_window_title(self, title):
        _.set_window_title(title)
        
    def show_information(self, message):
        _.show_information(message)
        
    def show_question(self, question, option0, option1, option2=""):
        return  _.show_question\
            (question, option0, option1, option2)
    
    def show_error(self, message):
        _.show_information(error)

    def get_filename_to_open(self, path, filter, caption=""):
        return _.get_filename_to_open(path, filter, caption)
    
    def get_filename_to_save(self, path, filter, caption=""):
        return _.get_filename_to_save(path, filter, caption)
   
    def set_status_bar_message(self, message):
        _.set_status_bar_message(message)
    
    def set_progress_text(self, text):
        _.set_progress_text(text)
                
    def set_progress_range(self, minimum, maximum):
        _.set_progress_range(minimum, maximum)
        
    def set_progress_update_interval(self, update_interval):
        _.set_progress_update_interval(update_interval)
        
    def set_progress_value(self, value):
        _.set_progress_value(value)
        
    def close_progress(self):
        _.close_progress()

    def enable_edit_current_card(self, enable):
        _.enable_edit_current_card(enable)

    def enable_delete_current_card(self, enable):
        _.enable_delete_current_card(enable)

    def enable_browse_cards(self, enable):      
        _.enable_browse_cards(enable)
