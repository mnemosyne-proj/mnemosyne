#
# add_cards_dlg.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from mnemosyne.libmnemosyne.category import *
from ui_add_cards_dlg import *

from mnemosyne.libmnemosyne.card_type import *
from mnemosyne.libmnemosyne.config import config
from mnemosyne.libmnemosyne.component_manager import *

from mnemosyne.pyqt_ui.generic_card_type_widget import GenericCardTypeWdgt


class AddCardsDlg(QDialog, Ui_AddCardsDlg):

    def __init__(self, filename, parent = None):
        QDialog.__init__(self, parent)

        # TODO: modal, Qt.WStyle_MinMax | Qt.WStyle_SysMenu))?

        self.setupUi(self)

        # We calculate card_type_by_name here rather than in the component
        # manager, because these names can change if the user chooses another
        # translation. TODO: test.

        for card_type in get_card_types():
            self.card_types.addItem(card_type.name)
            self.card_type_by_name[card_type.name] = card_type

        # TODO: sort card types by id.

        # TODO: remember last type.

        self.card_widget = None

        self.update_card_widget()

        self.update_combobox(config["last_add_category"])

        self.grades = QButtonGroup()

        self.grades.addButton(self.grade_0_button, 0)
        self.grades.addButton(self.grade_1_button, 1)
        self.grades.addButton(self.grade_2_button, 2)
        self.grades.addButton(self.grade_3_button, 3)
        self.grades.addButton(self.grade_4_button, 4)
        self.grades.addButton(self.grade_5_button, 5)

        self.connect(self.grades, SIGNAL("buttonClicked(int)"),
                     self.new_cards)

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

    def update_card_widget(self):
        if self.card_widget:
            self.vboxlayout.removeWidget(self.card_widget)
            self.card_widget.close()

        card_type_name = unicode(self.card_types.currentText())
        card_type = get_card_type_by_name(card_type_name)

        if card_type.widget == None:
            try:
                card_type.widget =  component_manager.\
                   get_current("card_type_widget",
                               used_for=card_type.__class__.__name__)()
            except KeyError:
                card_type.widget = GenericCardTypeWdgt(card_type)

        self.card_widget = card_type.widget
        self.card_widget.show()

        self.vboxlayout.insertWidget(1, self.card_widget)

        #self.adjustSize()

    def update_combobox(self, current_cat_name):
        no_of_categories = self.categories.count()
        for i in range(no_of_categories-1,-1,-1):
            self.categories.removeItem(i)

        self.categories.addItem(_("<default>"))
        for name in get_database().category_names():
            if name != _("<default>"):
                self.categories.addItem(name)

        for i in range(self.categories.count()):
            if self.categories.itemText(i) == current_cat_name:
                self.categories.setCurrentIndex(i)
                break

    def new_cards(self, grade):

        """Note that we don't rebuild revision queue afterwards, as this can
        cause corruption for the current card.  The new cards will show up
        after the old queue is empty."""

        fact_data = self.card_widget.get_data()

        if fact_data is None:
            return

        cat_names = [unicode(self.categories.currentText())]

        # Create the new cards.

        card_type_name = unicode(self.card_types.currentText())

        card_type = get_card_type_by_name(card_type_name)

        card_type.create_new_cards(fact_data, grade, cat_names)

        get_database().save(config['path'])

        # Update widget. TODO

        #self.question.setFocus()

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

    def preview(self):
        raise NotImplementedError()


