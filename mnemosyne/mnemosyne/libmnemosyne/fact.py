##############################################################################
#
# fact.py <Peter.Bienstman@UGent.be>
#
##############################################################################



##############################################################################
#
# Fact
#
#   Basic unit of information from which several cards can be derived.
#   The fields are stored in a dictionary.
#
#
# TODO: make list of common keys for standardisation
#
##############################################################################

class Fact:

    def __init__(self, data, id):
        self.id   = id
        self.data = data

    def __getitem__(self, key):
        try:
            return self.data[key]
        except IndexError:
            raise KeyError

    def __setitem__(self, key, value):
        self.data[key] = value
