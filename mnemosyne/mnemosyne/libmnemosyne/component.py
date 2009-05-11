#
# component.py <Peter.Bienstman@UGent.be>
#

class Component(object):

    """Base class of components that are registered with the component
    manager. Each component knows its type ('database', 'scheduler',
    'card_type', ...).

    'used_for' can store certain relationships between components, e.g.
    a card type widget is used for a certain card type.

    'delayed_instantion' is usually set to True for GUI widgets which are
    'used_for' a certain plugin, and for which it is better for efficiency
    reasons to delay their instantiation to when the plugin is activated.

    """
    
    component_type = ""
    used_for = None
    delayed_instantiation = False

    def activate(self):

        """Initialisation code called when the component is about to do actual
        work, and which can't happen in the constructor, e.g. because
        components on which it relies have not yet been registered.

        """

        pass

    def deactivate(self):        
        pass
