#
# fact.py <Peter.Bienstman@UGent.be>
#

import datetime

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from mnemosyne.libmnemosyne.component_manager import database


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

    def __init__(self, data, cat_names, card_type, uid=None):
        """
        data : dict of card data
        cat_names : XXX: use list of Category instances? why in constructor? add later
        card_type : CardType instance
        uid : globally unique id for this card
        """
        self.added = datetime.datetime.now()
        self.data = data
        self.card_type = card_type
        db = database()
        self.cat = []
        for cat_name in cat_names:
            self.cat.append(db.get_or_create_category_with_name(cat_name))
        if uid is None:
            # XXX use guid module?
            uid = md5(repr(sorted(data.items())) + \
                str(self.added)).hexdigest()
        self.uid = uid

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
