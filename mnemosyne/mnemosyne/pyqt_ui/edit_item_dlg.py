##############################################################################
#
# Widget to edit single item <Peter.Bienstman@UGent.be>
#
##############################################################################

from qt import *
from mnemosyne.core import *
from edit_item_frm import *

    
##############################################################################
#
# EditItemDlg
#
##############################################################################

class EditItemDlg(EditItemFrm):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, item, parent=None, name=None, modal=0, fl=0):
        
        EditItemFrm.__init__(self,parent,name,modal,fl)

        self.item = item

        self.categories.insertItem(self.item.cat.name.decode("utf-8"))
        for cat in get_categories():
            if cat.name != self.item.cat.name:
                self.categories.insertItem(cat.name.decode("utf-8"))

        self.question.setText(self.item.q.decode("utf-8"))
        self.answer.setText(self.item.a.decode("utf-8"))
        
        self.connect(self.ok_button, SIGNAL("clicked()"), self.apply)

        self.question.setFocus()

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
    # apply
    #
    ##########################################################################
    
    def apply(self):

        new_cat_name = unicode(self.categories.currentText()).encode("utf-8")

        if new_cat_name != self.item.cat.name:
            self.item.change_category(new_cat_name)   
        
        self.item.q  = unicode(self.question.text()).encode("utf-8")
        self.item.a  = unicode(self.answer.text())  .encode("utf-8")

        self.accept()
