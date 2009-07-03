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
        self.statusbar_widgets = []

    def closeEvent(self, event):
        self.config()["main_window_size"] = (self.width(), self.height())

    def activate(self):
        width, height = self.config()["main_window_size"]
        if width:
            self.resize(width, height)
        self.timer_1 = QtCore.QTimer()
        self.connect(self.timer_1, QtCore.SIGNAL("timeout()"),
                     self.ui_controller_review().heartbeat)
        self.timer_1.start(1000 * 60 * 10)
        self.timer_2 = QtCore.QTimer()
        self.connect(self.timer_2, QtCore.SIGNAL("timeout()"),
                     self.ui_controller_main().heartbeat)
        self.timer_2.start(1000 * 60 * 60 * 24)
        
    def add_to_statusbar(self, widget):
        self.statusbar_widgets.append(widget)
        self.statusbar.addPermanentWidget(widget)

    def clear_statusbar(self):
        for widget in self.statusbar_widgets:
            self.statusbar.removeWidget(widget)
        self.statusbar_widgets = []

    def information_box(self, message):
        QtGui.QMessageBox.information(None, _("Mnemosyne"), message, _("&OK"))

    def question_box(self, question, option0, option1, option2):
        return QtGui.QMessageBox.question(None,  _("Mnemosyne"),
            question, option0, option1, option2, 0, -1)

    def error_box(self, message):  
        QtGui.QMessageBox.critical(None, _("Mnemosyne"), message,
            _("&OK"), "", "", 0, -1)
 
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
        self.ui_controller_main().add_cards()

    def edit_current_card(self):
        self.ui_controller_main().edit_current_card()
        
    def delete_current_fact(self):
        self.ui_controller_main().delete_current_fact()
        
    def file_new(self):
        self.ui_controller_main().file_new()

    def file_open(self):
        self.ui_controller_main().file_open()
        
    def file_save(self):
        self.ui_controller_main().file_save()
        
    def file_save_as(self):
        self.ui_controller_main().file_save_as()
        
    def manage_card_types(self):
        self.ui_controller_main().manage_card_types()
        
    def card_appearance(self):
        self.ui_controller_main().card_appearance()
        
    def activate_plugins(self):
        self.ui_controller_main().activate_plugins()

    def show_statistics(self):
        self.ui_controller_main().show_statistics()
        
    def run_add_cards_dialog(self):
        dlg = self.component_manager.get_current("add_cards_dialog")\
            (self, self.component_manager)
        dlg.exec_()

    def run_edit_fact_dialog(self, fact, allow_cancel=True):
        dlg = self.component_manager.get_current("edit_fact_dialog")\
            (fact, self, self.component_manager, allow_cancel)
        dlg.exec_()
        
    def run_manage_card_types_dialog(self):
        dlg = self.component_manager.get_current("manage_card_types_dialog")\
            (self, self.component_manager)
        dlg.exec_()
        
    def run_card_appearance_dialog(self):
        dlg = self.component_manager.get_current("card_appearance_dialog")\
            (self, self.component_manager)
        dlg.exec_()

    def run_activate_plugins_dialog(self):
        dlg = self.component_manager.get_current("activate_plugins_dialog")\
            (self, self.component_manager)
        dlg.exec_()

    def run_show_statistics_dialog(self):
        dlg = self.component_manager.get_current("statistics_dialog")\
            (self, self.component_manager)
        dlg.exec_()
        
    def Import(self):
        stopwatch.pause()
        from xml.sax import saxutils, make_parser
        from xml.sax.handler import feature_namespaces
        dlg = ImportDlg(self)
        dlg.exec_loop()
        if self.card == None:
            self.newQuestion()
        self.updateDialog()
        stopwatch.unpause()

    def export(self):
        stopwatch.pause()
        dlg = ExportDlg(self)
        dlg.exec_loop()
        stopwatch.unpause()

    def editCards(self):
        stopwatch.pause()
        dlg = EditCardsDlg(self)
        dlg.exec_()
        rebuild_queue()
        if not in_queue(self.card):
            self.newQuestion()
        else:
            remove_from_queue(self.card) # It's already being asked.
        self.ui_controller_review().update_dialog(redraw_all=True)
        self.updateDialog()
        stopwatch.unpause()

    def cleanDuplicates(self):
        stopwatch.pause()
        self.statusbar.message(_("Please wait..."))
        clean_duplicates(self)
        rebuild_queue()
        if not in_queue(self.card):
            self.newQuestion()
        self.updateDialog()
        stopwatch.unpause()

    def showStatistics(self):
        stopwatch.pause()
        dlg = StatisticsDlg(self)
        dlg.exec_()
        stopwatch.unpause()

    def activateCategories(self):
        stopwatch.pause()
        dlg = ActivateCategoriesDlg(self)
        dlg.exec_()
        rebuild_queue()
        if not in_queue(self.card):
            self.newQuestion()
        else:
            remove_from_queue(self.card) # It's already being asked.
        self.updateDialog()
        stopwatch.unpause()

    def configuration(self):
        stopwatch.pause()
        dlg = ConfigurationDlg(self)
        dlg.exec_loop()
        rebuild_queue()
        if not in_queue(self.card):
            self.newQuestion()
        else:
            remove_from_queue(self.card) # It's already being asked.
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
