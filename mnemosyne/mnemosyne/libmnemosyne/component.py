#
# component.py <Peter.Bienstman@UGent.be>
#

class Component(object):

    """Base class of components that are registered with the component
    manager. Each component knows its type ('database', 'scheduler',
    'card_type', ...).

    'used_for' can store certain relationships between components, e.g.
    a card type widget is used for a certain card type.

    For efficiency reasons, not all components are instantiated immediately,
    e.g. instantiating a complex widget can take some time on a mobile device.
    Some components like review widgets need to be instantiated when their
    corresponding plugin (for which they are 'used_for') becomes active.
    Others, like card type widgets, are instantiated even later, e.g. when the
    add or edit dialog is shown.
    
    """
    
    component_type = ""
    used_for = None

    IMMEDIATELY = 0
    WHEN_PLUGIN_ACTIVE = 1
    LATER = 2
    
    instantiate = IMMEDIATELY

    def activate(self):

        """Initialisation code called when the component is about to do actual
        work, and which can't happen in the constructor, e.g. because
        components on which it relies have not yet been registered.

        """

        pass

    def deactivate(self):        
        pass
