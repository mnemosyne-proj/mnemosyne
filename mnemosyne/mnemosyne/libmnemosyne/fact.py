#
# fact.py <Peter.Bienstman@UGent.be>
#

import datetime
import hashlib

from mnemosyne.libmnemosyne.component_manager import get_database


class Fact(object):

    """Basic unit of information from which several cards can be derived.

    The fields are stored in a dictionary, and can be get and set using the
    standard dictionary syntax.

    Categories and card_type_id are stored here, because when resetting the
    learning data on export, we only export facts.

    Note that we store a card_type_id, as opposed to a card_type, because
    otherwise we can't use pickled databases, as the card_types themselves
    are not stored in the database.  It is also closer the SQL implementation.

    When making new card types, it is best to reuse the keys below as much
    as possible, to facilitate conversion between card types:

    === =============
     q  question
     a  answer
     f  foreign word
     t  translation
     p  pronunciation
    === =============

    """

    def __init__(self, data, cat_names, card_type, id=None):
        self.added = datetime.datetime.now()
        self.data = data
        self.card_type = card_type
        db = get_database()
        self.cat = []
        for cat_name in cat_names:
            self.cat.append(db.get_or_create_category_with_name(cat_name))
        if id is None:
            digest = hashlib.md5(str(self.data).encode("utf-8") + \
                             str(self.added)).hexdigest()
            id = digest[0:8]
        self.id = id

    def __getitem__(self, key):
        try:
            return self.data[key]
        except IndexError:
            raise KeyError

    def __setitem__(self, key, value):
        self.data[key] = value
