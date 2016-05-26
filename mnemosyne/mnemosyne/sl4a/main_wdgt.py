#
# main_wdgt.py <Peter.Bienstman@UGent.be>
#

import android
droid = android.Android()

from .mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class MainWdgt(MainWidget):

    def __init__(self, component_manager):
        MainWidget.__init__(self, component_manager)
        self.is_progress_bar_showing = False
        self.progress_bar_maximum = 100
        self.progress_bar_update_interval = 1
        self.progress_bar_last_shown_value = 0

    def show_information(self, text):
        if self.is_progress_bar_showing:
            self.close_progress()
        droid.dialogCreateAlert("Mnemosyne", text) 
        droid.dialogSetPositiveButtonText("OK")
        droid.dialogShow()
        droid.dialogGetResponse()
        droid.dialogDismiss()

    def show_question(self, text, option0, option1, option2):
        if self.is_progress_bar_showing:
            self.close_progress()
        droid.dialogCreateAlert("Mnemosyne", text) 
        droid.dialogSetPositiveButtonText(option0)
        if option1:
            droid.dialogSetNegativeButtonText(option1)
        if option2:
            droid.dialogSetNeutralButtonText(option2)
        droid.dialogShow()
        result = droid.dialogGetResponse().result["which"]
        droid.dialogDismiss()
        if result == "positive":
            return 0
        elif result == "negative":
            return 1
        elif result == "neutral":
            return 2
        raise NotImplementedError

    def show_error(self, text):
        if self.is_progress_bar_showing:
            self.close_progress()
        self.show_information(text)

    def set_progress_text(self, text):
        if self.is_progress_bar_showing:
            self.close_progress()
        droid.dialogCreateSpinnerProgress("Mnemosyne", text)
        self.progress_bar_maximum = 100
        self.progress_bar_update_interval = 1
        self.progress_bar_current_value = 0
        self.progress_bar_last_shown_value = 0
        droid.dialogShow()
        self.is_progress_bar_showing = True

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
            # SL4A does not seem to support changing the progress range after
            # the dialog has been created, so we need to rescale this to the
            # 0-100 range.
            droid.dialogSetCurrentProgress\
                (int(value / self.progress_bar_maximum * 100))
            self.progress_bar_last_shown_value = value
        if value >= self.progress_bar_maximum:
            self.close_progress()

    def close_progress(self):
        if self.is_progress_bar_showing:
            droid.dialogDismiss()
            self.is_progress_bar_showing = False

    def start_native_browser(self):
        droid.webViewShow("http://127.0.0.1:8513")
