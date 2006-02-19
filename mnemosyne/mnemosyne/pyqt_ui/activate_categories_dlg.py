##############################################################################
#
# Widget to activate categories <Peter.Bienstman@UGent.be>
#
##############################################################################

from qt import *

from mnemosyne.core import *
from activate_categories_frm import *



##############################################################################
#
# ActivateCategoriesDlg
#
##############################################################################

class ActivateCategoriesDlg(ActivateCategoriesFrm):
    
    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, parent=None, name=None, modal=0, fl=0):
        
        ActivateCategoriesFrm.__init__(self,parent,name,modal,fl)

        for cat in get_categories():
            c = QListBoxText(self.cat_list, cat.name)
            self.cat_list.setSelected(c, cat.active)
        self.cat_list.sort()
        
        self.connect(self.button_none, SIGNAL("clicked()"),
                     self.activate_none)
        self.connect(self.button_all, SIGNAL("clicked()"),
                     self.activate_all)
        self.connect(self.button_ok, SIGNAL("clicked()"),
                     self.apply)
        
    ##########################################################################
    #
    # activate_none
    #
    ##########################################################################
    
    def activate_none(self):
        
        item = self.cat_list.firstItem()
        while item != None:
            self.cat_list.setSelected(item, 0)
            item = item.next()
            
    ##########################################################################
    #
    # activate_all
    #
    ##########################################################################
    
    def activate_all(self):
        
        item = self.cat_list.firstItem()
        while item != None:
            self.cat_list.setSelected(item, 1)
            item = item.next()
            
    ##########################################################################
    #
    # apply
    #
    ##########################################################################

    def apply(self):

        item = self.cat_list.firstItem()
        while item != None:
            if item.isSelected() == True:
                get_category_by_name(unicode(item.text())).active = True
            else:
                get_category_by_name(unicode(item.text())).active = False
            item = item.next()

        self.close()
        
