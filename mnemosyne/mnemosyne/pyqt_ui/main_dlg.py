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

        self.item = None
        
        self.sched  = QLabel("Scheduled: 0", self.statusBar())
        self.notmem = QLabel("Not memorised: 0", self.statusBar())        
        self.all    = QLabel("All: 0", self.statusBar())
        
        self.statusBar().addWidget(self.sched,0,1)
        self.statusBar().addWidget(self.notmem,0,1)
        self.statusBar().addWidget(self.all,0,1)
        
        self.statusBar().setSizeGripEnabled(0)
        
        self.connect(self.importAction,SIGNAL("activated()"), self.importXML)
        self.connect(self.exportAction,SIGNAL("activated()"), self.exportXML)
        
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

        if filename != None:
            load_database(filename)
        else:
            load_database(get_config("path"))
        
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
            
        if sys.platform == "win32":
            path = "pixmaps"
        else:
            path = os.path.join(sys.exec_prefix,"lib","python"+sys.version[:3],
                                "site-packages","mnemosyne", "pixmaps")

        self.fileNewAction.setIconSet \
             (QIconSet(QPixmap(os.path.join(path,"filenew.png"))))
        self.fileOpenAction.setIconSet \
             (QIconSet(QPixmap(os.path.join(path,"fileopen.png"))))
        self.fileSaveAction.setIconSet \
             (QIconSet(QPixmap(os.path.join(path,"filesave.png"))))
        self.fileSaveAsAction.setIconSet \
             (QIconSet(QPixmap(os.path.join(path,"filesaveas.png"))))
        self.importAction.setIconSet \
             (QIconSet(QPixmap(os.path.join(path,"fileimport.png"))))
        self.exportAction.setIconSet \
             (QIconSet(QPixmap(os.path.join(path,"fileexport.png"))))
        self.fileExitAction.setIconSet \
             (QIconSet(QPixmap(os.path.join(path,"exit.png"))))
        self.configurationAction.setIconSet \
             (QIconSet(QPixmap(os.path.join(path,"configure.png"))))
        self.addItemsAction.setIconSet \
             (QIconSet(QPixmap(os.path.join(path,"edit_add.png"))))
        self.editItemsAction.setIconSet \
             (QIconSet(QPixmap(os.path.join(path,"edit.png"))))
        self.editCurrentItemAction.setIconSet \
             (QIconSet(QPixmap(os.path.join(path,"editclear.png"))))
        self.deleteCurrentItemAction.setIconSet \
             (QIconSet(QPixmap(os.path.join(path,"editdelete.png"))))

        self.setIcon(QPixmap(os.path.join(path,"mnemosyne.png")))

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
                status = QMessageBox.warning(None,
                    self.trUtf8("Mnemosyne"),
                    self.trUtf8("Overwrite existing file?"),
                    self.trUtf8("&Yes"), self.trUtf8("&No"),
                    QString(), 1, -1)
                if status == 1:
                    unpause_thinking()
                    return

            unload_database()
            self.clearQuestion()
            self.updateStatusBar()

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
                
        out = unicode(QFileDialog.getOpenFileName(get_config("path"),\
                                                  "*.mem")).encode("utf-8")
        if out != "":

            status = unload_database()
            if status == False:
                QMessageBox.critical(None,
                                     self.trUtf8("Mnemosyne"),
                                     self.trUtf8("Unable to save file."),
                                     self.trUtf8("&OK"), QString(), QString(),
                                     0, -1)   
            self.clearQuestion()
            self.updateStatusBar()
            
            status = load_database(out)
            self.updateCaption()
            if status == False:
                QMessageBox.critical(None,
                    self.trUtf8("Mnemosyne"),
                    self.trUtf8("File doesn't appear to be in "+\
                                "the correct format."),
                    self.trUtf8("&OK"), QString(), QString(), 0, -1)
                unpause_thinking()
                return

            self.updateStatusBar()
            self.newQuestion()

        unpause_thinking()
                
    ##########################################################################
    #
    # fileSave
    #
    ##########################################################################
    
    def fileSave(self):

        pause_thinking()

        status = save_database(get_config("path"))
        
        if status == False:
            QMessageBox.critical(None,
                 self.trUtf8("Mnemosyne"),
                 self.trUtf8("Unable to save file."),
                 self.trUtf8("&OK"), QString(), QString(), 0, -1)

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
                status = QMessageBox.warning(None,
                    self.trUtf8("Mnemosyne"),
                    self.trUtf8("Overwrite existing file?"),
                    self.trUtf8("&Yes"), self.trUtf8("&No"),
                    QString(), 1, -1)
                if status == 1:
                    unpause_thinking()
                    return
                
            status = save_database(out)
            if status == False:
                QMessageBox.critical(None,
                    self.trUtf8("Mnemosyne"),
                    self.trUtf8("Unable to save file."),
                    self.trUtf8("&OK"), QString(), QString(), 0, -1)
                unpause_thinking()
                return            

            self.updateCaption()

        unpause_thinking()
            
    ##########################################################################
    #
    # importXML
    #
    ##########################################################################

    def importXML(self):

        pause_thinking()
        
        try:
            from xml.sax import saxutils, make_parser
            from xml.sax.handler import feature_namespaces
        except:
            QMessageBox.critical(None,
                  self.trUtf8("Mnemosyne"),
                  self.trUtf8("PyXML must be installed to import XML."),
                  self.trUtf8("&OK"), QString(), QString(), 0, -1)
            unpause_thinking()
            return

        dlg = ImportDlg(self,"Import",0)
        dlg.exec_loop()
        self.updateStatusBar()
        if self.item == None:
            self.show_button.setText("&Show answer")
            self.show_button.setDefault(True)
            self.newQuestion()

        if number_of_items() != 0:
            self.editItemsAction.setEnabled(1)

        unpause_thinking()
        
    ##########################################################################
    #
    # exportXML
    #
    ##########################################################################

    def exportXML(self):
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
        if number_of_items() == 0:
            self.editItemsAction.setEnabled(0)
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
            QMessageBox.critical(None,
                                 self.trUtf8("Mnemosyne"),
                                 self.trUtf8("Unable to save file."),
                                 self.trUtf8("&OK"), QString(), QString(),
                                 0, -1)   
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
        self.setCaption("Mnemosyne - " \
                        + os.path.basename(get_config("path"))[:-4])
        
    ##########################################################################
    #
    # updateStatusBar
    #
    ##########################################################################

    def updateStatusBar(self):
        self.sched .setText("Scheduled: "     + str(scheduled_items()))
        self.notmem.setText("Not memorised: " + str(non_memorised_items()))
        self.all   .setText("All: "           + str(number_of_items()))
        
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
        
    ##########################################################################
    #
    # newQuestion
    #
    ##########################################################################

    def newQuestion(self, learn_ahead = False):
        
        self.clearQuestion()
        
        if number_of_items() == 0:
            return

        self.question.setText("")
        self.answer.setText("")
        self.editCurrentItemAction.setEnabled(0)
        self.deleteCurrentItemAction.setEnabled(0)
        self.grades.setEnabled(0)
         
        self.item = get_new_question(learn_ahead)

        if self.item == None:
            self.show_button.setText("Learn ahead of schedule")
            self.show_button.setEnabled(1)
            return
        
        if self.item.cat.name != "<default>":
            self.question_label.setText(escape("Question: " +
                                          self.item.cat.name))

        self.question.setText(escape(self.item.q))

        self.editCurrentItemAction.setEnabled(1)
        self.deleteCurrentItemAction.setEnabled(1)
        self.show_button.setDefault(True)
        self.show_button.setEnabled(1)
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
            self.question_label.setText(escape("Question: " + \
                                               self.item.cat.name))
            
        self.question.setText(escape(self.item.q))
            
        if self.answer.text() != "":
            self.answer.setText(escape(self.item.a))

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
        self.answer.setText(escape(self.item.a))        
        self.show_button.setEnabled(0)
        self.show_button.setDefault(False)
        self.grade_4_button.setDefault(True)
        self.grades.setEnabled(1)
        
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
