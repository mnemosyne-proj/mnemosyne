#
# SQLite_criterion_applier.py - <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.activity_criterion import CriterionApplier
from mnemosyne.libmnemosyne.activity_criteria.default_criterion import \
     DefaultCriterion


class DefaultCriterionApplier(CriterionApplier):

    used_for = DefaultCriterion

    def apply_to_database(self, criterion, active_or_in_view):
        if active_or_in_view == self.ACTIVE:
            field_name = "active"
        elif active_or_in_view == self.IN_VIEW:
            field_name = "in_view"
        db = self.database()
        # If every tag is required, take a short cut.
        tag_count = db.con.execute("select count() from tags").fetchone()[0]
        if len(criterion.required_tags) == tag_count:
            db.con.execute("update cards set active=1")
        else:     
            # Turn off everything.
            db.con.execute("update cards set active=0")
            # Turn on required tags.
            command = """update cards set %s=1 where _id in (select _card_id
                from tags_for_card where """ % field_name
            args = []
            for tag in criterion.required_tags:
                command += "_tag_id=? or "
                args.append(tag._id)
            command = command.rsplit("or ", 1)[0] + ")"
            if criterion.required_tags:
                db.con.execute(command, args)          
        # Turn off inactive card types and views.
        command = """update cards set %s=0 where _id in (select cards._id
            from cards, facts where cards._fact_id=facts._id and (""" \
            % field_name
        args = []        
        for card_type, fact_view in \
                criterion.deactivated_card_type_fact_views:
            command += "(cards.fact_view_id=? and facts.card_type_id=?)"
            command += " or "
            args.append(fact_view.id)  
            args.append(card_type.id)          
        command = command.rsplit("or ", 1)[0] + "))"
        if criterion.deactivated_card_type_fact_views:
            db.con.execute(command, args)
        # Turn off forbidden tags.
        command = """update cards set %s=0 where _id in (select _card_id
            from tags_for_card where """  % field_name       
        args = []
        for tag in criterion.forbidden_tags:
            command += "_tag_id=? or "
            args.append(tag._id)
        command = command.rsplit("or ", 1)[0] + ")"
        if criterion.forbidden_tags:
            db.con.execute(command, args)
