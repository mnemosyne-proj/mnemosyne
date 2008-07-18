##############################################################################
#
# Widget to add new items <Peter.Bienstman@UGent.be>
# Duplicate check by Jarno Elonen <elonen@iki.fi>
#
##############################################################################

import gettext
_ = gettext.gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *


#from mnemosyne.libmnemosyne.mnemosyne_core import *
from mnemosyne.libmnemosyne.category import *
from ui_add_cards_dlg import *
#from edit_item_dlg import *
from mnemosyne.libmnemosyne.card_type import *
from mnemosyne.libmnemosyne.config import *

# TODO: import them all at once
import mnemosyne.libmnemosyne.card_types.two_sided
import mnemosyne.libmnemosyne.card_types.three_sided
from card_twosided_wdgt import *
from card_threesided_wdgt import *


##############################################################################
#
# AddCardsDlg
#
##############################################################################

class AddCardsDlg(QDialog, Ui_AddCardsDlg):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, filename, parent = None):
        
        QDialog.__init__(self, parent)

        # TODO: modal, Qt.WStyle_MinMax | Qt.WStyle_SysMenu))?
        
        self.setupUi(self)

        self.card_type_by_name = {} # TODO: move to lib?
        
        for card_type in get_card_types().values():
            self.card_types.addItem(card_type.name)
            self.card_type_by_name[card_type.name] = card_type
               
        # TODO: remember last type

        self.card_widget = None

        self.update_card_widget()
        
        self.update_combobox(get_config("last_add_category"))

        self.grades = QButtonGroup()

        self.grades.addButton(self.grade_0_button, 0)
        self.grades.addButton(self.grade_1_button, 1)
        self.grades.addButton(self.grade_2_button, 2)
        self.grades.addButton(self.grade_3_button, 3)
        self.grades.addButton(self.grade_4_button, 4)
        self.grades.addButton(self.grade_5_button, 5)
        
        self.connect(self.grades, SIGNAL("buttonClicked(int)"),
                     self.new_card)
        
        #self.connect(self.preview_button, SIGNAL("clicked()"),
        #             self.preview)


        # TODO: fonts?
        
        #if get_config("QA_font") != None:
        #    font = QFont()
        #    font.fromString(get_config("QA_font"))
        #    self.question.setFont(font)
        #    self.pronunciation.setFont(font)
        #    self.answer.setFont(font)
        #self.categories.setFont(font)

        
            
    ##########################################################################
    #
    # update_card_widget
    #
    ##########################################################################       

    def update_card_widget(self):

        if self.card_widget:
            self.vboxlayout.removeWidget(self.card_widget)
            self.card_widget.close()
            del self.card_widget

        card_type_name = unicode(self.card_types.currentText())
        card_type = self.card_type_by_name[card_type_name]
        self.card_widget = card_type.widget_class()
        card_type.set_widget(self.card_widget)
        self.vboxlayout.insertWidget(1, self.card_widget)

        #self.adjustSize()



    ##########################################################################
    #
    # update_combobox
    #
    ##########################################################################

    def update_combobox(self, current_cat_name):

        no_of_categories = self.categories.count()
        for i in range(no_of_categories-1,-1,-1):
            self.categories.removeItem(i)

        self.categories.addItem(self.trUtf8("<default>"))
        for name in get_category_names():
            if name != self.trUtf8("<default>"):
                self.categories.addItem(name)

        for i in range(self.categories.count()):
            if self.categories.itemText(i) == current_cat_name:
                self.categories.setCurrentIndex(i)
                break


    ##########################################################################
    #
    # new_card
    #
    #   Don't rebuild revision queue afterwards, as this can cause corruption
    #   for the current card. The new cards will show up after the old queue
    #   is empty.
    #
    ##########################################################################
    
    def new_card(self, grade):

        # Get data from the card wiget.
        
        data = self.card_widget.get_data()
        
        if data is None:
            return

        # Add our own data. The card model can later remove these.

        data['grade'] = grade

        data['cat_names'] = [unicode(self.categories.currentText())]

        # Create the new cards.

        card_type_name = unicode(self.card_types.currentText())

        card_type = self.card_type_by_name[card_type_name]

        card_type.new_cards(data)

        # Update widget. TODO 
                        
        #self.question.setFocus()

        #set_config("last_add_vice_versa", self.addViceVersa.isOn())
        #set_config("last_add_category",   cat_name)

        #save_database(get_config("path"))


            
    ##########################################################################
    #
    # reject
    #
    ##########################################################################
    
    def reject(self):

        if self.card_widget.get_data() is None:
            QDialog.reject(self)
            return

        status = QMessageBox.warning(None, _("Mnemosyne"),
                                     _("Abandon current card?"),
                                     _("&Yes"), _("&No"),
                                     "", 1, -1)
        if status == 0:
            QDialog.reject(self)
            return
        else:
            return




    ##########################################################################
    #
    # preview
    #
    ##########################################################################

    def preview(self):

        raise NotImplementedError()

        if get_config("3_sided_input") == False:
        
            dlg = PreviewItemDlg(unicode(self.question.text()),
                                 unicode(self.answer.text()),
                                 unicode(self.categories.currentText()),
                                 self)
        else:
            dlg = PreviewItemDlg(unicode(self.question.text()),
                                 unicode(QString(self.pronunciation.text()).\
                                         append(QString("\n")).\
                                         append(QString(self.answer.text()))),
                                 unicode(self.categories.currentText()),
                                 self)            
        dlg.exec_loop()

