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
    
    def __init__(self, filename, item_id, parent = None,name = None,fl = 0):
        MainFrm.__init__(self,parent,name,fl)

        self.shrink = True

        self.item = None
        
        self.sched  = QLabel("Scheduled: 0", self.statusBar())
        self.notmem = QLabel("Not memorised: 0", self.statusBar())        
        self.all    = QLabel("All: 0", self.statusBar())
        
        self.statusBar().addWidget(self.sched,0,1)
        self.statusBar().addWidget(self.notmem,0,1)
        self.statusBar().addWidget(self.all,0,1)
        
        self.statusBar().setSizeGripEnabled(0)
        
        self.connect(self.importAction,SIGNAL("activated()"), self.Import)
        self.connect(self.exportAction,SIGNAL("activated()"), self.export)
        
        self.connect(self.addItemsAction,SIGNAL("activated()"),
                     self.addItems)
        self.connect(self.editItemsAction,SIGNAL("activated()"),
                     self.editItems)
        self.connect(self.cleanDuplicatesAction,SIGNAL("activated()"),
                     self.cleanDuplicates)
        self.connect(self.editCurrentItemAction,SIGNAL("activated()"),
                     self.editCurrentItem)
        self.connect(self.deleteCurrentItemAction,SIGNAL("activated()"),
                     self.deleteCurrentItem)
        self.connect(self.activateCategoriesAction,SIGNAL("activated()"),
                     self.activateCategories)
        self.connect(self.productTourAction,SIGNAL("activated()"),
                     self.productTour)

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
        
        self.updateCaption()
        self.updateStatusBar()

        if number_of_items() != 0:
            self.editItemsAction.setEnabled(1) 
            
        if get_config("hide_toolbar") == True:
            self.toolbar.hide()
            self.showToolbarAction.setOn(0)
        
        self.connect(self.showToolbarAction,SIGNAL("toggled(bool)"),
                     self.showToolbar)
        self.connect(self.configurationAction,SIGNAL("activated()"),
                     self.configuration)
   
        self.connect(self.show_button, SIGNAL("clicked()"),
                     self.showAnswer)
        self.connect(self.grades,SIGNAL("clicked(int)"),
                     self.gradeAnswer)
        
        if get_config("QA_font") != None:
            font = QFont()
            font.fromString(get_config("QA_font"))
            self.question.setFont(font)
            self.answer.setFont(font)
            
        if get_config("left_align") == True:
            self.question.setAlignment(Qt.AlignAuto | Qt.AlignVCenter)
            self.answer.setAlignment(Qt.AlignAuto | Qt.AlignVCenter)

        if item_id != None:
            try:
                item = get_item_by_id(long(item_id))
                dlg = EditItemDlg(item,self,"Edit item",0)
                dlg.exec_loop()
            except:
                pass
        
        self.newQuestion()

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
            self.clearQuestion()
            self.updateStatusBar()
            self.editItemsAction.setEnabled(0)
            
            new_database(out)
            load_database(get_config("path"))
            self.updateCaption()
                        
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

            self.clearQuestion()
            self.updateStatusBar()
            
            status = load_database(out)
            
            if status == False:
                QMessageBox.critical(None,
                    self.trUtf8("Mnemosyne"),
                    self.trUtf8("File doesn't appear to be in "+\
                                "the correct format."),
                    self.trUtf8("&OK"), QString(), QString(), 0, -1)
                self.editItemsAction.setEnabled(0)
                unpause_thinking()
                return

            self.updateCaption()

            if self.item == None: # Button shows 'learn ahead of schedule'.
                self.show_button.setText("&Show answer")
                self.languageChange() # Reset shortcuts.

            self.updateStatusBar()
            self.newQuestion()

        if number_of_items() != 0:
            self.editItemsAction.setEnabled(1)
        else:
            self.editItemsAction.setEnabled(0)           

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

            self.updateCaption()

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
        self.updateStatusBar()

        if self.item == None:
            self.show_button.setText("&Show answer")
            self.show_button.setDefault(True)
            self.newQuestion()

        if number_of_items() != 0:
            self.editItemsAction.setEnabled(1)
        else:
            self.editItemsAction.setEnabled(0)
            
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
        
        self.updateStatusBar()
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
        self.updateStatusBar()
        
        if self.item == None:
            self.show_button.setText("&Show answer")
            self.newQuestion()
            
        if number_of_items() != 0:
            self.editItemsAction.setEnabled(1)
            
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
        self.updateStatusBar()
        
        if not in_revision_queue(self.item):
            self.newQuestion()
        else:
            self.updateQuestion()
            remove_from_revision_queue(self.item) # It's already being asked.

        if number_of_items() == 0:
            self.editItemsAction.setEnabled(0)
            
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
        self.updateStatusBar()
        
        if not in_revision_queue(self.item):
            self.newQuestion()
        else:
            self.updateQuestion()
            
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
        self.updateQuestion()
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
        
        if status == 1:
            unpause_thinking()
            return
        else:
            delete_item(self.item)
            self.updateStatusBar()
            self.newQuestion()
            
        if number_of_items() == 0:
            self.editItemsAction.setEnabled(0)
            
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
        self.updateStatusBar()
        
        if self.item == None: # Button shows 'learn ahead of schedule'.
            self.show_button.setText("&Show answer")
            self.languageChange() # Reset shortcuts.
   
        if not in_revision_queue(self.item):
            self.newQuestion()
        else:
            self.updateQuestion()
            remove_from_revision_queue(self.item) # It's already being asked.
            
        unpause_thinking()

    ##########################################################################
    #
    # showToolbar
    #
    ##########################################################################

    def showToolbar(self, active):
        
        pause_thinking()
        if active:
            self.toolbar.show()
            set_config("hide_toolbar", False)
        else:
            self.toolbar.hide()
            set_config("hide_toolbar", True)
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
        
        if get_config("QA_font") != None:
            font = QFont()
            font.fromString(get_config("QA_font"))
            self.question.setFont(font)
            self.answer.setFont(font)
        else:
            self.question.setFont(self.show_button.font())
            self.answer.setFont(self.show_button.font())
            
        if get_config("left_align") == True:
            self.question.setAlignment(Qt.AlignAuto | Qt.AlignVCenter)
            self.answer.setAlignment(Qt.AlignAuto | Qt.AlignVCenter)
        else:
            self.question.setAlignment(Qt.AlignCenter)
            self.answer.setAlignment(Qt.AlignCenter)
            
        self.updateQuestion()
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
    # updateCaption
    #
    ##########################################################################

    def updateCaption(self):
        self.setCaption(unicode("Mnemosyne - " \
                        + os.path.basename(get_config("path"))[:-4],"utf-8"))
        
    ##########################################################################
    #
    # updateStatusBar
    #
    ##########################################################################

    def updateStatusBar(self):
        
        self.sched .setText("Scheduled: "     + str(scheduled_items()))
        self.notmem.setText("Not memorised: " + str(non_memorised_items()))
        self.all   .setText("All: "           + str(active_items()))
        
    ##########################################################################
    #
    # clearQuestion
    #
    ##########################################################################

    def clearQuestion(self):
        
        self.item = None
        self.question_label.setText("Question:")
        self.question.setText("")
        self.answer.setText("")
        self.show_button.setEnabled(0)
        self.editCurrentItemAction.setEnabled(0)
        self.deleteCurrentItemAction.setEnabled(0)
        self.grades.setEnabled(0)

        if self.shrink == True:
            self.adjustSize()
        
    ##########################################################################
    #
    # newQuestion
    #
    ##########################################################################

    def newQuestion(self, learn_ahead = False):
        
        self.clearQuestion()
        
        if number_of_items() == 0:
            return

        self.item = get_new_question(learn_ahead)

        if self.item == None:
            self.show_button.setText("Learn ahead of schedule")
            self.show_button.setEnabled(1)
            return
        
        if self.item.cat.name != "<default>":
            self.question_label.setText(preprocess("Question: " +
                                        self.item.cat.name))

        self.question.setText(preprocess(self.item.q))

        self.editCurrentItemAction.setEnabled(1)
        self.deleteCurrentItemAction.setEnabled(1)
        self.show_button.setDefault(True)
        self.show_button.setEnabled(1)

        if self.shrink == True:
            self.adjustSize()
        
        start_thinking()

    ##########################################################################
    #
    # updateQuestion
    #
    ##########################################################################

    def updateQuestion(self):
        
        if self.item == None:
            return
                
        if self.item.cat.name != "<default>":
            self.question_label.setText(preprocess("Question: " + \
                                                   self.item.cat.name))
            
        self.question.setText(preprocess(self.item.q))
            
        if self.answer.text() != "":
            self.answer.setText(preprocess(self.item.a))

        if self.shrink == True:
            self.adjustSize()

    ##########################################################################
    #
    # showAnswer
    #
    ##########################################################################

    def showAnswer(self):

        if self.item == None: # Button shows 'learn ahead of schedule'.
            self.show_button.setText("&Show answer")
            self.languageChange() # Reset keyboard shortcuts.
            self.newQuestion(learn_ahead = True)
            return

        stop_thinking()
        self.answer.setText(preprocess(self.item.a))        
        self.show_button.setEnabled(0)
        self.show_button.setDefault(False)
        self.grade_4_button.setDefault(True)
        self.grades.setEnabled(1)

        if self.shrink == True:
            self.adjustSize()
        
    ##########################################################################
    #
    # gradeAnswer
    #
    ##########################################################################

    def gradeAnswer(self, grade):

        process_answer(self.item, grade)
        self.grades.setEnabled(0)
        self.grade_4_button.setDefault(False)
        self.updateStatusBar()
        self.question.setText("")
        self.answer.setText("")
        self.newQuestion()
        
