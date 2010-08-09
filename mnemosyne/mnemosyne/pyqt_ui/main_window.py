#
# main_window.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_main_window import Ui_MainWindow
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


# The folloving is need to determine the location of the translations.
# TODO: needed?
import os
prefix = os.path.dirname(__file__)


class MainWindow(QtGui.QMainWindow, Ui_MainWindow, MainWidget):

    def __init__(self, component_manager):
        MainWidget.__init__(self, component_manager)
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        self.status_bar_widgets = []
        self.progress_bar = None
        self.progress_bar_update_interval = 1

    def closeEvent(self, event):
        self.config()["main_window_size"] = (self.width(), self.height())

    def activate(self):
        width, height = self.config()["main_window_size"]
        if width:
            self.resize(width, height)
        self.timer_1 = QtCore.QTimer()
        self.connect(self.timer_1, QtCore.SIGNAL("timeout()"),
                     self.review_controller().heartbeat)
        self.timer_1.start(1000 * 60 * 10)
        self.timer_2 = QtCore.QTimer()
        self.connect(self.timer_2, QtCore.SIGNAL("timeout()"),
                     self.controller().heartbeat)
        self.timer_2.start(1000 * 60 * 60 * 24)
        self.review_controller().reset()

    def status_bar_message(self, message):
        self.status_bar.showMessage(message)

    def add_to_status_bar(self, widget):
        self.status_bar_widgets.append(widget)
        self.status_bar.addPermanentWidget(widget)

    def clear_status_bar(self):
        for widget in self.status_bar_widgets:
            self.status_bar.removeWidget(widget)
        self.status_bar_widgets = []

    def information_box(self, message):
        QtGui.QMessageBox.information(None, _("Mnemosyne"), message, _("&OK"))

    def question_box(self, question, option0, option1, option2):
        return QtGui.QMessageBox.question(None,  _("Mnemosyne"),
            question, option0, option1, option2, 0, -1)

    def error_box(self, message):
        QtGui.QMessageBox.critical(None, _("Mnemosyne"), message,
            _("&OK"), "", "", 0, -1)

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
        if value % self.progress_bar_update_interval == 0:
            self.progress_bar.setValue(value)
        
    def close_progress(self):
        if self.progress_bar:
            self.progress_bar.close()
        self.progress_bar = None
        
    def enable_edit_current_card(self, enable):
        self.actionEditCurrentCard.setEnabled(enable)

    def enable_delete_current_card(self, enable):      
        self.actionDeleteCurrentFact.setEnabled(enable)

    def enable_browse_cards(self, enable):      
        self.actionBrowseCards.setEnabled(enable)

    def save_file_dialog(self, path, filter, caption=""):
        return unicode(QtGui.QFileDialog.getSaveFileName(self, caption, path,
                                                         filter))
    
    def open_file_dialog(self, path, filter, caption=""):
        return unicode(QtGui.QFileDialog.getOpenFileName(self, caption, path,
                                                         filter))

    def set_window_title(self, title):
        self.setWindowTitle(title)

    def add_cards(self):
        self.controller().add_cards()

    def edit_current_card(self):
        self.controller().edit_current_card()
        
    def delete_current_fact(self):
        self.controller().delete_current_fact()
        
    def activate_cards(self):
        self.controller().activate_cards()
        
    def file_new(self):
        self.controller().file_new()

    def file_open(self):
        self.controller().file_open()
        
    def file_save(self):
        self.controller().file_save()
        
    def file_save_as(self):
        self.controller().file_save_as()
        
    def manage_card_types(self):
        self.controller().manage_card_types()
        
    def card_appearance(self):
        self.controller().card_appearance()
        
    def activate_plugins(self):
        self.controller().activate_plugins()

    def show_statistics(self):
        self.controller().show_statistics()
        
    def import_file(self):
        self.controller().import_file()
        
    def export_file(self):
        self.controller().export_file()

    def sync(self):
        self.controller().sync()

    def configure(self):
        self.controller().configure()      

    def editCards(self):
        stopwatch.pause()
        dlg = EditCardsDlg(self)
        dlg.exec_()
        rebuild_queue()
        if not in_queue(self.card):
            self.newQuestion()
        else:
            remove_from_queue(self.card) # It's already being asked.
        self.review_controller().update_dialog(redraw_all=True)
        self.updateDialog()
        stopwatch.unpause()

    def cleanDuplicates(self):
        stopwatch.pause()
        self.status_bar.message(_("Please wait..."))
        clean_duplicates(self)
        rebuild_queue()
        if not in_queue(self.card):
            self.newQuestion()
        self.updateDialog()
        stopwatch.unpause()

    def productTour(self):
        return
        stopwatch.pause()
        dlg = ProductTourDlg(self)
        dlg.exec_()
        stopwatch.unpause()

    def Tip(self):
        return
        stopwatch.pause()
        dlg = TipDlg(self)
        dlg.exec_()
        stopwatch.unpause()

    def helpAbout(self):
        stopwatch.pause()
        dlg = AboutDlg(self)
        dlg.exec_()
        stopwatch.unpause()
