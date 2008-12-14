 #
# main_window.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

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
from sound import * # TODO
from message_boxes import * # TODO
from mnemosyne.libmnemosyne import initialise_user_plugins
from mnemosyne.libmnemosyne.stopwatch import stopwatch
from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.component_manager import database, config
from mnemosyne.libmnemosyne.component_manager import ui_controller_main
from mnemosyne.libmnemosyne.component_manager import ui_controller_review

# The folloving is need to determine the location of the translations.
prefix = os.path.dirname(__file__)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, filename, parent = None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        ui_controller_main().widget = self
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
            filename = config()["path"]
        try:
            database().load(filename)
        except MnemosyneError, e:
            messagebox_errors(self, LoadErrorCreateTmp())
            filename = os.path.join(os.path.split(filename)[0],"___TMP___.mem")
            database().new(filename)
        self.update_review_widget()
        ui_controller_review().new_question()

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
        ui_controller_review().widget = \
            component_manager.get_current("review_widget")(parent=self)
        self.setCentralWidget(ui_controller_review().widget)

    def fileNew(self):
        stopwatch.pause()
        out = unicode(QFileDialog.getSaveFileName(config().get_basedir(),
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
            load_database(config()["path"])
        self.updateDialog()
        stopwatch.unpause()

    def fileOpen(self):
        stopwatch.pause()
        oldPath = expand_path(config()["path"])
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
        path = config()["path"]
        try:
            save_database(path)
        except MnemosyneError, e:
            messagebox_errors(self, e)
        stopwatch.unpause()

    def fileSaveAs(self):
        stopwatch.pause()
        oldPath = expand_path(config()["path"])
        out = unicode(QFileDialog.getSaveFileName(oldPath,\
                    _("Mnemosyne databases (*.mem)"), self))
        if out != "":
            if out[-4:] != ".mem":
                out += ".mem"
            if os.path.exists(out) and out != config()["path"]:
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
        controller = ui_controller_review()
        if controller.card == None:
            controller.new_question()
        else:
            self.update_statusbar()
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
        ui_controller_review().update_dialog(redraw_all=True)
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
        ui_controller_review().update_dialog(redraw_all=True)
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
        ui_controller_review().update_dialog(redraw_all=True)
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
        try:
            config().save()
            database().backup()
            database().unload()
        except MnemosyneError, e:
            messagebox_errors(self, e)
            event.ignore()
        else:
            event.accept()

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

    def update_statusbar(self):
        db = database()
        self.sched.setText(_("Scheduled: ") + \
                           str(db.scheduled_count()) + " ")
        self.notmem.setText(_("Not memorised: ") + \
                            str(db.non_memorised_count()) + " ")
        self.all.setText(_("All: ") \
                         + str(db.active_count()) + " ")
