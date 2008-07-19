##############################################################################
#
# Main widget for Mnemosyne <Peter.Bienstman@UGent.be>
#
##############################################################################

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
from mnemosyne.libmnemosyne.mnemosyne_core import *
from mnemosyne.libmnemosyne.config import get_config
from mnemosyne.libmnemosyne.card import *

prefix = os.path.dirname(__file__)



##############################################################################
#
# Tooltip texts
#
##############################################################################

tooltip = [["","","","","",""],["","","","","",""]]

def install_tooltip_strings(self):

    global tooltip
    
    tooltip[0][0] = \
        self.trUtf8("You don't remember this card yet.")
    tooltip[0][1] = \
        self.trUtf8("Like '0', but it's getting more familiar.").append(\
        self.trUtf8(" Show it less often."))
    tooltip[0][2] = tooltip[0][3] = tooltip[0][4] = tooltip[0][5] = \
        self.trUtf8("You've memorised this card now,").append(\
        self.trUtf8(" and will probably remember it for a few days."))

    tooltip[1][0] = tooltip[1][1] = \
        self.trUtf8("You have forgotten this card completely.")
    tooltip[1][2] = \
        self.trUtf8("Barely correct answer. The interval was way too long.")
    tooltip[1][3] = \
        self.trUtf8("Correct answer, but with much effort.").append(\
        self.trUtf8(" The interval was probably too long."))
    tooltip[1][4] = \
        self.trUtf8("Correct answer, with some effort.").append(\
        self.trUtf8(" The interval was probably just right."))
    tooltip[1][5] = \
        self.trUtf8("Correct answer, but without any").append(\
        self.trUtf8(" difficulties. The interval was probably too short."))



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

        self.review_widget = None
        self.update_review_widget()
        
        #self.shrink = True

        self.q_sound_played = False
        self.a_sound_played = False
        
        self.sched  = QLabel("", self.statusbar)
        self.notmem = QLabel("", self.statusbar)        
        self.all    = QLabel("", self.statusbar)
        
        self.statusbar.addPermanentWidget(self.sched)
        self.statusbar.addPermanentWidget(self.notmem)
        self.statusbar.addPermanentWidget(self.all)
        self.statusbar.setSizeGripEnabled(0)

        try:
            run_user_plugins()
        except MnemosyneError, e:
            messagebox_errors(self, e)
                
        if filename == None:
            filename = get_config("path")

        # TODO: enable load/save

        #try:
        #    load_database(filename)
        #except MnemosyneError, e:
        #    messagebox_errors(self, LoadErrorCreateTmp())
        #    filename =os.path.join(os.path.split(filename)[0],"___TMP___.mem")
        #    new_database(filename)
        

        # TODO: add sound.

        #self.timer = QTimer(self)
        #self.connect(self.timer, SIGNAL("timeout()"), soundmanager.update)
        #self.timer.setSingleShot(False)
        #self.timer.start(250)


        
    ##########################################################################
    #
    # update_review_widget
    #
    ##########################################################################

    def update_review_widget(self):

        if self.central_widget:
            self.central.close()
            del self.card_widget

        # TODO: remove hard coded widget.
        
        self.central_widget = ReviewWdgt()

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

        pause_thinking()

		# TODO: improve basedir handling.
		
        out = unicode(QFileDialog.getSaveFileName(basedir,
                 self.trUtf8("Mnemosyne databases (*.mem)"), self, None,\
                 self.trUtf8("New")))
        if out != "":
            
            if out[-4:] != ".mem":
                out += ".mem"
                
            if os.path.exists(out):
                if not queryOverwriteFile(self, out):
                    unpause_thinking()
                    return

            unload_database()
            self.state = "EMPTY"
            self.card = None
            new_database(out)
            load_database(get_config("path"))

        self.updateDialog()
        
        unpause_thinking()
            
    ##########################################################################
    #
    # fileOpen
    #
    ##########################################################################

    def fileOpen(self):

        pause_thinking()
                
        oldPath = expand_path(get_config("path"))
        out = unicode(QFileDialog.getOpenFileName(oldPath,\
                 self.trUtf8("Mnemosyne databases (*.mem)"), self))
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
                unpause_thinking()
                return

            self.newQuestion()

        self.updateDialog()
        unpause_thinking()
                
    ##########################################################################
    #
    # fileSave
    #
    ##########################################################################
    
    def fileSave(self):

        pause_thinking()

        path = get_config("path")
        
        try:
            save_database(path)
        except MnemosyneError, e:
            messagebox_errors(self, e)

        unpause_thinking()

    ##########################################################################
    #
    # fileSaveAs
    #
    ##########################################################################

    def fileSaveAs(self):
        
        pause_thinking()

        oldPath = expand_path(get_config("path"))
        out = unicode(QFileDialog.getSaveFileName(oldPath,\
                 self.trUtf8("Mnemosyne databases (*.mem)"), self))
                         
        if out != "":
            
            if out[-4:] != ".mem":
                out += ".mem"

            if os.path.exists(out) and out != get_config("path"):
                if not queryOverwriteFile(self, out):
                    unpause_thinking()
                    return
                
            try:
                save_database(out)
            except MnemosyneError, e:
                messagebox_errors(self, e)
                unpause_thinking()
                return            

        self.updateDialog()
        unpause_thinking()
            
    ##########################################################################
    #
    # Import
    #
    ##########################################################################

    def Import(self):

        pause_thinking()
        
        from xml.sax import saxutils, make_parser
        from xml.sax.handler import feature_namespaces

        dlg = ImportDlg(self)
        dlg.exec_loop()
         
        if self.card == None:
            self.newQuestion()

        self.updateDialog()
        unpause_thinking()
        
    ##########################################################################
    #
    # export
    #
    ##########################################################################

    def export(self):
        
        pause_thinking()

        dlg = ExportDlg(self)
        dlg.exec_loop()
                
        unpause_thinking()
        
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
        
        pause_thinking()
        
        dlg = AddCardsDlg(self)
        dlg.exec_()
        
        if self.card == None:
            self.newQuestion()
            
        self.updateDialog()
        unpause_thinking()
        
    ##########################################################################
    #
    # editCards
    #
    ##########################################################################
    
    def editCards(self):
        
        pause_thinking()
        
        dlg = EditCardsDlg(self)
        dlg.exec_()
        rebuild_revision_queue()
        
        if not in_revision_queue(self.card):
            self.newQuestion()
        else:
            remove_from_revision_queue(self.card) # It's already being asked.

        self.updateDialog()
        unpause_thinking()
        
    ##########################################################################
    #
    # cleanDuplicates
    #
    ##########################################################################
    
    def cleanDuplicates(self):
        
        pause_thinking()
        
        self.statusbar.message(self.trUtf8("Please wait..."))
        clean_duplicates(self)
        rebuild_revision_queue()
        
        if not in_revision_queue(self.card):
            self.newQuestion()
            
        self.updateDialog()
        unpause_thinking()

    ##########################################################################
    #
    # showStatistics
    #
    ##########################################################################
    
    def showStatistics(self):
        
        pause_thinking()
        dlg = StatisticsDlg(self)
        dlg.exec_()
        unpause_thinking()
        
    ##########################################################################
    #
    # editCurrentCard
    #
    ##########################################################################
    
    def editCurrentCard(self):
        
        pause_thinking()
        dlg = EditCardDlg(self.card, self)
        dlg.exec_()
        self.updateDialog()
        unpause_thinking()

    ##########################################################################
    #
    # deleteCurrentCard
    #
    ##########################################################################

    def deleteCurrentCard(self):
        
        pause_thinking()
        
        status = QMessageBox.warning(None,
                    self.trUtf8("Mnemosyne"),
                    self.trUtf8("Delete current card?"),
                    self.trUtf8("&Yes"), self.trUtf8("&No"),
                    QString(), 1, -1)
        
        if status == 0:
            delete_card(self.card)
            self.newQuestion()
            
        self.updateDialog()
        unpause_thinking()

    ##########################################################################
    #
    # activateCategories
    #
    ##########################################################################

    def activateCategories(self):
        
        pause_thinking()
        
        dlg = ActivateCategoriesDlg(self)
        dlg.exec_()
        
        rebuild_revision_queue()
        if not in_revision_queue(self.card):
            self.newQuestion()
        else:
            remove_from_revision_queue(self.card) # It's already being asked.
            
        self.updateDialog()
        unpause_thinking()

    ##########################################################################
    #
    # showToolbar
    #
    ##########################################################################

    def showToolbar(self, active):
        
        pause_thinking()
        if active:
            set_config("hide_toolbar", False)
        else:
            set_config("hide_toolbar", True)
        self.updateDialog()
        unpause_thinking()
        
    ##########################################################################
    #
    # configuration
    #
    ##########################################################################

    def configuration(self):
        
        pause_thinking()
        dlg = ConfigurationDlg(self)
        dlg.exec_loop()

        rebuild_revision_queue()
        if not in_revision_queue(self.card):
            self.newQuestion()
        else:
            remove_from_revision_queue(self.card) # It's already being asked.
            
        self.updateDialog()
        unpause_thinking()
            
    ##########################################################################
    #
    # closeEvent
    #
    ##########################################################################

    def closeEvent(self, event):
        
        try:
            save_config()
            backup_database()
            unload_database()
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
        
        # ToDO: activate tour.

        return
        
        pause_thinking()
        dlg = ProductTourDlg(self)
        dlg.exec_()
        unpause_thinking()
        
    ##########################################################################
    #
    # Tip
    #
    ##########################################################################
    
    def Tip(self):

        # ToDO: activate tips.

        return
        
        pause_thinking()
        dlg = TipDlg(self)
        dlg.exec_()
        unpause_thinking()
        
    ##########################################################################
    #
    # helpAbout
    #
    ##########################################################################
    
    def helpAbout(self):
        
        pause_thinking()
        dlg = AboutDlg(self)
        dlg.exec_()
        unpause_thinking()


    ##########################################################################
    #
    # replaySound
    #
    ##########################################################################

    #def replaySound(self):
    #    play_sound(preprocess(self.card.q))
    #    if self.state == "SELECT GRADE":
    #        play_sound(preprocess(self.card.a))
