##############################################################################
#
# Widget to edit single item <Peter.Bienstman@UGent.be>
#
##############################################################################

from qt import *
from mnemosyne.core import *
from edit_item_frm import *
from preview_item_dlg import *


    
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

        self.categories.insertItem(self.item.cat.name)

        names = get_category_names()
        names.sort()
        for name in names:
            if name != self.item.cat.name:
                self.categories.insertItem(name)

        self.question.setText(self.item.q)
        self.answer.setText(self.item.a)
        
        self.connect(self.ok_button,      SIGNAL("clicked()"), self.apply)
        self.connect(self.preview_button, SIGNAL("clicked()"), self.preview)
        
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
    # allow_3_sided
    #
    ##########################################################################

    def allow_3_sided(self):

        return False

        

    ##########################################################################
    #
    # preview
    #
    ##########################################################################

    def preview(self):
        
        dlg = PreviewItemDlg(unicode(self.question.text()),
                             unicode(self.answer.text()),
                             unicode(self.categories.currentText()),
                             self,"Preview current card",0)
        dlg.exec_loop()

        

    ##########################################################################
    #
    # apply
    #
    ##########################################################################
    
    def apply(self):

        new_cat_name = unicode(self.categories.currentText())

        if new_cat_name != self.item.cat.name:
            self.item.change_category(new_cat_name)   
        
        self.item.q  = unicode(self.question.text())
        self.item.a  = unicode(self.answer.text())

        self.accept()
