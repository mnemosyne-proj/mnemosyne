##############################################################################
#
# Main widget for Mnemosyne <Peter.Bienstman@UGent.be>
#
##############################################################################

import sys, os
from qt import *
from main_frm import *
from import_dlg import *
from export_dlg import *
from add_items_dlg import *
from edit_item_dlg import *
from clean_duplicates import *
from edit_items_dlg import *
from activate_categories_dlg import *
from config_dlg import *
from product_tour_dlg import *
from mnemosyne.core import *



##############################################################################
#
# messageUnableToSave
#
#  Note: operator+ would be nicer than append, but the PyQt version we use
#        under Windows does not support this.
#
##############################################################################

def messageUnableToSave(fileName):
    
    QMessageBox.critical(None,
                         qApp.translate("Mnemosyne", "Mnemosyne"),
                         qApp.translate("Mnemosyne", "Unable to save file:")\
                         .append(QString("\n" + fileName)),
                         qApp.translate("Mnemosyne", "&OK"),
                         "", "", 0, -1)



##############################################################################
#
# queryOverwriteFile
#
##############################################################################

def queryOverwriteFile(fileName):
    
    status = QMessageBox.warning(None,
                                 qApp.translate("Mnemosyne", "Mnemosyne"),
                                 qApp.translate("Mnemosyne", "File exists: ")\
                                 .append(QString("\n" + fileName)),
                                 qApp.translate("Mnemosyne", "&Overwrite"),
                                 qApp.translate("Mnemosyne", "&Cancel"),
                                 "", 1, -1)
    if status == 0:
        return True
    else:
        return False



##############################################################################
#
# MainDlg
#
##############################################################################

class MainDlg(MainFrm):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, filename, parent = None,name = None,fl = 0):
        MainFrm.__init__(self,parent,name,fl)

        self.state = "EMPTY"
        self.item = None
        
        self.shrink = True
        
        self.sched  = QLabel("", self.statusBar())
        self.notmem = QLabel("", self.statusBar())        
        self.all    = QLabel("", self.statusBar())
        
        self.statusBar().addWidget(self.sched,0,1)
        self.statusBar().addWidget(self.notmem,0,1)
        self.statusBar().addWidget(self.all,0,1)
        self.statusBar().setSizeGripEnabled(0)
        
        if filename == None:
            filename = get_config("path")
        
        status = load_database(filename)
        
        if status == False:
            QMessageBox.critical(None,
                    self.trUtf8("Mnemosyne"),
                    self.trUtf8("Unable to load file. Creating a tmp database."),
                    self.trUtf8("&OK"), QString(), QString(), 0, -1)
            filename = os.path.join(os.path.split(filename)[0],"___TMP___.mem")
            new_database(filename)
        
        self.newQuestion()
        self.updateDialog()

    ##########################################################################
    #
    # resizeEvent
    #
    ##########################################################################
    
    def resizeEvent(self, e):
        
        if e.spontaneous() == True:
            self.shrink = False
        
    ##########################################################################
    #
    # fileNew
    #
    ##########################################################################

    def fileNew(self):

        pause_thinking()

        path = os.path.join(os.path.expanduser("~"), ".mnemosyne")
        out = unicode(QFileDialog.getSaveFileName(path, "*.mem"))\
              .encode("utf-8")
        if out != "":
            
            if out[-4:] != ".mem":
                out += ".mem"
                
            if os.path.exists(out):
                if not queryOverwriteFile(out):
                    unpause_thinking()
                    return

            unload_database()
            self.state = "EMPTY"
            self.item = None
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
                
        oldPath = get_config("path")
        out = unicode(QFileDialog.getOpenFileName(oldPath,\
                                                  "*.mem")).encode("utf-8")
        if out != "":

            status = unload_database()
            if status == False:
                messageUnableToSave(oldPath)

            self.state = "EMPTY"
            self.item = None
            
            status = load_database(out)
            
            if status == False:
                QMessageBox.critical(None,
                    self.trUtf8("Mnemosyne"),
                    self.trUtf8("File doesn't appear to be in "+\
                                "the correct format."),
                    self.trUtf8("&OK"), QString(), QString(), 0, -1)
                self.updateDialog()
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
        status = save_database(path)
        if status == False:
            messageUnableToSave(path)

        unpause_thinking()

    ##########################################################################
    #
    # fileSaveAs
    #
    ##########################################################################

    def fileSaveAs(self):
        
        pause_thinking()
        
        out = unicode(QFileDialog.getSaveFileName(get_config("path"),\
                                                  "*.mem")).encode("utf-8")
        if out != "":
            
            if out[-4:] != ".mem":
                out += ".mem"

            if os.path.exists(out) and out != get_config("path"):
                if not queryOverwriteFile(out):
                    unpause_thinking()
                    return
                
            status = save_database(out)
            if status == False:
                messageUnableToSave(out)
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
        
        try:
            from xml.sax import saxutils, make_parser
            from xml.sax.handler import feature_namespaces
        except:
            QMessageBox.Warning(None,
                  self.trUtf8("Mnemosyne"),
                  self.trUtf8("PyXML must be installed to import XML."),
                  self.trUtf8("&OK"), QString(), QString(), 0, -1)

        dlg = ImportDlg(self,"Import",0)
        dlg.exec_loop()
        if self.item == None:
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
        dlg = ExportDlg(self,"Export",0)
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
    # addItems
    #
    ##########################################################################

    def addItems(self):
        
        pause_thinking()
        
        dlg = AddItemsDlg(self,"Add items",0)
        dlg.exec_loop()
        
        if self.item == None:
            self.newQuestion()
            
        self.updateDialog()
        unpause_thinking()
        
    ##########################################################################
    #
    # editItems
    #
    ##########################################################################
    
    def editItems(self):
        
        pause_thinking()
        
        dlg = EditItemsDlg(self,"Edit items",0)
        dlg.exec_loop()
        rebuild_revision_queue()
        
        if not in_revision_queue(self.item):
            self.newQuestion()
        else:
            remove_from_revision_queue(self.item) # It's already being asked.

        self.updateDialog()
        unpause_thinking()
        
    ##########################################################################
    #
    # cleanDuplicates
    #
    ##########################################################################
    
    def cleanDuplicates(self):
        
        pause_thinking()
        
        self.statusBar().message("Please wait...")
        clean_duplicates(self)
        rebuild_revision_queue()
        
        if not in_revision_queue(self.item):
            self.newQuestion()
            
        self.updateDialog()
        unpause_thinking()
        
    ##########################################################################
    #
    # editCurrentItem
    #
    ##########################################################################
    
    def editCurrentItem(self):
        
        pause_thinking()
        dlg = EditItemDlg(self.item,self,"Edit current item",0)
        dlg.exec_loop()
        self.updateDialog()
        unpause_thinking()

    ##########################################################################
    #
    # deleteCurrentItem
    #
    ##########################################################################

    def deleteCurrentItem(self):
        
        pause_thinking()
        
        status = QMessageBox.warning(None,
                    self.trUtf8("Mnemosyne"),
                    self.trUtf8("Delete current item?"),
                    self.trUtf8("&Yes"), self.trUtf8("&No"),
                    QString(), 1, -1)
        
        if status == 0:
            delete_item(self.item)
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
        
        dlg = ActivateCategoriesDlg(self,"Activate categories",0)
        dlg.exec_loop()
        
        rebuild_revision_queue()
        if not in_revision_queue(self.item):
            self.newQuestion()
        else:
            remove_from_revision_queue(self.item) # It's already being asked.
            
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
        dlg = ConfigurationDlg(self,"Configure Mnemosyne",0)
        dlg.exec_loop()
        self.updateDialog()
        unpause_thinking()
            
    ##########################################################################
    #
    # closeEvent
    #
    ##########################################################################

    def closeEvent(self, event):
        
        save_config()
        status = unload_database()
        if status == False:
            messageUnableToSave(get_config("path"))
        event.accept()

    ##########################################################################
    #
    # productTour
    #
    ##########################################################################
    
    def productTour(self):
        
        pause_thinking()
        dlg = ProductTourDlg(self,"Mnemosyne product tour",0)
        dlg.exec_loop()
        unpause_thinking()
        
    ##########################################################################
    #
    # helpAbout
    #
    ##########################################################################
    
    def helpAbout(self):
        
        import mnemosyne.version
        pause_thinking()
        QMessageBox.about(None,
            self.trUtf8("Mnemosyne"),
            self.trUtf8("Mnemosyne " + mnemosyne.version.version + "\n\n"+
                        "Author: Peter Bienstman\n\n" +
                        "More info: http://mnemosyne-proj.sourceforge.net\n"))
        unpause_thinking()

    ##########################################################################
    #
    # newQuestion
    #
    ##########################################################################

    def newQuestion(self, learn_ahead = False):
        
        if number_of_items() == 0:
            self.state = "EMPTY"
            self.item = None
        else:
            self.item = get_new_question(learn_ahead)
            if self.item != None:
                self.state = "SELECT SHOW"
            else:
                self.state = "SELECT AHEAD"
        
        start_thinking()

    ##########################################################################
    #
    # showAnswer
    #
    ##########################################################################

    def showAnswer(self):

        if self.state == "SELECT AHEAD":
            self.newQuestion(learn_ahead = True)
        else:
            stop_thinking()
            self.state = "SELECT GRADE"
        self.updateDialog()
        
    ##########################################################################
    #
    # gradeAnswer
    #
    ##########################################################################

    def gradeAnswer(self, grade):

        process_answer(self.item, grade)
        self.newQuestion()
        self.updateDialog()

    ##########################################################################
    #
    # updateDialog
    #
    ##########################################################################

    def updateDialog(self):

        # Update caption.
        
        database_name = os.path.basename(get_config("path"))[:-4]
        caption_text = unicode("Mnemosyne - " + database_name, "utf-8")
        self.setCaption(caption_text)

        # Update menu bar.
        
        if self.item != None and self.state == "SELECT GRADE":
            self.editCurrentItemAction.setEnabled(True)
        else:
            self.editCurrentItemAction.setEnabled(False)
        self.deleteCurrentItemAction.setEnabled(self.item != None)
        self.editItemsAction.setEnabled(number_of_items() > 0)

        # Update tool bar.
        
        if get_config("hide_toolbar") == True:
            self.toolbar.hide()
            self.showToolbarAction.setOn(0)
        else:
            self.toolbar.show()
            self.showToolbarAction.setOn(1)

        # Update question and answer font.
        
        if get_config("QA_font") != None:
            font = QFont()
            font.fromString(get_config("QA_font"))
        else:
            font = self.show_button.font()

        self.question.setFont(font)
        self.answer.setFont(font)

        # Size for non-latin characters.

        increase_non_latin = get_config("non_latin_font_size_increase")
        non_latin_size = font.pointSize() + increase_non_latin

        # Update question and answer alignment.

        # Note: for some reason the default alignment is not AlignCenter
        # (68) but some other value (2116) which seems to make a difference
        # in how the widgets are laid out and resized.
        
        if get_config("left_align") == True:
            alignment = Qt.AlignAuto | Qt.AlignVCenter
        else:
            alignment = 2116

        self.question.setAlignment(alignment)
        self.answer.setAlignment(alignment)

        # Update question label.
        
        question_label_text = self.trUtf8("Question:")
        if self.item != None and self.item.cat.name != "<default>":
            question_label_text += " " + preprocess(self.item.cat.name)
        self.question_label.setText(question_label_text)

        # Update question content.
        
        if self.item == None:
            self.question.setText("")
        else:
            text = preprocess(self.item.q)
            if increase_non_latin:
                text = set_non_latin_font_size(text, non_latin_size)
            self.question.setText(text)

        # Update answer content.
        
        if self.item == None or self.state == "SELECT SHOW":
            self.answer.setText("")
        else:
            text = preprocess(self.item.a)            
            if increase_non_latin:
                text = set_non_latin_font_size(text, non_latin_size)
            self.answer.setText(text)

        # Update buttons.
        
        if self.state == "EMPTY":
            show_enabled, default, text = 0, 1, "&Show answer"
            grades_enabled = 0
        elif self.state == "SELECT SHOW":
            show_enabled, default, text = 1, 1, "&Show answer"
            grades_enabled = 0
        elif self.state == "SELECT GRADE":
            show_enabled, default, text = 0, 1, "&Show answer"
            grades_enabled = 1
        elif self.state == "SELECT AHEAD":
            show_enabled, default, text = 1, 0, "Learn ahead of schedule"
            grades_enabled = 0

        self.show_button.setText(self.trUtf8(text))
        self.show_button.setDefault(default)
        self.show_button.setEnabled(show_enabled)

        self.grade_4_button.setDefault(grades_enabled)
        self.grades.setEnabled(grades_enabled)

        # Update status bar.
        
        self.sched .setText("Scheduled: "     + str(scheduled_items()))
        self.notmem.setText("Not memorised: " + str(non_memorised_items()))
        self.all   .setText("All: "           + str(active_items()))

        if self.shrink == True:
            self.adjustSize()
