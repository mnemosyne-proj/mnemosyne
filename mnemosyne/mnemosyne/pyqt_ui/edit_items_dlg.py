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
        
        self.selected = []
        self.found_once = False
        self.last_search_str = None

        for e in get_items():
            ListItem(self.item_list, e)

        self.connect(self.item_list,
                     SIGNAL("itemRenamed(QListViewItem*,int)"),
                     self.cell_edited)

        self.popup_1 = QPopupMenu(self, "menu1")
        self.popup_1.insertItem(self.tr("&Edit"), self.edit)
        self.popup_1.insertItem(self.tr("&Preview"), self.preview)        
        self.popup_1.insertItem(self.tr("&Add vice versa"), self.viceversa)
        self.popup_1.insertItem(self.tr("&Delete"), self.delete)
        
        self.popup_2 = QPopupMenu(self, "menu2")
        self.popup_2.insertItem(self.tr("&Change category"), self.delete)
        self.popup_2.insertItem(self.tr("&Add vice versa"), self.viceversa)
        self.popup_2.insertItem(self.tr("&Delete"), self.delete)
        
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

        self.item_list.keyPressEvent = self.listView_keyPressEvent

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
    
    def cell_edited(self, list_item, col):

        list_item.item.q = unicode(list_item.text(0))
        list_item.item.a = unicode(list_item.text(1))
            
        old_cat_name = list_item.item.cat.name
        new_cat_name = unicode(list_item.text(2))
        
        if old_cat_name != new_cat_name:
            list_item.item.change_category(new_cat_name)
            
    ##########################################################################
    #
    # find_selected
    #
    ##########################################################################

    def find_selected(self):
    
        self.selected = []

        iter = QListViewItemIterator(self.item_list,
                                     QListViewItemIterator.Selected)
        
        while iter.current():
            self.selected.append(iter.current())
            iter += 1

    ##########################################################################
    #
    # show_popup
    #
    ##########################################################################
    
    def show_popup(self, list_item, point, i):

        self.find_selected()

        if len(self.selected) == 0:
            return
        elif len(self.selected) == 1:
            self.popup_1.popup(point)
        else:
            self.popup_2.popup(point)            
        
    ##########################################################################
    #
    # edit
    #
    ##########################################################################

    def edit(self):
        
        list_item = self.selected[0]
        dlg = EditItemDlg(list_item.item,self,"Edit current item",0)
        dlg.exec_loop()
        list_item.setText(0, list_item.item.q)
        list_item.setText(1, list_item.item.a)
        list_item.setText(2, list_item.item.cat.name)
        
    ##########################################################################
    #
    # preview
    #
    ##########################################################################

    def preview(self):
                
        item = self.selected[0].item
        dlg = PreviewItemDlg(item.q,item.a,item.cat.name,
                             self,"Preview current item",0)
        
        dlg.exec_loop()
        
    ##########################################################################
    #
    # viceversa
    #
    ##########################################################################
    
    def viceversa(self):
        
        status = QMessageBox.warning(None,
                    self.trUtf8("Mnemosyne"),
                    self.trUtf8("Add vice virsa of this item?"),
                    self.trUtf8("&Yes"), self.trUtf8("&No"),
                    QString(), 1, -1)
        if status == 1:
            return
        else:
            item = self.selected[0].item
            new_item = add_new_item(i.grade, i.a, i.q, i.cat.name)
            ListItem(self.item_list, new_item)

    ##########################################################################
    #
    # delete
    #
    ##########################################################################
    
    def delete(self):

        if len(self.selected) > 1:
            message = "Delete these items?"
        else:
            message = "Delete this item?"            
        
        status = QMessageBox.warning(None,
                    self.trUtf8("Mnemosyne"),
                    self.trUtf8(message),
                    self.trUtf8("&Yes"), self.trUtf8("&No"),
                    QString(), 1, -1)
        if status == 1:
            return
        else:
            for list_item in self.selected:
                delete_item(list_item.item)
                self.item_list.takeItem(list_item)
            self.selected = []

       
    ##########################################################################
    #
    # find
    #
    ##########################################################################
    
    def find(self):

        # If this is a new search, check if the item is present at all.

        to_find = self.to_find.text()

        if len(to_find) == 0:
            return
        
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
            self.item_list.setFocus()
            self.item_list.clearSelection()
            self.item_list.ensureItemVisible(f)
            self.item_list.setSelected(f, 1)
            self.item_list.setCurrentItem(f)
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
            
    ##########################################################################
    #
    # listView_keyPressEvent
    #
    ##########################################################################
    
    def listView_keyPressEvent(self, e):
        if e.key() == Qt.Key_Delete:
            self.find_selected()
            if len(self.selected) == 0:
                return
            else:
                self.delete()         
        else:
            QListView.keyPressEvent(self.item_list, e)
            
    ##########################################################################
    #
    # reset_find
    #
    ##########################################################################
    
    def reset_find(self):
        self.found_once = False
        self.last_search_str = None
        self.find_button.setText("&Find")
        
