#
# fact.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.utils import CompareOnId


class Fact(CompareOnId):

    """Basic unit of information from which several cards can be derived.

    The fields are stored in a dictionary called 'data', and can be get and 
    set using the standard dictionary syntax.

    'id' is used to identify this object to the external world (logs, xml
    files, ...), whereas '_id' is an internal id that could be different and
    that can be used by the database for efficiency reasons.

    The keys in data should not contain characters like <, >, &, ..., as they
    are used as unescaped tag names during sync.
    
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

    def __init__(self, data, id=None):
        self.data = data
        if id is None:
            # Importing this module takes a long time on mobile devices,
            # so we only do so as late as possible.
            import uuid
            id = str(uuid.uuid4())
        self.id = id
        self._id = None
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
        
