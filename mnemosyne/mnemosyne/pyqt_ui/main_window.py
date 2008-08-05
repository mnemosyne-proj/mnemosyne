##############################################################################
#
# Main widget for Mnemosyne <Peter.Bienstman@UGent.be>
#
##############################################################################

import gettext
_ = gettext.gettext

# TODO: show toolbar

import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_main_window import *

from add_cards_dlg import *
from review_wdgt import *
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

prefix = os.path.dirname(__file__)




##############################################################################
#
# MainWindow
#
##############################################################################

class MainWindow(QMainWindow, Ui_MainWindow):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, filename, parent = None):
        
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.update_review_widget()

        
        self.sched  = QLabel("", self.statusbar)  
        self.notmem = QLabel("", self.statusbar)        
        self.all    = QLabel("", self.statusbar)
        
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

        # TODO: enable load/save

        try:
            get_database().load(filename)
        except MnemosyneError, e:
            messagebox_errors(self, LoadErrorCreateTmp())
            filename = os.path.join(os.path.split(filename)[0],"___TMP___.mem")
            get_database().new(filename)

        
    ##########################################################################
    #
    # update_review_widget
    #
    ##########################################################################

    def update_review_widget(self):

        w = self.centralWidget()

        if w:
            w.close()
            del w

        # TODO: remove hard coded widget.
        
        self.setCentralWidget(ReviewWdgt())


        #self.adjustSize()
        
    ##########################################################################
    #
    # resizeEvent
    #
    ##########################################################################
    
    #def resizeEvent(self, e):
    #    
    #    if e.spontaneous() == True:
    #        self.shrink = False
        
    ##########################################################################
    #
    # fileNew
    #
    ##########################################################################

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
            
    ##########################################################################
    #
    # fileOpen
    #
    ##########################################################################

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
                
    ##########################################################################
    #
    # fileSave
    #
    ##########################################################################
    
    def fileSave(self):

        stopwatch.pause()

        path = config["path"]
        
        try:
            save_database(path)
        except MnemosyneError, e:
            messagebox_errors(self, e)

        stopwatch.unpause()

    ##########################################################################
    #
    # fileSaveAs
    #
    ##########################################################################

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
            
    ##########################################################################
    #
    # Import
    #
    ##########################################################################

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
        
    ##########################################################################
    #
    # export
    #
    ##########################################################################

    def export(self):
        
        stopwatch.pause()

        dlg = ExportDlg(self)
        dlg.exec_loop()
                
        stopwatch.unpause()
        
    ##########################################################################
    #
    # fileExit
    #
    ##########################################################################

    def fileExit(self):
        
        self.close()
        
    ##########################################################################
    #
    # addCards
    #
    ##########################################################################

    def addCards(self):
        
        stopwatch.pause()
        
        dlg = AddCardsDlg(self)
        dlg.exec_()
        
        if self.centralWidget().controller.current_card() == None:
            self.centralWidget().controller.new_question()
            
        self.updateDialog()
        stopwatch.unpause()
        
    ##########################################################################
    #
    # editCards
    #
    ##########################################################################
    
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
        
    ##########################################################################
    #
    # cleanDuplicates
    #
    ##########################################################################
    
    def cleanDuplicates(self):
        
        stopwatch.pause()
        
        self.statusbar.message(_("Please wait..."))
        clean_duplicates(self)
        rebuild_revision_queue()
        
        if not in_revision_queue(self.card):
            self.newQuestion()
            
        self.updateDialog()
        stopwatch.unpause()

    ##########################################################################
    #
    # showStatistics
    #
    ##########################################################################
    
    def showStatistics(self):
        
        stopwatch.pause()
        dlg = StatisticsDlg(self)
        dlg.exec_()
        stopwatch.unpause()
        
    ##########################################################################
    #
    # editCurrentCard
    #
    ##########################################################################
    
    def editCurrentCard(self):
        
        stopwatch.pause()
        dlg = EditCardDlg(self.card, self)
        dlg.exec_()
        self.updateDialog()
        stopwatch.unpause()

    ##########################################################################
    #
    # deleteCurrentCard
    #
    ##########################################################################

    def deleteCurrentCard(self):
        
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

    ##########################################################################
    #
    # activateCategories
    #
    ##########################################################################

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

    ##########################################################################
    #
    # showToolbar
    #
    ##########################################################################

    def showToolbar(self, active):
        
        stopwatch.pause()
        if active:
            config["hide_toolbar"] = False
        else:
            config["hide_toolbar"] = True
        self.updateDialog()
        stopwatch.unpause()
        
    ##########################################################################
    #
    # configuration
    #
    ##########################################################################

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
            
    ##########################################################################
    #
    # closeEvent
    #
    ##########################################################################

    def closeEvent(self, event):

        # TODO: To implement
        
        try:
            config.save()
            #backup_database()
            #unload_database()
        except MnemosyneError, e:
            messagebox_errors(self, e)
            event.ignore()
        else:
            event.accept()

    ##########################################################################
    #
    # productTour
    #
    ##########################################################################
    
    def productTour(self):
        
        # TODO: activate tour.

        return
        
        stopwatch.pause()
        dlg = ProductTourDlg(self)
        dlg.exec_()
        stopwatch.unpause()
        
    ##########################################################################
    #
    # Tip
    #
    ##########################################################################
    
    def Tip(self):

        # ToDO: activate tips.

        return
        
        stopwatch.pause()
        dlg = TipDlg(self)
        dlg.exec_()
        stopwatch.unpause()
        
    ##########################################################################
    #
    # helpAbout
    #
    ##########################################################################
    
    def helpAbout(self):
        
        stopwatch.pause()
        dlg = AboutDlg(self)
        dlg.exec_()
        stopwatch.unpause()


    ##########################################################################
    #
    # replaySound
    #
    ##########################################################################

    #def replaySound(self):
    #    play_sound(preprocess(self.card.q))
    #    if self.state == "SELECT GRADE":
    #        play_sound(preprocess(self.card.a))
