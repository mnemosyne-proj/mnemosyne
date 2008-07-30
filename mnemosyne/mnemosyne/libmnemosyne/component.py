##############################################################################
#
# component.py <Peter.Bienstman@UGent.be>
#
##############################################################################


#TODO: remove this class


##############################################################################
#
# Component
#
#  A component can optionally describe another object that it provides
#  services to, e.g. a CardType widget is used in relation to a CardType.
#
##############################################################################

class Component(object):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self, name, description="", used_for=used_for):
        
        self.name        = name
        self.description = description
        self.used_for    = used_for
