#
# fact.py <Peter.Bienstman@UGent.be>
#

import time


class Fact(object):

    """Basic unit of information from which several cards can be derived.

    The fields are stored in a dictionary called 'data', and can be get and 
    set using the standard dictionary syntax.
    
    Note that a dynamic data field can be defined by defining a data_foo method
    for a card_type that accepts a datafields dictonary.

    Card_type and categories are also stored here, because when resetting the
    learning data on export, we only export facts.

    Creating and modification dates are POSIX timestamps stored as integers.

    'id' is used to identify this object to the external world (logs, xml
    files, ...), whereas '_id' is an internal id that could be different and
    that can be used by the database for efficiency reasons.

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

    def __init__(self, data, card_type, creation_time=None, id=None):
        if creation_time is None:
            creation_time = time.time()
        self.creation_time = creation_time
        self.modification_time = self.creation_time
        self.data = data
        self.card_type = card_type
        if id is None:
            import uuid
            id = str(uuid.uuid4())
        self.id = id
        self._id = None

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
            dynfield = getattr(self.card_type, 'field_' + key, None)
            if not dynfield:
                raise KeyError, "Fact has no field '%s'" % key
            else:
                return dynfield(self.data)

    def __setitem__(self, key, value):
        self.data[key] = value
        
