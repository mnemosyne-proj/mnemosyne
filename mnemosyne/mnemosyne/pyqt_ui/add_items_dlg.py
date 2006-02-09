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

    def __init__(self, parent = None, name = None, modal = 0, fl = 0):
        
        AddItemsFrm.__init__(self,parent,name,modal,fl)
        
        self.categories.insertItem("<default>")
        for cat in get_categories():
            if cat.name != "<default>":
                self.categories.insertItem(cat.name.decode("utf-8"))

        self.connect(self.grades,SIGNAL("clicked(int)"),
                     self.new_item)
        
        if get_config("QA_font") != None:
            font = QFont()
            font.fromString(get_config("QA_font"))
            self.question.setFont(font)
            self.answer.setFont(font)
            #self.categories.setFont(font)
            
        self.question.setTabChangesFocus(1)
        self.answer.setTabChangesFocus(1)



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
                    
                status = QMessageBox.question(None,
                      self.trUtf8("Mnemosyne"),
                      self.trUtf8("There are different answers for "+
                                  "this question."),
                      self.trUtf8("&Merge and edit"),
                      self.trUtf8("&Add as is"),
                      self.trUtf8("&Don't add"), 0, -1)
                
                if status == 0: # Merge and edit.
                    
                    new_item = add_new_item(grade, q, a, cat_name)
                    
                    if cat_name not in get_category_names():
                        self.categories.insertItem(cat_name)
                        
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
        
        if cat_name not in get_category_names():
            self.categories.insertItem(cat_name)
            
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

        q        = unicode(self.question.text()         ).encode("utf-8")
        a        = unicode(self.answer.text()           ).encode("utf-8")
        cat_name = unicode(self.categories.currentText()).encode("utf-8")

        if q == "" or a == "":
            return

        orig_added = self.check_duplicates_and_add(grade, q, a, cat_name)
        rev_added = True
        if orig_added and self.addViceVersa.isOn():
            rev_added = self.check_duplicates_and_add(grade, a, q, cat_name)

        if self.addViceVersa.isOn() and orig_added and not rev_added:
            
            # Swap question and answer.
            
            self.question.setText(a.decode("utf-8"))
            self.answer.setText(q.decode("utf-8"))
            self.addViceVersa.setChecked(False)
            
        elif orig_added:
            
            # Clear the form to make room for new question.
            
            self.question.setText("")
            self.answer.setText("")
            
        self.question.setFocus()
