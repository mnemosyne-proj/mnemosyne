#
# component.py <Peter.Bienstman@UGent.be>
#


class Component(object):

    """The base class of everything that can be plugged together and swapped
    out to realise the core functionality of Mnemosyne.

    """

    def __init__(self, name="", description=""):
        self.name = name
        self.description = description
