#
# SQLite_criterion_applier.py - <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.criterion import CriterionApplier
from mnemosyne.libmnemosyne.criteria.default_criterion import DefaultCriterion


class DefaultCriterionApplier(CriterionApplier):

    used_for = DefaultCriterion

    def apply_to_database(self, criterion):
        if len(criterion._tag_ids_forbidden) != 0:
            assert len(criterion._tag_ids_active) != 0
        db = self.database()
        # If every tag is active, take a shortcut.
        tag_count = db.con.execute("select count() from tags").fetchone()[0]
        if len(criterion._tag_ids_active) == tag_count:
            db.con.execute("update cards set active=1")
        else:
            # Turn off everything.
            db.con.execute("update cards set active=0")
            # Turn on active tags.
            command = """update cards set active=1 where _id in
                (select _card_id from tags_for_card where _tag_id in ("""
            args = []
            for _tag_id in criterion._tag_ids_active:
                command += "?,"
                args.append(_tag_id)
            command = command.rsplit(",", 1)[0] + "))"
            if criterion._tag_ids_active:
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
            from tags_for_card where _tag_id in ("""
        args = []
        for _tag_id in criterion._tag_ids_forbidden:
            command += "?,"
            args.append(_tag_id)
        command = command.rsplit(",", 1)[0] + "))"
        if criterion._tag_ids_forbidden:
            db.con.execute(command, args)
