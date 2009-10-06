#
# grades_activity_criterion.py <Peter.Bienstman@UGent.be>
#

# The criterion itself.

from mnemosyne.libmnemosyne.activity_criterion import ActivityCriterion

class GradesCriterion(ActivityCriterion):

    """Only review cards with grade lower than or equal to 'threshold'."""

    criterion_type = "Grades"

    def __init__(self, component_manager, id=None):
        ActivityCriterion.__init__(self, component_manager, id)
        self.threshold = 5
        
    def apply_to_card(self, card):
        card.active = (card.grade <= self.threshold)

    def data_to_string(self):
        return repr(self.threshold)
    
    def data_from_string(self, data):
        self.threshold = eval(data)


# The criterion applier.

from mnemosyne.libmnemosyne.activity_criterion import CriterionApplier

class GradesCriterionApplier(CriterionApplier):

    used_for = GradesCriterion

    def apply_to_database(self, criterion, active_or_in_view):
        if active_or_in_view == self.ACTIVE:
            field_name = "active"
        elif active_or_in_view == self.IN_VIEW:
            field_name = "in_view"
        db = self.database()
        db.con.execute("update cards set %s=0" % field_name)
        db.con.execute("update cards set %s=1 where grade<=?" % field_name,
                       (self.threshold, ))


# The UI widget to set the threshold.

from mnemosyne.libmnemosyne.ui_components.activity_criterion_widget \
     import ActivityCriterionWidget

from PyQt4 import QtCore, QtGui

class GradesCriterionWdgt(QtGui.QDialog, ActivityCriterionWidget)

    used_for = GradesCriterion

    def __init__(self, component_manager, parent):
        ActivityCriterionWidget.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, parent)        
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.label = QtGui.QLabel("Activate cards with grade <=", self)
        self.horizontalLayout.addWidget(self.label)
        self.threshold = QtGui.QSpinBox(self)
        self.threshold.setMaximum(5)
        self.horizontalLayout.addWidget(self.threshold)
        self.verticalLayout.addLayout(self.horizontalLayout)

    def display_criterion(self, criterion):
        self.threshold.setValue(criterion.threshold)

    def get_criterion(self):
        criterion = GradesCriterion()
        criterion.threshold = shelf.threshold.value()
        return criterion


# Wrap it into a Plugin and then register the Plugin.

from mnemosyne.libmnemosyne.plugin import Plugin

class GradesActivityCriterionPlugin(Plugin):
    name = "Activity criterion example"
    description = "Example plugin for grade-based activity criteria."
    components = [GradesCriterion, GradesCriterionApplier, GradesCriterionWdgt]

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(GradesActivityCriterionPlugin)

