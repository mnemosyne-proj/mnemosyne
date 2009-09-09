#
# SQLite_criterion_applier.py - <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.activity_criterion import CriterionApplier
from mnemosyne.libmnemosyne.activity_criteria.default_criterion import \
     DefaultCriterion


class DefaultCriterionApplier(CriterionApplier):

    used_for = DefaultCriterion

    def apply_to_database(self, active_or_in_view):
        if active_or_in_view == self.ACTIVE:
            field_name = "active"
        elif active_or_in_view == self.IN_VIEW:
            field_name = "in_view"
        db = self.database()
        criterion = db.current_activity_criterion()
        # If every tag is required, take a short cut.
        if len(criterion.required_tags) == len(db.tag_names()):
            db.con.execute("update cards set active=1")
        else:     
            # Turn off everything.
            db.con.execute("update cards set active=0")
            # Turn on required tags.
            command = """update cards set %s=1 where _id in (select cards._id
                from cards, tags, tags_for_card where
                tags_for_card._card_id=cards._id and
                tags_for_card._tag_id=tags._id and """ % field_name
            args = []
            for tag in criterion.required_tags:
                command += "tags.id=? or "
                args.append(tag.id)
            command = command.rsplit("or ", 1)[0] + ")"
            if criterion.required_tags:
                db.con.execute(command, args)          
        # Turn off inactive card types and views.
        command = """update cards set %s=0 where _id in (select cards._id
            from cards, facts where cards._fact_id=facts._id and """ \
            % field_name
        args = []        
        for card_type, fact_view in criterion.inactive_card_types_fact_views:
            command += "not (cards.fact_view_id=? and facts.card_type_id=?)"
            command += " and "
            args.append(fact_view.id)  
            args.append(card_type.id)          
        command = command.rsplit("and ", 1)[0] + ")"
        if criterion.inactive_card_types_fact_views:
            db.con.execute(command, args)
        # Turn off forbidden tags.
        command = """update cards set %s=0 where _id in (select cards._id
            from cards, tags, tags_for_card where
            tags_for_card._card_id=cards._id and
            tags_for_card._tag_id=tags._id and """ % field_name       
        args = []
        for tag in criterion.forbidden_tags:
            command += "tags.id=? or "
            args.append(tag.id)
        command = command.rsplit("or ", 1)[0] + ")"
        if criterion.forbidden_tags:
            db.con.execute(command, args)
