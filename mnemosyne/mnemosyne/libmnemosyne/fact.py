#
# fact.py <Peter.Bienstman@UGent.be>
#

import uuid
from mnemosyne.libmnemosyne.component_manager import database


class Fact(object):

    """Basic unit of information from which several cards can be derived.

    The fields are stored in a dictionary called 'data', and can be get and 
    set using the standard dictionary syntax.
    
    Note that a dynamic data field can be defined by defining a data_foo method
    for a card_type that accepts a datafields dictonary.

    Card_type and categories are also stored here, because when resetting the
    learning data on export, we only export facts.

    Creating and modification dates are stored as days since the creation of the
    database (see start_date.py for rationale).

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

    def __init__(self, data, card_type, id=None, creation_date=None):
        if not creation_date:
            creation_date = database().days_since_start()
        self.creation_date = creation_date
        self.modification_date = self.creation_date
        self.data = data
        self.card_type = card_type
        if id is None: 
            id = str(uuid.uuid4())
        self.id = id
        self.needs_sync = True

    def __eq__(self, other):
        try:
            return self.id == other.id
        except:
            return False
    
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
        
