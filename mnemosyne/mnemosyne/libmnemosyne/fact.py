#
# fact.py <Peter.Bienstman@UGent.be>
#

import datetime

try:
    from hashlib import md5
except ImportError:
    from md5 import md5


class Fact(object):

    """Basic unit of information from which several cards can be derived.

    The fields are stored in a dictionary called 'data', and can be get and 
    set using the standard dictionary syntax.
    
    Note that a dynamic data field can be defined by defining a data_foo method
    for a card_type that accepts a datafields dictonary.

    Card_type and categories are also stored here, because when resetting the
    learning data on export, we only export facts.

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

    def __init__(self, data, card_type, categories=[], uid=None, added=None):
        if not added:
            added = datetime.datetime.now()
        self.added = added
        self.data = data
        self.card_type = card_type
        self.cat = categories
        if uid is None: 
            # TODO KW: use guid module? Make sure not to use too much space for 
            # the global log analysis of all users, though.
            uid = md5(repr(sorted(data.items())) + str(self.added)).hexdigest()
        self.uid = uid

    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            # Check if the card_type defines a dynamic field by this name.
            dynfield = getattr(self.card_type, 'field_'+key, None)
            if dynfield is None:
                raise KeyError("Fact has no field '%s'" % key)
            else:
                return dynfield(self.data)

    def __setitem__(self, key, value):
        self.data[key] = value
