##############################################################################
#
# Main widget for Mnemosyne <Peter.Bienstman@UGent.be>
#
##############################################################################

import gettext
_ = gettext.gettext

# TODO: show toolbar

import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_main_window import *

import review_wdgt
from add_cards_dlg import *
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
from sound import *
from message_boxes import *
from mnemosyne.libmnemosyne import *
from mnemosyne.libmnemosyne.config import config
from mnemosyne.libmnemosyne.card import *
from mnemosyne.libmnemosyne.stopwatch import stopwatch
from mnemosyne.libmnemosyne.component_manager import get_database
from mnemosyne.libmnemosyne.component_manager import get_ui_controller_main
from mnemosyne.libmnemosyne.component_manager import get_ui_controller_review

prefix = os.path.dirname(__file__) # TODO: still needed?


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, filename, parent = None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        get_ui_controller_main().widget = self
        self.update_review_widget()

        self.sched = QLabel("", self.statusbar)
        self.notmem = QLabel("", self.statusbar)
        self.all = QLabel("", self.statusbar)

        self.statusbar.addPermanentWidget(self.sched)
        self.statusbar.addPermanentWidget(self.notmem)
        self.statusbar.addPermanentWidget(self.all)
        self.statusbar.setSizeGripEnabled(0)

        try:
            initialise_user_plugins()
        except MnemosyneError, e:
            messagebox_errors(self, e)

        if filename == None:
            filename = config["path"]

        try:
            get_database().load(filename)
        except MnemosyneError, e:
            messagebox_errors(self, LoadErrorCreateTmp())
            filename = os.path.join(os.path.split(filename)[0],"___TMP___.mem")
            get_database().new(filename)
            
        get_ui_controller_review().new_question()

    def information_box(self, message, OK_string):
        QMessageBox.information(None, _("Mnemosyne"), message, OK_string)

    def question_box(self, question, option0, option1, option2):
        return QMessageBox.question(None, _("Mnemosyne"),
                                    question, option0, option1, option2, 0, -1)

    def update_review_widget(self):
        w = self.centralWidget()
        if w:
            w.close()
            del w
        get_ui_controller_review().widget = \
            component_manager.get_current("review_widget")()
        self.setCentralWidget(get_ui_controller_review().widget)

    def fileNew(self):
        stopwatch.pause()
        # TODO: improve basedir handling.
        out = unicode(QFileDialog.getSaveFileName(basedir,
                        _("Mnemosyne databases (*.mem)"), self, None,\
                        _("New")))
        if out != "":
            if out[-4:] != ".mem":
                out += ".mem"
            if os.path.exists(out):
                if not queryOverwriteFile(self, out):
                    stopwatch.unpause()
                    return
            unload_database()
            self.state = "EMPTY"
            self.card = None
            new_database(out)
            load_database(config["path"])
        self.updateDialog()
        stopwatch.unpause()

    def fileOpen(self):
        stopwatch.pause()
        oldPath = expand_path(get_config("path"))
        out = unicode(QFileDialog.getOpenFileName(oldPath,\
                    _("Mnemosyne databases (*.mem)"), self))
        if out != "":
            try:
                unload_database()
            except MnemosyneError, e:
                messagebox_errors(self, e)
            self.state = "EMPTY"
            self.card = None
            try:
                load_database(out)
            except MnemosyneError, e:
                messagebox_errors(self, e)
                stopwatch.unpause()
                return
            self.newQuestion()

        self.updateDialog()
        stopwatch.unpause()

    def fileSave(self):
        stopwatch.pause()
        path = config["path"]
        try:
            save_database(path)
        except MnemosyneError, e:
            messagebox_errors(self, e)
        stopwatch.unpause()


    def fileSaveAs(self):
        stopwatch.pause()
        oldPath = expand_path(config["path"])
        out = unicode(QFileDialog.getSaveFileName(oldPath,\
                    _("Mnemosyne databases (*.mem)"), self))
        if out != "":
            if out[-4:] != ".mem":
                out += ".mem"
            if os.path.exists(out) and out != config["path"]:
                if not queryOverwriteFile(self, out):
                    stopwatch.unpause()
                    return
            try:
                save_database(out)
            except MnemosyneError, e:
                messagebox_errors(self, e)
                stopwatch.unpause()
                return
        self.updateDialog()
        stopwatch.unpause()

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

    def fileExit(self):
        self.close()

    def addCards(self):
        stopwatch.pause()
        dlg = AddCardsDlg(self)
        dlg.exec_()
        if get_ui_controller_review().card == None:
            get_ui_controller_review().new_question()
        self.updateDialog()
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

    def editCurrentCard(self):
        stopwatch.pause()
        dlg = EditCardDlg(self.card, self)
        dlg.exec_()
        self.updateDialog()
        stopwatch.unpause()

    def deleteCurrentCard(self):
        # TODO: ask user if he wants to delete all related cards, or only 
        # deactivate this cardview?
        
        stopwatch.pause()
        status = QMessageBox.warning(None,
                                     _("Mnemosyne"),
                                     _("Delete current card?"),
                                     _("&Yes"), _("&No"),
                                     QString(), 1, -1)
        if status == 0:
            delete_card(self.card)
            self.newQuestion()
        self.updateDialog()
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

    def closeEvent(self, event):
        # TODO: To implement
        try:
            config.save()
            backup_database()
            unload_database()
        except MnemosyneError, e:
            messagebox_errors(self, e)
            event.ignore()
        else:
            event.accept()


    def productTour(self):
        # TODO: activate tour.
        return
        stopwatch.pause()
        dlg = ProductTourDlg(self)
        dlg.exec_()
        stopwatch.unpause()

    def Tip(self):
        # TODO: activate tips.
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
