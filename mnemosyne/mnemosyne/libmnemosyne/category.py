#
# category.py <Peter.Bienstman@UGent.be>
#

class Category(object):
    
    """The category name is the full name, including all levels of the hierarchy
    separated by two colons.

    'id' is used to identify this object to the external world (logs, xml
    files, ...), whereas '_id' is an internal id that could be different and
    that can be used by the database for efficiency reasons.
    
    """

    def __init__(self, name, id=None):
        if id is None:
            import uuid
            id = str(uuid.uuid4())
        self.id = id
        self._id = None
        self.name = name
        self.needs_sync = True

    def __eq__(self, other):
        try:
            return self.id == other.id
        except:
            return False
