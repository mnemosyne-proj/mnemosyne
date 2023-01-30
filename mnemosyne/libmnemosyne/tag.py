#
# tag.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.utils import rand_uuid, CompareOnId


class Tag(CompareOnId):

    """The tag name is the full name, including all levels of the hierarchy
    separated by ::.

    'id' is used to identify this object to the external world (logs, xml
    files, sync, ...), whereas '_id' is an internal id that could be
    different and that can be used by the database for efficiency reasons.

    Untagged cards are given the internal tag __UNTAGGED__, to allow for a
    fast implementation of applying criteria.

    """

    def __init__(self, name, id=None):
        if id is None:
            id = rand_uuid()
        self.id = id
        self._id = None
        self.name = name
        self.extra_data = {}

