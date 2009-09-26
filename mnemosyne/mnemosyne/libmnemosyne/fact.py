#
# fact.py <Peter.Bienstman@UGent.be>
#

import time

from mnemosyne.libmnemosyne.utils import CompareOnId


class Fact(CompareOnId):

    """Basic unit of information from which several cards can be derived.

    The fields are stored in a dictionary called 'data', and can be get and 
    set using the standard dictionary syntax.
    
    Note that a dynamic data field can be defined by defining a data_foo method
    for a card_type that accepts a datafields dictonary.

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
            creation_time = int(time.time())
        self.creation_time = creation_time
        self.modification_time = self.creation_time
        self.data = data
        self.card_type = card_type
        if id is None:
            import uuid
            id = str(uuid.uuid4())
        self.id = id
        self._id = None
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
        
