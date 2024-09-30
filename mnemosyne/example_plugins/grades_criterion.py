#
# grades_criterion.py <Peter.Bienstman@gmail.com>
#

# The criterion itself.

from mnemosyne.libmnemosyne.criterion import Criterion

class GradesCriterion(Criterion):

    """Only review cards with grade lower than or equal to 'threshold'."""

    criterion_type = "grades"

    def __init__(self, component_manager, id=None):
        Criterion.__init__(self, component_manager, id)
        self.threshold = 5

    def apply_to_card(self, card):
        card.active = (card.grade <= self.threshold)

    def data_to_string(self):
        return repr(self.threshold)

    def set_data_from_string(self, data):
        self.threshold = eval(data)


# The criterion applier.

from mnemosyne.libmnemosyne.criterion import CriterionApplier

class GradesCriterionApplier(CriterionApplier):

    used_for = GradesCriterion

    def apply_to_database(self, criterion):
        db = self.database()
        db.con.execute("update cards set active=0")
        db.con.execute("update cards set active=1 where grade<=?",
                       (criterion.threshold, ))


# The UI widget to set the threshold.

from mnemosyne.libmnemosyne.ui_components.criterion_widget \
     import CriterionWidget

from PyQt6 import QtCore, QtGui, QtWidgets

class GradesCriterionWdgt(QtWidgets.QWidget, CriterionWidget):

    used_for = GradesCriterion

    def __init__(self, **kwds):
        super().__init__(**kwds)    
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel("Activate cards with grade <=", self)
        self.horizontalLayout.addWidget(self.label)
        self.threshold = QtWidgets.QSpinBox(self)
        self.threshold.setMaximum(5)
        self.horizontalLayout.addWidget(self.threshold)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.parent_saved_sets = self.parent().saved_sets
        self.threshold.valueChanged.connect(self.criterion_changed)
        self.threshold.setValue(5)

    def display_criterion(self, criterion):
        self.threshold.setValue(criterion.threshold)

    def criterion(self):
        criterion = GradesCriterion(self.component_manager)
        criterion.threshold = self.threshold.value()
        return criterion

    def criterion_changed(self):
        self.parent_saved_sets.clearSelection()

# Wrap it into a Plugin and then register the Plugin.

from mnemosyne.libmnemosyne.plugin import Plugin

class GradesCriterionPlugin(Plugin):
    name = "Activity criterion example"
    description = "Example plugin for grade-based criterion."
    components = [GradesCriterion, GradesCriterionApplier, GradesCriterionWdgt]
    supported_API_level = 3

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(GradesCriterionPlugin)
