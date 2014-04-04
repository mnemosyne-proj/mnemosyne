#
# main_wdgt.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class MainWdgt(MainWidget):

    def __init__(self, component_manager):
        MainWidget.__init__(self, component_manager)
        self.callbacks = {}
        self.is_progress_bar_showing = False
        self.progress_bar_maximum = 100
        self.progress_bar_update_interval = 1
        self.progress_bar_last_shown_value = 0		

    def set_callback(self, name, callback):
        self.callbacks[name] = callback

    def show_information(self, text):
        if self.is_progress_bar_showing:
            self.close_progress()
        self.callbacks["show_information"](text)

    def show_question(self, text, option0, option1, option2):
        if self.is_progress_bar_showing:
            self.close_progress()		
        return self.callbacks["show_question"]\
               (text, option0, option1, option2)

    def show_error(self, text):
        if self.is_progress_bar_showing:
            self.close_progress()			
        self.callbacks["show_error"](text)

    def set_progress_text(self, text):
        if self.is_progress_bar_showing:
            self.close_progress()			
        self.callbacks["set_progress_text"](text)

    def set_progress_range(self, maximum):
        self.progress_bar_maximum = maximum

    def set_progress_update_interval(self, update_interval):
        update_interval = int(update_interval)
        if update_interval == 0:
            update_interval = 1
        self.progress_bar_update_interval = update_interval

    def increase_progress(self, value):
        self.set_progress_value(self.progress_bar_current_value + value)

    def set_progress_value(self, value):
        # There is a possibility that 'value' does not visit all intermediate
        # integer values in the range, so we need to check and store the last
        # shown and the current value here.
        self.progress_bar_current_value = value
        if value - self.progress_bar_last_shown_value >= \
            self.progress_bar_update_interval:
            # Android does not seem to support changing the progress range 
            # after the dialog has been created, so we need to rescale this 
            # to the 0-100 range.
            self.callbacks["set_progress_value"]\
                (int(value / self.progress_bar_maximum * 100))
            self.progress_bar_last_shown_value = value
        if value >= self.progress_bar_maximum:
            self.close_progress()

    def close_progress(self):
        self.is_progress_bar_showing = False
        self.callbacks["close_progress"]()