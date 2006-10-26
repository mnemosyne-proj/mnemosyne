##############################################################################
#
# Widget to change category <Peter.Bienstman@UGent.be>
#
##############################################################################

from qt import *
from mnemosyne.core import *
from change_category_frm import *


    
##############################################################################
#
# ChangeCategoryDlg
#
##############################################################################

class ChangeCategoryDlg(ChangeCategoryFrm):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, items, parent=None, name=None, modal=0, fl=0):
        
        ChangeCategoryFrm.__init__(self,parent,name,modal,fl)
        
        self.items = items

        self.categories.insertItem(self.items[0].item.cat.name)

        names = [cat.name for cat in get_categories()]
        names.sort()
        for name in names:
            if name != self.items[0].item.cat.name:
                self.categories.insertItem(name)
          
        self.connect(self.ok_button, SIGNAL("clicked()"), self.apply)       

    ##########################################################################
    #
    # apply
    #
    ##########################################################################
    
    def apply(self):

        new_cat_name = unicode(self.categories.currentText())
        
        for list_item in self.items:
            list_item.item.change_category(new_cat_name)

        self.accept()
