##############################################################################
#
# Widget to add new items <Peter.Bienstman@UGent.be>
# Duplicate check by Jarno Elonen <elonen@iki.fi>
#
##############################################################################

from qt import *

from mnemosyne.core import *
from add_items_frm import *
from edit_item_dlg import *



##############################################################################
#
# AddItemsDlg
#
##############################################################################

class AddItemsDlg(AddItemsFrm):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self, parent=None, name=None, modal=0):
        
        AddItemsFrm.__init__(self,parent,name,modal,
                             Qt.WStyle_MinMax | Qt.WStyle_SysMenu)
        
        self.addViceVersa.setChecked(get_config("last_add_vice_versa"))
        self.update_combobox(get_config("last_add_category"))

        self.connect(self.grades, SIGNAL("clicked(int)"),
                     self.new_item)

        self.connect(self.preview_button, SIGNAL("clicked()"),
                     self.preview)

        self.connect(self.question, PYSIGNAL("3_way_input_toggled"),
                     self.toggle_3_way)

        self.connect(self.answer, PYSIGNAL("3_way_input_toggled"),
                     self.toggle_3_way)
        
        if get_config("QA_font") != None:
            font = QFont()
            font.fromString(get_config("QA_font"))
            self.question.setFont(font)
            self.answer.setFont(font)
            #self.categories.setFont(font)
            
        self.question.setTabChangesFocus(1)
        self.answer.setTabChangesFocus(1)
        
        # Doesn't seem to work yet...
        
        #self.question.__class__.dropEvent = self.my_drop_event



    ##########################################################################
    #
    # update_combobox
    #
    ##########################################################################

    def update_combobox(self, current_cat_name):

        no_of_categories = self.categories.count()
        for i in range(no_of_categories-1,-1,-1):
            self.categories.removeItem(i)

        self.categories.insertItem("<default>")
        names = [cat.name for cat in get_categories()]
        names.sort()
        for name in names:
            if name != "<default>":
                self.categories.insertItem(name)

        for i in range(self.categories.count()):
            if self.categories.text(i) == current_cat_name:
                self.categories.setCurrentItem(i)
                break



    ##########################################################################
    #
    # my_drop_event
    #
    ##########################################################################

    def my_drop_event(self, e):
        
        t=QString()
        
        if QTextDrag.decode(e, t): # fills t with decoded text
            
            self.insert(t)
            self.emit(SIGNAL("textChanged()"), ())


            
    ##########################################################################
    #
    # reject
    #
    ##########################################################################
    
    def reject(self):

        if not self.question.text() and not self.answer.text():
            QDialog.reject(self)
            return

        status = QMessageBox.warning(None,
                        qApp.translate("Mnemosyne", "Mnemosyne"),
                        qApp.translate("Mnemosyne", "Abandon current item?"),
                        qApp.translate("Mnemosyne", "&Yes"),
                        qApp.translate("Mnemosyne", "&No"),
                        "", 1, -1)
        if status == 0:
            QDialog.reject(self)
            return
        else:
            return



    ##########################################################################
    #
    # allow_3_way
    #
    ##########################################################################

    def allow_3_way(self):

        return True

        

    ##########################################################################
    #
    # toggle_3_way
    #
    ##########################################################################

    def toggle_3_way(self):

        if not get_config("3_way_input"):
            self.question.show()
        else:
            self.question.hide()            

        

    ##########################################################################
    #
    # preview
    #
    ##########################################################################

    def preview(self):
        
        dlg = PreviewItemDlg(unicode(self.question.text()),
                             unicode(self.answer.text()),
                             unicode(self.categories.currentText()),
                             self,"Preview current item",0)
        dlg.exec_loop()

        

    ##########################################################################
    #
    # check_duplicates_and_add
    #
    ##########################################################################

    def check_duplicates_and_add(self, grade, q, a, cat_name):

        if get_config("check_duplicates_when_adding") == True:

            # Find duplicate questions and refuse to add if duplicate
            # answers are found as well.
            
            allow_dif_cat = get_config("allow_duplicates_in_diff_cat")
            
            same_questions = []
            
            for item in get_items():
                if item.q == q:
                    if item.a == a:
                        
                        if item.cat.name == cat_name or not allow_dif_cat:
                            QMessageBox.information(None,
                                self.trUtf8("Mnemosyne"),
                                self.trUtf8("Item is already in database.\n"+
                                            "Duplicate not added."),
                                self.trUtf8("&OK"))
                
                            return True   
                        
                    elif item.cat.name == cat_name or not allow_dif_cat:
                        same_questions.append(item)

            # Make a list of already existing answers for this question
            # and merge if the user wishes so.
            
            if len(same_questions) != 0:

                answers = a
                for i in same_questions:
                    answers += ' / ' + i.a
                        
                status = QMessageBox.question(None,
                      self.trUtf8("Mnemosyne"),
                      self.trUtf8("There are different answers for "+
                                  "this question:\n\n"+answers.encode("utf8")),
                      self.trUtf8("&Merge and edit"),
                      self.trUtf8("&Add as is"),
                      self.trUtf8("&Don't add"), 0, -1)
                
                if status == 0: # Merge and edit.
                    
                    new_item = add_new_item(grade, q, a, cat_name)
                    self.update_combobox(cat_name)
                    
                    for i in same_questions:
                        new_item.grade = min(new_item.grade, i.grade)
                        new_item.a += ' / ' + i.a
                        delete_item(i)
                        
                    dlg = EditItemDlg(new_item, self, "Edit merged item", 0)
                    
                    dlg.exec_loop()
                    
                    return True

                if status == 2: # Don't add.
                    return False

        add_new_item(grade, q, a, cat_name)
        self.update_combobox(cat_name)
                
        return True



    ##########################################################################
    #
    # new_item
    #
    #   Don't rebuild revision queue afterwards, as this can cause corruption
    #   for the current item. The new items will show up after the old queue
    #   is empty.
    #
    ##########################################################################

    def new_item(self, grade):

        q        = unicode(self.question.text())
        a        = unicode(self.answer.text())
        cat_name = unicode(self.categories.currentText())

        if self.addViceVersa.isOn():
            if q == "" or a == "":
                return
        else:
            if q == "":
                return            

        orig_added = self.check_duplicates_and_add(grade, q, a, cat_name)
        rev_added = True
        if orig_added and self.addViceVersa.isOn():
            rev_added = self.check_duplicates_and_add(grade, a, q, cat_name)

        if self.addViceVersa.isOn() and orig_added and not rev_added:
            
            # Swap question and answer.
            
            self.question.setText(a)
            self.answer.setText(q)
            self.addViceVersa.setChecked(False)
            
        elif orig_added:
            
            # Clear the form to make room for new question.
            
            self.question.setText("")
            self.answer.setText("")
            
        self.question.setFocus()

        set_config("last_add_vice_versa", self.addViceVersa.isOn())
        set_config("last_add_category",   cat_name)

        save_database(get_config("path"))
