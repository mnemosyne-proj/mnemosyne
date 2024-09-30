#
# upgrade2.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.component import Component


class Upgrade2(Component):

    """Upgrade to SQL format 2, making sure card ids are unique."""

    def run(self):
        cards_with_id = {}
        for cursor in self.database().con.execute(\
            "select _id, id from cards order by _id"):
            _id, id = cursor
            if not id in cards_with_id:
                cards_with_id[id] = []
            cards_with_id[id].append(_id)
        for id in cards_with_id:
            if len(cards_with_id[id]) > 1:
                suffix = 1
                for _id in cards_with_id[id][1:]:
                    new_id = id + "." + str(suffix)
                    self.database().con.execute(\
                        "update cards set id=? where _id=?", (new_id, _id))
                    suffix += 1
        self.database().save()