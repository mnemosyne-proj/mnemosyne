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


# Wrap it into a Plugin and then register the Plugin.

from mnemosyne.libmnemosyne.plugin import Plugin

class GradesActivityCriterionPlugin(Plugin):
    name = "Activity criterion example"
    description = "Example plugin for grade-based activity criteria."
    components = [MyHtmlStatistics]

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(GradesActivityCriterionPlugin)
