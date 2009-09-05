#
# SQLite_criterion_applier.py - <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.activity_criterion import CriterionApplier
from mnemosyne.libmnemosyne.activity_criteria.default_criterion import \
     DefaultCriterion


class DefaultCriterionApplier(CriterionApplier):

    def apply_to_database(self):
        db = self.database()
        # Turn off everything.
        db.con.execute("update cards set active=0")
        # Turn on as soon as there is one active tag.
        command = """update cards set %s=1 where _id in (select cards._id
            from cards, tags, tags_for_card where
            tags_for_card._card_id=cards._id and
            tags_for_card._tag_id=tags._id and """ % attr
        args = []
        for tag in tags:
            command += "tags.id=? or "
            args.append(tag.id)
        command = command.rsplit("or ", 1)[0] + ")"
        db.con.execute(command, args)
        # Turn off inactive card types and views.
        command = """update cards set %s=0 where _id in (select cards._id
            from cards, facts where cards._fact_id=facts._id and """ % attr
        args = []        
        for card_type, fact_view in card_types_fact_views:
            command += "not (cards.fact_view_id=? and facts.card_type_id=?)"
            command += " and "
            args.append(fact_view.id)  
            args.append(card_type.id)          
        command = command.rsplit("and ", 1)[0] + ")"
        db.con.execute(command, args)
