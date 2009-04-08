#
# category.py <Peter.Bienstman@UGent.be>
#

import uuid
import datetime


class Category(object):
    
    """The category name is the full name, including all levels of the hierarchy
    separated by two colons.
    
    """

    def __init__(self, name, id=None):
        if id is None:
            id = str(uuid.uuid4())
        self.id = id
        self.name = name
        self.needs_sync = True

    def __eq__(self, other):
        try:
            return self.id == other.id
        except:
            return False
