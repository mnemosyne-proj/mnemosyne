#
# component.py <Peter.Bienstman@UGent.be>
#


class Component(object):

    """Base class of components that are registered with the component
    manager. This is a list of component types: config, log, database,
    scheduler, stopwatch, translator, card_type, card_type_converter,
    render_chain, renderer, filter, card_type_widget,
    generic_card_type_widget, ui_component, controller, main_widget,
    review_controller, review_widget, file format, plugin, hook,
    criterion, criterion_applier, statistics_page, sync_server,
    all the abstract dialogs, ...

    'used_for' can store certain relationships between components, e.g.
    a card type widget is used for a certain card type.

    Most of the time, instances are stored here, apart from widgets in which
    case classes are stored. (Instantiating a complex widget can take a lot of
    time on a mobile device, and should be done lazily.) Only the main
    widget is stored as an instance here.

    When 'instantiate == LATER', the component is lazily created when needed.
    The instance is not cached for subsequent reuse, as these widgets
    typically can become obsolete/overwritten by plugins.

    Each component has access to all of the context of the other components
    because it hold a reference to the user's component manager.

    We need to pass the context of the component manager already in the
    constructor, as many component make use of it in their __init__ method.
    This means that derived components should always call the
    Component.__init__ if they provide their own constructor.

    """

    component_type = ""
    used_for = None

    IMMEDIATELY = 0
    LATER = 1

    instantiate = IMMEDIATELY

    def __init__(self, component_manager, **kwds):
        super().__init__(**kwds)        
        self.component_manager = component_manager

    def activate(self):

        """Initialisation code called when the component is about to do actual
        work, and which can't happen in the constructor, e.g. because
        components on which it relies have not yet been registered.

        """

        pass

    def deactivate(self):
        pass

    # Convenience functions, for easier access to all of the context of
    # libmnemosyne from within a component.

    def _(self):
        return self.component_manager.current("translator")

    def translator(self):
        return self.component_manager.current("translator")

    def config(self):
        return self.component_manager.current("config")

    def log(self):
        return self.component_manager.current("log")

    def database(self):
        return self.component_manager.current("database")

    def scheduler(self):
        return self.component_manager.current("scheduler")

    def stopwatch(self):
        return self.component_manager.current("stopwatch")

    def main_widget(self):
        return self.component_manager.current("main_widget")

    def review_widget(self):

        """Apart from the main widget, we create all other widgets lazily for
        efficiency reasons. The review widget instance is therefore not stored
        in the component manager, but is under the control of the review
        controller.

        """

        return self.review_controller().widget

    def controller(self):
        return self.component_manager.current("controller")

    def review_controller(self):
        return self.component_manager.current("review_controller")

    def card_types(self):
        return self.component_manager.all("card_type")

    def card_type_with_id(self, id):
        return self.component_manager.card_type_with_id[id]

    def render_chain(self, id="default"):
        return self.component_manager.render_chain_by_id[id]

    def plugins(self):
        return self.component_manager.all("plugin")

    def start_review(self):
        self.review_controller().reset()

    def flush_sync_server(self):

        """If there are still dangling sessions (i.e. those waiting in vain
        for more client input) in the sync server, we should flush them and
        make sure they restore from backup before doing anything that could
        change the database (e.g. adding a card). Otherwise, if these
        sessions close later during program shutdown, their backup
        restoration will override the changes.
        
        Also stop any running media.

        """

        server = self.component_manager.current("sync_server")
        if server:
            server.flush()
        review_widget = self.review_widget()
        if review_widget:
            review_widget.stop_media()
