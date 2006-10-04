##############################################################################
#
# Widget to edit items
#
# <Peter.Bienstman@UGent.be>, Jarno Elonen <elonen@iki.fi>
#
##############################################################################

from qt import *
from mnemosyne.core import *
from edit_items_frm import *
from edit_item_dlg import *
from preview_item_dlg import *


##############################################################################
#
# ListItem
#
##############################################################################

class ListItem(QListViewItem):
    def __init__(self, parent, item):
        QListViewItem.__init__(self,parent, item.q, item.a, item.cat.name)

        self.item = item
        
        self.setMultiLinesEnabled(1)
        self.setRenameEnabled(0, 1)
        self.setRenameEnabled(1, 1)
        self.setRenameEnabled(2, 1)


    
##############################################################################
#
# EditItemsDlg
#
##############################################################################

class EditItemsDlg(EditItemsFrm):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, parent=None, name=None, modal=0, fl=0):
        
        EditItemsFrm.__init__(self,parent,name,modal,fl)

        parent.statusBar().message("Please wait...")
        
        self.popup_item = None
        self.found_once = False
        self.last_search_str = None

        for e in get_items():
            ListItem(self.item_list, e)

        self.connect(self.item_list,
                     SIGNAL("itemRenamed(QListViewItem*,int)"),
                     self.cell_edited)

        self.popup = QPopupMenu(self, "menu")
        self.popup.insertItem(self.tr("&Edit"), self.edit)
        self.popup.insertItem(self.tr("&Preview"), self.preview)        
        self.popup.insertItem(self.tr("&Add vice versa"), self.viceversa)
        self.popup.insertItem(self.tr("&Delete"), self.delete)
        
        self.connect(self.item_list,
          SIGNAL("contextMenuRequested(QListViewItem*,const QPoint&,int)"),
          self.show_popup)
        
        self.connect(self.to_find, SIGNAL("returnPressed()"),
                     self.find)
        self.connect(self.to_find, SIGNAL("textChanged(const QString&)"),
                     self.reset_find)
        self.connect(self.find_button, SIGNAL("clicked()"),
                     self.find)
        self.connect(self.close_button, SIGNAL("clicked()"),
                     self.close)

        if get_config("list_font") != None:
            font = QFont()
            font.fromString(get_config("list_font"))
            self.to_find.setFont(font)
            self.item_list.setFont(font)

        parent.statusBar().clear()

    ##########################################################################
    #
    # cell_edited
    #
    ##########################################################################
    
    def cell_edited(self, item, col):

        item.item.q  = unicode(item.text(0))
        item.item.a  = unicode(item.text(1))
            
        old_cat_name = item.item.cat.name
        new_cat_name = unicode(item.text(2))
        
        if old_cat_name != new_cat_name:
            item.item.change_category(new_cat_name)

    ##########################################################################
    #
    # show_popup
    #
    ##########################################################################
    
    def show_popup(self,item,point,i):
        self.popup_item = item
        self.popup.popup(point)
        
    ##########################################################################
    #
    # edit
    #
    ##########################################################################

    def edit(self):
        
        if self.popup_item == None:
            return
        
        item = self.popup_item.item
        dlg = EditItemDlg(item,self,"Edit current item",0)
        dlg.exec_loop()
        self.popup_item.setText(0, item.q)
        self.popup_item.setText(1, item.a)
        self.popup_item.setText(2, item.cat.name)
        
    ##########################################################################
    #
    # preview
    #
    ##########################################################################

    def preview(self):
        
        if self.popup_item == None:
            return
        
        item = self.popup_item.item
        dlg = PreviewItemDlg(item.q,item.a,item.cat.name,
                             self,"Preview current item",0)
        
        dlg.exec_loop()
        
    ##########################################################################
    #
    # viceversa
    #
    ##########################################################################
    
    def viceversa(self):

        if self.popup_item == None:
            return
        
        status = QMessageBox.warning(None,
                    self.trUtf8("Mnemosyne"),
                    self.trUtf8("Add vice virsa of this item?"),
                    self.trUtf8("&Yes"), self.trUtf8("&No"),
                    QString(), 1, -1)
        if status == 1:
            return
        else:
            i = self.popup_item.item
            new_item = add_new_item(i.grade, i.a, i.q, i.cat.name)
            ListItem(self.item_list, new_item)

    ##########################################################################
    #
    # delete
    #
    ##########################################################################
    
    def delete(self):

        if self.popup_item == None:
            return
        
        status = QMessageBox.warning(None,
                    self.trUtf8("Mnemosyne"),
                    self.trUtf8("Delete this item?"),
                    self.trUtf8("&Yes"), self.trUtf8("&No"),
                    QString(), 1, -1)
        if status == 1:
            return
        else:
            delete_item(self.popup_item.item)
            self.item_list.takeItem(self.popup_item)
            self.popup_item = None

       
    ##########################################################################
    #
    # find
    #
    ##########################################################################
    
    def find(self):

        # If this is a new search, check if the item is present at all.

        to_find = self.to_find.text()
        
        if self.to_find.text() != self.last_search_str:
            
            self.last_search_str = to_find
            
            iter = QListViewItemIterator(self.item_list)
            f = None
            while iter.current():
                if iter.current().text(0).find(to_find, 0, False) >= 0 or \
                   iter.current().text(1).find(to_find, 0, False) >= 0:
                    f = iter.current()
                    break
                iter += 1            

            if f == None:
                QMessageBox.critical(None,
                   self.trUtf8("Mnemosyne"),
                   self.trUtf8("The text you entered was not found."),
                   self.trUtf8("&OK"), QString(), QString(), 0, -1)
                self.last_search_str = None
                return
            else:
                self.found_once = True

        # Now, search either from the current selection or if nothing is
        # selected, from the beginning.
            
        iter     = QListViewItemIterator(self.item_list)   
        sel_iter = QListViewItemIterator(self.item_list,
                                         QListViewItemIterator.Selected)
        if sel_iter.current():
            next  = QListViewItemIterator(sel_iter.current())
            next += 1
            if next.current():
                iter = next

        f = None
        while iter.current():
            if iter.current().text(0).find(to_find, 0, False) >= 0 or \
               iter.current().text(1).find(to_find, 0, False) >= 0:
                f = iter.current()
                break
            iter += 1
                                    
        if f:
            self.find_button.setText("&Find again")
            self.item_list.setSelected(f, 1)
            self.item_list.ensureItemVisible(f)
            self.item_list.setFocus()
        elif self.found_once == True: # Wrap search.
            # Prevent infinite recursion in case the item was deleted by now.
            self.last_search_str = None
            self.item_list.clearSelection()
            self.find()
                    
    ##########################################################################
    #
    # keyPressEvent
    #
    ##########################################################################
    
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_F3:
            self.find()
            e.accept()
        else:
            e.ignore()

    ##########################################################################
    #
    # reset_find
    #
    ##########################################################################
    
    def reset_find(self):
        self.found_once = False
        self.last_search_str = None
        self.find_button.setText("&Find")
        
