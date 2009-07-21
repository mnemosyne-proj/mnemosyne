#
# SQLite_statistics.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.utils import numeric_string_cmp


class SQLiteStatistics(object):

    """Code to be injected into the SQLite database class through inheritance,
    so that SQLite.py does not becomes too large.

    """

    def get_tags__id_and_name(self):
        result = [(cursor[0], cursor[1]) for cursor in self.con.execute(\
            "select _id, name from tags")]
        result.sort(key=lambda x: x[1], cmp=numeric_string_cmp)
        return result
        
    def easinesses(self):
        return [cursor[0] for cursor in self.con.execute(\
            "select easiness from cards where active=1 and grade>=0")]

    def easinesses_for__tag_id(self, _tag_id):    
        return [cursor[0] for cursor in self.con.execute(\
            """select cards.easiness from cards, tags_for_card where
            tags_for_card._card_id=cards._id and cards.active=1 and
            cards.grade>=0 and tags_for_card._tag_id=?""", (_tag_id, ))]

    def card_count_for_grade(self, grade):
        return self.con.execute(\
            "select count() from cards where grade=? and active=1",
            (grade, )).fetchone()[0]

    def card_count_for_grade_and__tag_id(self, grade, _tag_id):
        return self.con.execute(\
             """select count() from cards, tags_for_card where
             tags_for_card._card_id=cards._id and cards.active=1
             and tags_for_card._tag_id=? and grade=?""",
             (_tag_id, grade)).fetchone()[0]

    def card_count_scheduled_between(self, start, stop):
        return self.con.execute(\
            """select count() from cards where active=1 and grade>=2
            and ?<next_rep and next_rep<=?""",
            (start, stop)).fetchone()[0]
