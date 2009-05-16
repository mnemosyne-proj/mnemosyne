#
# component.py <Peter.Bienstman@UGent.be>
#

class Component(object):

    """Base class of components that are registered with the component
    manager. This is a list of component types: config, log, database,
    scheduler, translator, filter, card_type, card_type_converter,
    card_type_widget, ui_component, renderer, ui_controller_main, main_widget,
    ui_controller_review, review_widget, plugin, function_hook.       

    'used_for' can store certain relationships between components, e.g.
    a card type widget is used for a certain card type.

    For efficiency reasons, not all components are instantiated immediately,
    e.g. instantiating a complex widget can take a lot of time on a mobile
    device. Some components like review widgets need to be instantiated when
    the plugin in which they are contained becomes active. Others, like card
    type widgets, are instantiated even later, e.g. when the add or edit
    dialog is shown.
    
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
