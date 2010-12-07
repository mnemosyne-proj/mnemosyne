#
# SQLite_criterion_applier.py - <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.criterion import CriterionApplier
from mnemosyne.libmnemosyne.criteria.default_criterion import DefaultCriterion


class DefaultCriterionApplier(CriterionApplier):

    used_for = DefaultCriterion

    def apply_to_database(self, criterion):
        db = self.database()
        # If every tag is active, take a shortcut.
        tag_count = db.con.execute("select count() from tags").fetchone()[0]
        if len(criterion.active_tag__ids) == tag_count:
            db.con.execute("update cards set active=1")
        else:     
            # Turn off everything.
            db.con.execute("update cards set active=0")
            # Turn on active tags.
            command = """update cards set active=1 where _id in
                (select _card_id from tags_for_card where """
            args = []
            for _tag_id in criterion.active_tag__ids:
                command += "_tag_id=? or "
                args.append(_tag_id)
            command = command.rsplit("or ", 1)[0] + ")"
            if criterion.active_tag__ids:
                db.con.execute(command, args)          
        # Turn off inactive card types and views.
        command = "update cards set active=0 where "
        args = []        
        for card_type_id, fact_view_id in \
                criterion.deactivated_card_type_fact_view_ids:
            command += "(cards.fact_view_id=? and cards.card_type_id=?)"
            command += " or "
            args.append(fact_view_id)  
            args.append(card_type_id)          
        command = command.rsplit("or ", 1)[0]
        if criterion.deactivated_card_type_fact_view_ids:
            db.con.execute(command, args)
        # Turn off forbidden tags.
        command = """update cards set active=0 where _id in (select _card_id
            from tags_for_card where """       
        args = []
        for _tag_id in criterion.forbidden_tag__ids:
            command += "_tag_id=? or "
            args.append(_tag_id)
        command = command.rsplit("or ", 1)[0] + ")"
        if criterion.forbidden_tag__ids:
            db.con.execute(command, args)
