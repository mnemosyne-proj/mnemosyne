#
# criterion_wdgt_default.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.ui_components.criterion_widget \
     import CriterionWidget
from mnemosyne.libmnemosyne.criteria.default_criterion import DefaultCriterion
from mnemosyne.pyqt_ui.tag_tree_wdgt import TagsTreeWdgt
from mnemosyne.pyqt_ui.card_type_tree_wdgt import CardTypesTreeWdgt
from mnemosyne.pyqt_ui.ui_criterion_wdgt_default import Ui_DefaultCriterionWdgt


class DefaultCriterionWdgt(QtWidgets.QWidget, CriterionWidget,
                           Ui_DefaultCriterionWdgt):

    """Note that this dialog can support active tags and forbidden tags,
    but not at the same time, in order to keep the interface compact.

    """

    used_for = DefaultCriterion

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.parent = kwds["parent"]
        component_manager = kwds["component_manager"]
        self.setupUi(self)
        self.card_type_tree_wdgt = CardTypesTreeWdgt(\
            component_manager=component_manager, parent=self)
        # Bug in Qt: need to explicitly reset the text of this label.
        self.label.setText(_("Activate cards from these card types:"))
        self.gridLayout.addWidget(self.card_type_tree_wdgt, 1, 0)
        self.tag_tree_wdgt = TagsTreeWdgt(\
            component_manager=component_manager, parent=self)
        self.gridLayout.addWidget(self.tag_tree_wdgt, 1, 1)

        criterion = DefaultCriterion(component_manager=self.component_manager)
        for tag in self.database().tags():
            criterion._tag_ids_active.add(tag._id)
        self.display_criterion(criterion)
        self.card_type_tree_wdgt.tree_wdgt.\
            itemChanged.connect(self.criterion_changed)
        self.tag_tree_wdgt.tree_wdgt.\
            itemChanged.connect(self.criterion_changed)
        self.card_type_tree_wdgt.tree_wdgt.\
            itemClicked.connect(self.criterion_clicked)
        self.tag_tree_wdgt.tree_wdgt.\
            itemClicked.connect(self.criterion_clicked)

    def display_criterion(self, criterion):
        self.card_type_tree_wdgt.display(criterion)
        self.tag_tree_wdgt.display(criterion)
        if len(criterion._tag_ids_forbidden):
            self.active_or_forbidden.setCurrentIndex(1)
        else:
            self.active_or_forbidden.setCurrentIndex(0)

    def criterion(self):

        """Build the criterion from the information the user entered in the
        widget.

        """

        criterion = DefaultCriterion(component_manager=self.component_manager)
        criterion = self.card_type_tree_wdgt.checked_to_criterion(criterion)
        # Tag tree contains active tags.
        if self.active_or_forbidden.currentIndex() == 0:
            self.tag_tree_wdgt.checked_to_active_tags_in_criterion(criterion)
        # Tag tree contains forbidden tags.
        else:
            self.tag_tree_wdgt.\
                checked_to_forbidden_tags_in_criterion(criterion)
            for tag in self.database().tags():
                criterion._tag_ids_active.add(tag._id)
        return criterion

    def criterion_clicked(self):
        if self.parent.was_showing_a_saved_set and not self.parent.is_shutting_down:
            self.main_widget().show_information(\
_("Cards you (de)activate now will not be stored in the previously selected set unless you click 'Save this set for later use' again. This allows you to make some quick-and-dirty modifications."))
            self.parent.was_showing_a_saved_set = False

    def criterion_changed(self):
        self.parent.saved_sets.clearSelection()

    def closeEvent(self, event):
        # This allows the state of the tag tree to be saved.
        self.tag_tree_wdgt.close()