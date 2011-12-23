#
# main_wdgt.py <Peter.Bienstman@UGent.be>
#

import sys
from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_main_wdgt import Ui_MainWdgt
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class MainWdgt(QtGui.QMainWindow, Ui_MainWdgt, MainWidget):

    def __init__(self, component_manager):
        MainWidget.__init__(self, component_manager)
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        # Qt designer does not allow setting multiple shortcuts per action.
        self.actionDeleteCurrentCard.setShortcuts\
            ([QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace])
        self.status_bar_widgets = []
        self.progress_bar = None
        self.progress_bar_update_interval = 1
        self.progress_bar_last_shown_value = 0

    def _store_state(self):
        self.config()["main_window_state"] = self.saveGeometry()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUi(self)
        QtGui.QMainWindow.changeEvent(self, event)

    def createPopupMenu(self):
        # Don't create a silly popup menu saying ('toolBar').
        pass 

    def closeEvent(self, event):
        # Generated when clicking the window's close button.
        self._store_state()

    def activate(self):
        state = self.config()["main_window_state"]
        if state:
            self.restoreGeometry(state)
        self.TIMER_1_INTERVAL = 1000 * 60 * 10 # For reuse in review widget.
        self.timer_1 = QtCore.QTimer()
        self.timer_1.timeout.connect(self.review_controller_heartbeat)
        self.timer_1.start(self.TIMER_1_INTERVAL)
        self.TIMER_2_INTERVAL = 1000 * 60 * 60 * 12
        self.timer_2 = QtCore.QTimer()
        self.timer_2.timeout.connect(self.controller_heartbeat)
        self.timer_2.start(self.TIMER_2_INTERVAL)
        self.start_review()

    def review_controller_heartbeat(self):
        self.review_controller().heartbeat()  # Late binding
        
    def controller_heartbeat(self):
        self.controller().heartbeat()  # Late binding

    def set_window_title(self, text):
        self.setWindowTitle(text)
        
    def show_information(self, text):
        QtGui.QMessageBox.information(self, _("Mnemosyne"), text, _("&OK"))

    def show_question(self, text, option0, option1, option2):
        return QtGui.QMessageBox.question(self,  _("Mnemosyne"),
            text, option0, option1, option2, 0, -1)

    def show_error(self, text):
        QtGui.QMessageBox.critical(self, _("Mnemosyne"), text,
            _("&OK"), "", "", 0, -1)

    def default_font_size(self):
        return QtGui.qApp.font().pointSize()
    
    def get_filename_to_open(self, path, filter, caption=""):
        return unicode(QtGui.QFileDialog.\
            getOpenFileName(self, caption, path, filter))
     
    def get_filename_to_save(self, path, filter, caption=""):
        return unicode(QtGui.QFileDialog.\
            getSaveFileName(self, caption, path, filter))
    
    def set_status_bar_message(self, text):
        self.status_bar.showMessage(text)

    def set_progress_text(self, text):
        if self.progress_bar:
            self.progress_bar.close()
            self.progress_bar = None
        if not self.progress_bar:
            self.progress_bar = QtGui.QProgressDialog(self)
            self.progress_bar.setWindowTitle(_("Mnemosyne"))
            self.progress_bar.setWindowModality(QtCore.Qt.WindowModal)
            self.progress_bar.setCancelButton(None)
            self.progress_bar.setMinimumDuration(0)
        self.progress_bar.setLabelText(text)
        self.progress_bar.setRange(0, 0)
        self.progress_bar_update_interval = 1
        self.progress_bar_last_shown_value = 0
        self.progress_bar.setValue(0)
        self.progress_bar.show()

    def set_progress_range(self, minimum, maximum):
        self.progress_bar.setRange(minimum, maximum)
        
    def set_progress_update_interval(self, update_interval):
        update_interval = int(update_interval)
        if update_interval == 0:
            update_interval = 1
        self.progress_bar_update_interval = update_interval
        
    def set_progress_value(self, value):
        # There is a possibility that 'value' does not visit all intermediate
        # integer values in the range, so we need to check and store the last
        # shown value here.
        if value - self.progress_bar_last_shown_value >= \
               self.progress_bar_update_interval:
            self.progress_bar.setValue(value)
            self.progress_bar_last_shown_value = value
            # This automatically processes events too. Calling processEvents
            # explictly here might even cause some crashes.
        
    def close_progress(self):
        if self.progress_bar:
            self.progress_bar.close()
        self.progress_bar = None
        
    def enable_edit_current_card(self, is_enabled):
        self.actionEditCurrentCard.setEnabled(is_enabled)

    def enable_delete_current_card(self, is_enabled):      
        self.actionDeleteCurrentCard.setEnabled(is_enabled)

    def enable_browse_cards(self, is_enabled):      
        self.actionBrowseCards.setEnabled(is_enabled)

    def add_to_status_bar(self, widget):
        self.status_bar_widgets.append(widget)
        self.status_bar.addPermanentWidget(widget)

    def clear_status_bar(self):
        for widget in self.status_bar_widgets:
            self.status_bar.removeWidget(widget)
        self.status_bar_widgets = []
        
    def file_new(self):
        self.controller().show_new_file_dialog()

    def file_open(self):
        self.controller().show_open_file_dialog()
        
    def file_save(self):
        self.controller().save_file()
        
    def file_save_as(self):
        self.controller().show_save_file_as_dialog()

    def import_file(self):
        self.controller().show_import_file_dialog()
        
    def export_file(self):
        self.controller().show_export_file_dialog()
 
    def sync(self):
        self.controller().show_sync_dialog()

    def add_cards(self):
        self.controller().show_add_cards_dialog()

    def edit_current_card(self):
        self.controller().show_edit_card_dialog()
        
    def delete_current_card(self):
        self.controller().delete_current_card()
        
    def browse_cards(self):
        self.controller().show_browse_cards_dialog()
        
    def activate_cards(self):
        self.controller().show_activate_cards_dialog()   
        
    def manage_card_types(self):
        self.controller().show_manage_card_types_dialog()
        
    def configure(self):
        self.controller().show_configuration_dialog()
        
    def set_card_appearance(self):
        self.controller().show_card_appearance_dialog()
        
    def activate_plugins(self):
        self.controller().show_activate_plugins_dialog()

    def show_statistics(self):
        self.controller().show_statistics_dialog()

    def show_getting_started(self):
        self.controller().show_getting_started_dialog()

    def show_tip(self):
        self.controller().show_tip_dialog()
        
    def show_about(self):
        self.controller().show_about_dialog()
