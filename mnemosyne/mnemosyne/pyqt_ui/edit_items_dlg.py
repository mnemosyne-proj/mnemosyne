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
from change_category_dlg import *


##############################################################################
#
# ListItem
#
#   Note: first I thought the subclassing was the main culprit of the
#   slowdown, but testing shows that without it, it is just as slow.
#   A Qt4 based model/view construction seems like the only way out.
#
##############################################################################

class ListItem(QListViewItem):
    def __init__(self, parent, item):
        QListViewItem.__init__(self, parent, item.q, item.a, item.cat.name)

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
    
    def __init__(self, parent=None, name=None, modal=0):
        
        EditItemsFrm.__init__(self,parent,name,modal,
                              Qt.WStyle_MinMax | Qt.WStyle_SysMenu)
        
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
        self.popup_1.insertItem(self.trUtf8("&Edit"), self.edit, \
                                QKeySequence(self.trUtf8("Ctrl+E")))
        self.popup_1.insertItem(self.trUtf8("&Preview"), self.preview, \
                                QKeySequence(self.trUtf8("Ctrl+P")))
        self.popup_1.insertItem(self.trUtf8("&Add vice versa"), self.viceversa)
        self.popup_1.insertItem(self.trUtf8("S&tatistics"), self.statistics, \
                                QKeySequence(self.trUtf8("Ctrl+T")))
        self.popup_1.insertItem(self.trUtf8("&Delete"), self.delete, \
                                Qt.Key_Delete)
        
        self.popup_2 = QPopupMenu(self, "menu2")
        self.popup_2.insertItem(self.trUtf8("&Change category"),
                                self.change_category)
        self.popup_2.insertItem(self.trUtf8("&Add vice versa"), self.viceversa)
        self.popup_2.insertItem(self.trUtf8("&Delete"), self.delete)
        
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

        if get_config("column_0_width") != None:
            
            self.item_list.setColumnWidthMode(0, QListView.Manual)
            self.item_list.setColumnWidthMode(1, QListView.Manual)
            self.item_list.setColumnWidthMode(2, QListView.Manual)
            
            self.item_list.setColumnWidth(0, get_config("column_0_width"))
            self.item_list.setColumnWidth(1, get_config("column_1_width"))
            self.item_list.setColumnWidth(2, get_config("column_2_width"))

            self.item_list.setSortColumn(get_config("sort_column"))
            self.item_list.setSortOrder(\
                Qt.SortOrder(get_config("sort_order")))            
                        
        if get_config("list_font") != None:
            font = QFont()
            font.fromString(get_config("list_font"))
            self.to_find.setFont(font)
            self.item_list.setFont(font) # Takes a lot of time!

        parent.statusBar().clear()

    ##########################################################################
    #
    # cell_edited
    #
    ##########################################################################
    
    def cell_edited(self, list_item, col):

        list_item.item.q = unicode(list_item.text(0))
        list_item.item.a = unicode(list_item.text(1))
        list_item.item.change_category(unicode(list_item.text(2)))
            
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
        
        self.find_selected()
        if len(self.selected) == 0:
            return
        
        list_item = self.selected[0]
        dlg = EditItemDlg(list_item.item, self)
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
        
        self.find_selected()
        if len(self.selected) == 0:
            return
        
        item = self.selected[0].item
        dlg = PreviewItemDlg(item.q, item.a, item.cat.name, self)
        
        dlg.exec_loop()
        
    ##########################################################################
    #
    # viceversa
    #
    ##########################################################################
    
    def viceversa(self):
        
        self.find_selected()
        if len(self.selected) == 0:
            return
        
        if len(self.selected) > 1:
            message = self.trUtf8("Add vice versa of these cards?")
        else:
            message = self.trUtf8("Add vice versa of this card?")
            
        status = QMessageBox.warning(None,
            self.trUtf8("Mnemosyne"),
            message.append(self.trUtf8(\
             "\n\nThis could create duplicates if the vice "))\
            .append(self.trUtf8(\
             "versas are already present, \nso you might want to run "))\
            .append(self.trUtf8("clean duplicates' afterwards.")),
             self.trUtf8("&Yes"), self.trUtf8("&No"),
             QString(), 2, -1)
        
        if status == 1:
            return
        else:
            for list_item in self.selected:
                i = list_item.item
                new_list_item = add_new_item(i.grade,i.a,i.q,i.cat.name,\
                                             i.id+'.inv')
                ListItem(self.item_list, new_list_item)

    ##########################################################################
    #
    # statistics
    #
    ##########################################################################
    
    def statistics(self):
        
        self.find_selected()
        if len(self.selected) == 0:
            return
        
        item = self.selected[0].item

        message = QString()
        message.append(self.trUtf8("Grade:"))
        message.append(" " + QString(str(item.grade) + "\n"))
        
        message.append(self.trUtf8("Easiness:"))
        message.append(" " + QString("%1.2f" % item.easiness + "\n"))
        
        message.append(self.trUtf8("Repetitions:"))
        message.append(" " + QString(str(item.acq_reps+item.ret_reps) + "\n"))
        
        message.append(self.trUtf8("Lapses:"))
        message.append(" " + QString(str(item.lapses) + "\n"))
        
        message.append(self.trUtf8("Days since last repetition:"))
        message.append(" " + QString(str(item.days_since_last_rep()) + "\n"))
        
        message.append(self.trUtf8("Days until next repetition:"))
        message.append(" " + QString(str(item.days_until_next_rep()) + "\n"))
                
        QMessageBox.information(None, self.trUtf8("Mnemosyne"), message,
                                self.trUtf8("&OK"),QString(),QString(),0,-1)

    ##########################################################################
    #
    # delete
    #
    ##########################################################################
    
    def delete(self):

        self.find_selected()
        if len(self.selected) == 0:
            return
        
        if len(self.selected) > 1:
            message = self.trUtf8("Delete these cards?")
        else:
            message = self.trUtf8("Delete this card?")           
        
        status = QMessageBox.warning(None, self.trUtf8("Mnemosyne"),
                    message, self.trUtf8("&Yes"), self.trUtf8("&No"),
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
    # change_category
    #
    ##########################################################################
    
    def change_category(self):

        self.find_selected()
        if len(self.selected) == 0:
            return
        
        dlg = ChangeCategoryDlg(self.selected, self)
        dlg.exec_loop()     
        for list_item in self.selected:
            list_item.setText(2, list_item.item.cat.name)
            
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
            self.find_button.setText(self.trUtf8("&Find again"))
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
        if e.key() == Qt.Key_F3 or \
          (e.key() == QKeySequence(self.trUtf8("F")) and e.state() == \
                                                          Qt.ControlButton):
            self.find()
            
    ##########################################################################
    #
    # reset_find
    #
    ##########################################################################
    
    def reset_find(self):
        self.found_once = False
        self.last_search_str = None
        self.find_button.setText(self.trUtf8("&Find"))

    ##########################################################################
    #
    # closeEvent
    #
    ##########################################################################

    def closeEvent(self, event):

        set_config("column_0_width", self.item_list.columnWidth(0))
        set_config("column_1_width", self.item_list.columnWidth(1))
        set_config("column_2_width", self.item_list.columnWidth(2))

        set_config("sort_column", self.item_list.sortColumn())
        set_config("sort_order", int(self.item_list.sortOrder()))        
        
        event.accept()
        
