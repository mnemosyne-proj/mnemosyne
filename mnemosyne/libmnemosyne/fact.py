#
# fact.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.utils import rand_uuid, CompareOnId


class Fact(CompareOnId):

    """Basic unit of information from which several cards can be derived.

    The fields are stored in a dictionary called 'data', and can be get and
    set using the standard dictionary syntax.

    'id' is used to identify this object to the external world (logs, xml
    files, sync, ...), whereas '_id' is an internal id that could be different
    and that can be used by the database for efficiency reasons.

    The keys in data should not contain characters like <, >, &, ..., as they
    are used as unescaped tag names during sync.

    When making new card types, it is best to reuse the keys below as much
    as possible, to facilitate conversion between card types:

    ===== =============
     f    front
     b    back
     f    foreign word
     p_1  pronunciation
     m_1  meaning
    ===== =============

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

    def __contains__(self, key):
        return key in self.data

    def update(self, new_dict):
        return self.data.update(new_dict)

