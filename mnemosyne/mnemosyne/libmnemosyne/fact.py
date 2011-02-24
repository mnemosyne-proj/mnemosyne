#
# fact.py <Peter.Bienstman@UGent.be>
#

import re

from mnemosyne.libmnemosyne.utils import rand_uuid, CompareOnId

re_src = re.compile(r"""src=\"(.+?)\"""", re.DOTALL | re.IGNORECASE)


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
            id = rand_uuid()
        self.id = id
        self._id = None
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
        
    def contains_static_media(self):
        return re_src.search("".join(self.data.values())) != None
