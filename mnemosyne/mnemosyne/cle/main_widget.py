#
# main_wdgt.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

class MainWdgt(MainWidget):

    def __init__(self, component_manager):
        MainWidget.__init__(self, component_manager)
        self.is_progress_bar_showing = False
        self.progress_bar_current_value = 0
        self.progress_bar_update_interval = 1
        self.progress_bar_last_shown_value = 0		

    def show_information(self, text):
        if self.is_progress_bar_showing:
            self.close_progress()
        self.component_manager.activity.showInformation(text.encode("utf-8"))            

    def show_question(self, text, option0, option1, option2):
        if self.is_progress_bar_showing:
            self.close_progress()
        return self.component_manager.activity.showQuestion(\
            text.encode("utf-8"), option0.encode("utf-8"), 
            option1.encode("utf-8"), option2.encode("utf-8"))

    def show_error(self, text):
        self.show_information(text)

    def set_progress_text(self, text):
        if self.is_progress_bar_showing:
            self.close_progress()	
        self.component_manager.activity.setProgressText(text.encode("utf-8"))

    def set_progress_range(self, maximum):
        self.component_manager.activity.setProgressRange(maximum)

    def set_progress_update_interval(self, update_interval):
        update_interval = int(update_interval)
        if update_interval == 0:
            update_interval = 1
        self.progress_bar_update_interval = update_interval

    def increase_progress(self, value):
        self.set_progress_value(self.progress_bar_current_value + value)

    def set_progress_value(self, value):
        print 'start python set_progress_value'
        # There is a possibility that 'value' does not visit all intermediate
        # integer values in the range, so we need to check and store the last
        # shown and the current value here.
        self.progress_bar_current_value = value
        if value - self.progress_bar_last_shown_value >= \
               self.progress_bar_update_interval:
            self.component_manager.activity.setProgressValue(value)
            self.progress_bar_last_shown_value = value
        print 'done python set_progress_value'

    def close_progress(self):
        self.is_progress_bar_showing = False
        self.component_manager.activity.closeValue()

