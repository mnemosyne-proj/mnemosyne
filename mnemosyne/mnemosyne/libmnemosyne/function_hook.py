#TODO: see where we need hook points

##############################################################################
#
# function_hook.py <Peter.Bienstman@UGent.be>
#
##############################################################################

from plugin import Plugin



##############################################################################
#
# FunctionHook
#
#  Note that this class actually does not contain any new functionality.
#  It mainly exists to make the taxonomy of different component types visible
#  and for documentation purposes.
#
#  The 'type' from Plugin should be the name of the function hook.
#  The 'run' method from plugin is the one that does all the work.
#
#  TODO: list possible hook points.
#
##############################################################################

class FunctionHook(Plugin):

    pass

