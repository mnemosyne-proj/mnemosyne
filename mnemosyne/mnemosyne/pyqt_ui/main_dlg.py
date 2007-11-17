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
from statistics_dlg import *
from edit_items_dlg import *
from activate_categories_dlg import *
from config_dlg import *
from product_tour_dlg import *
from sound import *
from message_boxes import *
from mnemosyne.core import *

prefix = os.path.dirname(__file__)



##############################################################################
#
# Tooltip texts
#
##############################################################################

tooltip = [["","","","","",""],["","","","","",""]]

def install_tooltip_strings():

    global tooltip
    
    tooltip[0][0] = \
        qApp.trUtf8("You don't remember this card yet.")
    tooltip[0][1] = \
        qApp.trUtf8("Like '0', but it's getting more familiar.").append(\
        qApp.trUtf8(" Show it less often."))
    tooltip[0][2] = tooltip[0][3] = tooltip[0][4] = tooltip[0][5] = \
        qApp.trUtf8("You've memorised this card now,").append(\
        qApp.trUtf8(" and will probably remember it for a few days."))

    tooltip[1][0] = tooltip[1][1] = \
        qApp.trUtf8("You have forgotten this card completely.")
    tooltip[1][2] = \
        qApp.trUtf8("Barely correct answer. The interval was way too long.")
    tooltip[1][3] = \
        qApp.trUtf8("Correct answer, but with much effort.").append(\
        qApp.trUtf8(" The interval was probably too long."))
    tooltip[1][4] = \
        qApp.trUtf8("Correct answer, with some effort.").append(\
        qApp.trUtf8(" The interval was probably just right."))
    tooltip[1][5] = \
        qApp.trUtf8("Correct answer, but without any").append(\
        qApp.trUtf8(" difficulties. The interval was probably too short."))



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

        self.q_sound_played = False
        self.a_sound_played = False
        
        self.sched  = QLabel("", self.statusBar())
        self.notmem = QLabel("", self.statusBar())        
        self.all    = QLabel("", self.statusBar())
        
        self.statusBar().addWidget(self.sched,0,1)
        self.statusBar().addWidget(self.notmem,0,1)
        self.statusBar().addWidget(self.all,0,1)
        self.statusBar().setSizeGripEnabled(0)

        self.grade_buttons = []

        self.grade_buttons.append(self.grade_0_button)
        self.grade_buttons.append(self.grade_1_button)
        self.grade_buttons.append(self.grade_2_button)
        self.grade_buttons.append(self.grade_3_button) 
        self.grade_buttons.append(self.grade_4_button)
        self.grade_buttons.append(self.grade_5_button)      
                
        if filename == None:
            filename = get_config("path")

        try:
            load_database(filename)
        except MnemosyneError, e:
            messagebox_errors(LoadErrorCreateTmp())
            filename = os.path.join(os.path.split(filename)[0],"___TMP___.mem")
            new_database(filename)
        
        self.newQuestion()
        self.updateDialog()

        try:
            run_plugins()
        except MnemosyneError, e:
            messagebox_errors(e)

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
        out = unicode(QFileDialog.getSaveFileName(path,
                 self.trUtf8("Mnemosyne databases (*.mem)"), self))
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
                
        oldPath = expand_path(get_config("path"))
        out = unicode(QFileDialog.getOpenFileName(oldPath,\
                 self.trUtf8("Mnemosyne databases (*.mem)"), self))
        if out != "":

            try:
                unload_database()
            except MnemosyneError, e:
                messagebox_errors(e)

            self.state = "EMPTY"
            self.item = None

            try:
                load_database(out)
            except MnemosyneError, e:
                messagebox_errors(e)
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
            messagebox_errors(e)

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
                if not queryOverwriteFile(out):
                    unpause_thinking()
                    return
                
            try:
                save_database(out)
            except MnemosyneError, e:
                messagebox_errors(e)
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
    # addItems
    #
    ##########################################################################

    def addItems(self):
        
        pause_thinking()
        
        dlg = AddItemsDlg(self)
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
        
        dlg = EditItemsDlg(self)
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
        
        self.statusBar().message(self.trUtf8("Please wait..."))
        clean_duplicates(self)
        rebuild_revision_queue()
        
        if not in_revision_queue(self.item):
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
        dlg.exec_loop()
        unpause_thinking()
        
    ##########################################################################
    #
    # editCurrentItem
    #
    ##########################################################################
    
    def editCurrentItem(self):
        
        pause_thinking()
        dlg = EditItemDlg(self.item, self)
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
                    self.trUtf8("Delete current card?"),
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
        
        dlg = ActivateCategoriesDlg(self)
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
        dlg = ConfigurationDlg(self)
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
    # closeEvent
    #
    ##########################################################################

    def closeEvent(self, event):
        
        try:
            save_config()
            backup_database()
            unload_database()
        except MnemosyneError, e:
            messagebox_errors(e)
            event.ignore()
        else:
            event.accept()

    ##########################################################################
    #
    # productTour
    #
    ##########################################################################
    
    def productTour(self):
        
        pause_thinking()
        dlg = ProductTourDlg(self)
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
            self.trUtf8("Mnemosyne").append(" " + \
            mnemosyne.version.version + "\n\n").append(\
            self.trUtf8("Main author: Peter Bienstman\n\n")).append(\
            self.trUtf8("More info: http://mnemosyne-proj.sourceforge.net\n")))
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

        self.q_sound_played = False
        self.a_sound_played = False
        
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

        interval = process_answer(self.item, grade)
        self.newQuestion()
        self.updateDialog()

        if get_config("show_intervals") == "statusbar":
            self.statusBar().message(self.trUtf8("Returns in ").append(\
                str(interval)).append(self.trUtf8(" day(s).")))
            
    ##########################################################################
    #
    # next_rep_string
    #
    ##########################################################################

    def next_rep_string(self, days):
        
        if days == 0:
            return QString('\n') + self.trUtf8("Next repetition: today.")
        elif days == 1:
            return QString('\n') + self.trUtf8("Next repetition: tomorrow.")
        else: 
            return QString('\n') + self.trUtf8("Next repetition in ").\
                   append(QString(str(days))).\
                   append(qApp.trUtf8(" days."))
        
    ##########################################################################
    #
    # updateDialog
    #
    ##########################################################################

    def updateDialog(self):

        # Update caption.
        
        database_name = os.path.basename(get_config("path"))[:-4]
        caption_text = u"Mnemosyne - " + database_name
        self.setCaption(caption_text)

        # Update menu bar.

        if get_config("only_editable_when_answer_shown") == True:
            if self.item != None and self.state == "SELECT GRADE":
                self.editCurrentItemAction.setEnabled(True)
            else:
                self.editCurrentItemAction.setEnabled(False)
        else:
            if self.item != None:
                self.editCurrentItemAction.setEnabled(True)
            else:
                self.editCurrentItemAction.setEnabled(False)            
            
        self.deleteCurrentItemAction.setEnabled(self.item != None)
        self.editItemsAction.setEnabled(number_of_items() > 0)

        # Update toolbar.
        
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
        
        if get_config("left_align") == True:
            alignment = Qt.AlignAuto    | Qt.AlignVCenter | Qt.WordBreak
        else:
            alignment = Qt.AlignHCenter | Qt.AlignVCenter | Qt.WordBreak

        self.question.setAlignment(alignment)
        self.answer.setAlignment(alignment)

        # Update question label.
        
        question_label_text = self.trUtf8("Question:")
        if self.item!=None and self.item.cat.name!=self.trUtf8("<default>"):
            question_label_text += " " + preprocess(self.item.cat.name)
        self.question_label.setText(question_label_text)

        # Update question content.
        
        if self.item == None:
            self.question.setText("")
        else:
            text = preprocess(self.item.q)

            if self.q_sound_played == False:
                play_sound(text)
                self.q_sound_played = True
                
            if increase_non_latin:
                text = set_non_latin_font_size(text, non_latin_size)

            self.question.setText(text)

        # Update answer content.
        
        if self.item == None or self.state == "SELECT SHOW":
            self.answer.setText("")
        else:
            text = preprocess(self.item.a)

            if self.a_sound_played == False:
                play_sound(text)
                self.a_sound_played = True
                
            if increase_non_latin:
                text = set_non_latin_font_size(text, non_latin_size)
            self.answer.setText(text)

        # Update 'show answer' button.
        
        if self.state == "EMPTY":
            show_enabled, default, text = 0, 1, self.trUtf8("Show &answer")
            grades_enabled = 0
        elif self.state == "SELECT SHOW":
            show_enabled, default, text = 1, 1, self.trUtf8("Show &answer")
            grades_enabled = 0
        elif self.state == "SELECT GRADE":
            show_enabled, default, text = 0, 1, self.trUtf8("Show &answer")
            grades_enabled = 1
        elif self.state == "SELECT AHEAD":
            show_enabled, default, text = 1, 0, \
                                     self.trUtf8("Learn ahead of schedule")
            grades_enabled = 0

        self.show_button.setText(text)
        self.show_button.setDefault(default)
        self.show_button.setEnabled(show_enabled)

        # Update grade buttons.

        if self.item != None and self.item.grade in [0,1]:
            i = 0 # Acquisition phase.
        else:
            i = 1 # Retention phase.     
            
        self.grade_4_button.setDefault(grades_enabled)
        self.grades.setEnabled(grades_enabled)
        
        QToolTip.setWakeUpDelay(0)

        for grade in range(0,6):

            # Tooltip.
            
            QToolTip.remove(self.grade_buttons[grade])
            
            if self.state == "SELECT GRADE" and \
               get_config("show_intervals") == "tooltips":
                QToolTip.add(self.grade_buttons[grade],
                      tooltip[i][grade].
                      append(self.next_rep_string(process_answer(self.item,
                                                  grade, dry_run=True))))
            else:
                QToolTip.add(self.grade_buttons[grade],
                            tooltip[i][grade])

            # Button text.
                    
            if self.state == "SELECT GRADE" and \
               get_config("show_intervals") == "buttons":
                self.grade_buttons[grade].setText(\
                        str(process_answer(self.item, grade, dry_run=True)))
                self.grades.setTitle(\
                    self.trUtf8("Pick days until next repetition:"))
            else:
                self.grade_buttons[grade].setText(str(grade))
                self.grades.setTitle(self.trUtf8("Grade your answer:"))

            self.grade_buttons[grade].setAccel(QKeySequence(str(grade)))

        # Update status bar.
        
        self.sched .setText(self.trUtf8("Scheduled: ") \
                            + str(scheduled_items()))
        self.notmem.setText(self.trUtf8("Not memorised: ") \
                            + str(non_memorised_items()))
        self.all   .setText(self.trUtf8("All: ") \
                            + str(active_items()))

        if self.shrink == True:
            self.adjustSize()

    ##########################################################################
    #
    # replaySound
    #
    ##########################################################################

    def replaySound(self):
        play_sound(preprocess(self.item.q))
        if self.state == "SELECT GRADE":
            play_sound(preprocess(self.item.a))
