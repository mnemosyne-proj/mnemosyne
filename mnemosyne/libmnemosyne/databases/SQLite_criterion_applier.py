#
# SQLite_criterion_applier.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.criterion import CriterionApplier
from mnemosyne.libmnemosyne.criteria.default_criterion import DefaultCriterion


class DefaultCriterionApplier(CriterionApplier):

    used_for = DefaultCriterion

    def split_set(self, _set, chunk_size):
        lst = list(_set)
        # Note that [1,2,3][2:666] = [3]
        return [lst[i:i+chunk_size] for i in range(0, len(lst), chunk_size)]

    def set_activity_for_tags_with__id(self, _tag_ids, active):
        if len(_tag_ids) == 0:
            return
        command = """update cards set active=? where _id in
            (select _card_id from tags_for_card where _tag_id in ("""
        args = [1 if active else 0]
        for _tag_id in _tag_ids:
            command += "?,"
            args.append(_tag_id)
        command = command.rsplit(",", 1)[0] + "))"
        self.database().con.execute(command, args)

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
            # Turn on active tags. Limit to 500 at a time to deal with
            # SQLite limitations.
            for chunked__tag_ids in self.split_set(\
                    criterion._tag_ids_active, 500):
                self.set_activity_for_tags_with__id(chunked__tag_ids, active=1)
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
        # Turn off forbidden tags. Limit to 500 at a time to deal with
        # SQLite limitations.
        for chunked__tag_ids in self.split_set(\
                criterion._tag_ids_forbidden, 500):
            self.set_activity_for_tags_with__id(chunked__tag_ids, active=0)
