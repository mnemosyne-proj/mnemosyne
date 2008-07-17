
##############################################################################
#
# plugin.py <Peter.Bienstman@UGent.be>
#
##############################################################################

##############################################################################
#
# register_function_hook
#
##############################################################################

function_hooks = {}

def register_function_hook(name, function):

    global function_hooks

    if function_hooks.has_key(name):
        function_hooks[name].append(function)
    else:
        function_hooks[name] = [function]



##############################################################################
#
# unregister_function_hook
#
##############################################################################

def unregister_function_hook(name, function):

    global function_hooks

    if function_hooks.has_key(name):
        function_hooks[name].remove(function)



##############################################################################
#
# Plugin
#
##############################################################################

plugins = []

class Plugin:

    def __init__(self):
        global plugins
        plugins.append(self)
        
    def description(self):
        pass
    
    def load(self):
        pass

    def unload(self):
        pass
