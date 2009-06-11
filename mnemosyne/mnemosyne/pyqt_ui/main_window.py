#
# main_window.py <Peter.Bienstman@UGent.be>
#

import sys
import os

from PyQt4 import QtCore, QtGui

from ui_main_window import Ui_MainWindow
from add_cards_dlg import AddCardsDlg
from edit_fact_dlg import EditFactDlg
from card_appearance_dlg import CardAppearanceDlg
from activate_plugins_dlg import ActivatePluginsDlg
from cloned_card_types_list_dlg import ClonedCardTypesListDlg
#from import_dlg import *
#from export_dlg import *
#from edit_item_dlg import *
#from clean_duplicates import *
#from statistics_dlg import *
#from edit_items_dlg import *
#from activate_categories_dlg import *
#from config_dlg import *
#from product_tour_dlg import *
#from tip_dlg import *
#from about_dlg import *
from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


# The folloving is need to determine the location of the translations.
# TODO: needed?
prefix = os.path.dirname(__file__)


class MainWindow(QtGui.QMainWindow, Ui_MainWindow, MainWidget):

    def __init__(self, component_manager):
        MainWidget.__init__(self, component_manager)
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        self.statusbar_widgets = []

    def activate(self):
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
        
    def run_add_cards_dialog(self):
        dlg = AddCardsDlg(self, self.component_manager)
        dlg.exec_()

    def run_edit_fact_dialog(self, fact, allow_cancel=True):
        dlg = EditFactDlg(fact, self, self.component_manager, allow_cancel)
        dlg.exec_()
        
    def run_manage_card_types_dialog(self):
        dlg = ClonedCardTypesListDlg(self, self.component_manager)
        dlg.exec_()
        
    def run_card_appearance_dialog(self):
        dlg = CardAppearanceDlg(self, self.component_manager)
        dlg.exec_()

    def run_activate_plugins_dialog(self):
        dlg = ActivatePluginsDlg(self, self.component_manager)
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
        rebuild_revision_queue()
        if not in_revision_queue(self.card):
            self.newQuestion()
        else:
            remove_from_revision_queue(self.card) # It's already being asked.
        self.ui_controller_review().update_dialog(redraw_all=True)
        self.updateDialog()
        stopwatch.unpause()

    def cleanDuplicates(self):
        stopwatch.pause()
        self.statusbar.message(_("Please wait..."))
        clean_duplicates(self)
        rebuild_revision_queue()
        if not in_revision_queue(self.card):
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
        rebuild_revision_queue()
        if not in_revision_queue(self.card):
            self.newQuestion()
        else:
            remove_from_revision_queue(self.card) # It's already being asked.
        self.updateDialog()
        stopwatch.unpause()

    def configuration(self):
        stopwatch.pause()
        dlg = ConfigurationDlg(self)
        dlg.exec_loop()
        rebuild_revision_queue()
        if not in_revision_queue(self.card):
            self.newQuestion()
        else:
            remove_from_revision_queue(self.card) # It's already being asked.
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
