#
# category.py <Peter.Bienstman@UGent.be>
#


class Category(object):
    
    """The category name is the full name, including all levels of the hierarchy
    separated by two colons.
    
    """

    def __init__(self, name):
        self.name = name
