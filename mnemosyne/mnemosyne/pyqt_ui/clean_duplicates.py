##############################################################################
#
# Duplicate checking Jarno Elonen <elonen@iki.fi>, <Peter.Bienstman@UGent.be>
#
##############################################################################

from qt import *
from edit_item_dlg import *
from mnemosyne.core import *


##########################################################################
#
# clean_duplicates
#
##########################################################################

def clean_duplicates(self):

    # Build a dictionary of format 'question':[item, item, ...]
    
    allow_dif_cat = get_config("allow_duplicates_in_diff_cat")
    
    items_for_question = {}
    for item in get_items():
        key = item.q
        if allow_dif_cat:
            key = (item.cat.name, item.q)
        if not key in items_for_question:
            items_for_question[key] = []
        items_for_question[key].append(item)

    self.statusBar().clear()

    # Filter out duplicate items.

    n_removed = 0   
    for q, itemlist in items_for_question.iteritems():
        if len(itemlist) > 1:

            # Make sure we keep the oldest copy.
            
            itemlist.sort(key=Item.sort_key_newest, reverse=True)
            
            old_len = len(itemlist)
            for j in range(old_len-1):
                if j < len(itemlist):
                    i1 = itemlist[j]
                    new_itemlist = []
                    for i in itemlist:
                        if i is i1 or i.a != i1.a:
                            new_itemlist.append(i)
                        else:
                            delete_item(i)
                            n_removed += 1
                    itemlist = new_itemlist
            items_for_question[q] = itemlist

    showed_box = False
    if n_removed > 0:
        QMessageBox.information(None, self.trUtf8("Mnemosyne"),
            self.trUtf8("Removed duplicates: ").\
                        append(QString(str(n_removed))),
            self.trUtf8("&OK"))
        showed_box = True

    # Ask about different answers for same question and merge if the
    # user wishes so.
    
    for q, itemlist in items_for_question.iteritems():
        
        if len(itemlist) > 1:
                
            status = QMessageBox.question(None, self.trUtf8("Mnemosyne"),
                self.trUtf8(\
                 "There are cards with different answers for question:\n\n").\
                 append(QString(itemlist[0].q)),
                self.trUtf8("&Merge and edit"),
                self.trUtf8("&Don't merge"),
                QString(), 0, -1)

            showed_box = True
            
            if status == 0: # Merge and edit.
                new_item = itemlist[0]
                delete_item(itemlist[0])
                for i in itemlist[1:]:
                    new_item.gr = min(new_item.grade, i.grade)
                    new_item.a += ' / ' + i.a
                    delete_item(i)
                new_item = add_new_item(new_item.grade, new_item.q,
                                        new_item.a, new_item.cat.name)
                dlg = EditItemDlg(new_item, self)
                dlg.exec_loop()


    # Finished.

    if showed_box == False:
        QMessageBox.information(None, self.trUtf8("Mnemosyne"),
                                self.trUtf8("Done!"), self.trUtf8("&OK"))
    
