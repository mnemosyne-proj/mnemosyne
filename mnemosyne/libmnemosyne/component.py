#
# component.py <Peter.Bienstman@gmail.com>
#


class Component(object):

    """Base class of components that are registered with the component
    manager. This is a list of component types: config, log, database,
    scheduler, stopwatch, gui_translator, card_type, card_type_converter,
    render_chain, renderer, filter, card_type_widget,
    generic_card_type_widget, ui_component, controller, main_widget,
    review_controller, review_widget, file format, plugin, hook,
    criterion, criterion_applier, statistics_page, sync_server,
    study_mode, translator, pronouncer, all the abstract dialogs, ...

    'used_for' can store certain relationships between components, e.g.
    a card type widget is used for a certain card type.

    Most of the time, instances are stored here, apart from widgets in which
    case classes are stored. (Instantiating a complex widget can take a lot of
    time on a mobile device, and should be done lazily.) Only the main
    widget is stored as an instance here.

    To achieve this lazy instantiation for widget, set 'instantiate == LATER'.
    Other components can then instantiate the widget when they see fit.
    The instance is not cached for subsequent reuse, as these widgets
    typically can become obsolete/overwritten by plugins.

    It can be that when instantiating a component, not all the other components
    on which it relies have been instantiated yet. E.g., the log and the
    database depend on each other before doing actual work. Therefore, some of
    the  actual initialisation work can be postponed to the 'activate' function.

    Each component has access to all of the context of the other components
    because it hold a reference to the user's component manager.

    We need to pass the context of the component manager already in the
    constructor, as many component make use of it in their __init__ method.
    This means that derived components should always call the
    Component.__init__ if they provide their own constructor.

    In case the GUI needs to add functionality to a certain component, that
    can be done through component_manager.add_gui_to_component() function
    (lower level) or through the gui_for_component class variable (higher
    level).

    """

    component_type = ""
    used_for = None

    IMMEDIATELY = 0
    LATER = 1

    instantiate = IMMEDIATELY

    def __init__(self, component_manager, **kwds):
        super().__init__(**kwds)  # For parent classes other than 'Object'.
        self.component_manager = component_manager
        self.gui_components = []
        self.instantiated_gui_components = []

    def activate(self):

        """Initialisation code called when the component is about to do actual
        work, and which can't happen in the constructor, e.g. because
        components on which it relies have not yet been registered.

        """

        pass

    def activate_gui_components(self):

        """GUI classes are only instantiated when activated, since that can take
        a lot of time on mobile clients.

        Classes that require more control over this, e.g. when needing to return
        values from the UI, can subclass this.

        """

        for component in self.gui_components:
            component = component(component_manager=self.component_manager)
            self.component_manager.register(component)
            component.activate()
            self.instantiated_gui_components.append(component)

    def deactivate(self):
        for component in self.instantiated_gui_components:
            component.deactivate()
            self.component_manager.unregister(component)
        self.instantiated_gui_components = []

    # Convenience functions, for easier access to all of the context of
    # libmnemosyne from within a component.

    def _(self):
        return self.component_manager.current("gui_translator")

    def gui_translator(self):
        return self.component_manager.current("gui_translator")

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
        return self.component_manager.current("review_widget")

    def controller(self):
        return self.component_manager.current("controller")

    def review_controller(self):
        return self.component_manager.current("review_controller")

    def card_types(self):
        return self.component_manager.all("card_type")

    def card_type_with_id(self, id):
        return self.component_manager.card_type_with_id[id]

    def render_chain(self, id="default"):
        return self.component_manager.render_chain_with_id[id]

    def study_mode_with_id(self, id):
        return self.component_manager.study_mode_with_id[id]

    def plugins(self):
        return self.component_manager.all("plugin")

    def languages(self):
        return self.component_manager.language_with_id.values()

    def language_with_id(self, id):
        return self.component_manager.language_with_id[id]

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
