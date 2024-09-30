#
# component_manager.py <Peter.Bienstman@gmail.com>
#

class ComponentManager(object):

    """Manages the different components. Typically, instances of the different
    components are stored, as opposed to classes. In such a way, the component
    manager stores all the state of the user. Exceptions are widgets other
    than the main widget, which are lazily created for efficiency reasons.

    For certain components, many can be active at the same time (card types,
    filters, function hooks, ...). For others, there can be only on active
    at the same time, like schedule, database ... The idea is that the last
    one registered takes preference.

    """

    def __init__(self):
        self.components = {} # {used_for: {type: [component]} }
        self.card_type_with_id = {}
        self.render_chain_with_id = {}
        self.study_mode_with_id = {}
        self.language_with_id = {}
        self.debug_file = None

    def register(self, component):
        comp_type = component.component_type
        used_for = component.used_for if type(component.used_for) in \
            (tuple, list) else [component.used_for]
        for used_for_i in used_for:
            if used_for_i not in self.components:
                self.components[used_for_i] = {}
            if comp_type not in self.components[used_for_i]:
                self.components[used_for_i][comp_type] = [component]
            else:
                if component not in self.components[used_for_i][comp_type]:
                    self.components[used_for_i][comp_type].append(component)
        # (We could abuse the component's used_for as the id here, but that
        # would hamper readability.)
        if comp_type == "card_type":
            self.card_type_with_id[component.id] = component
        elif comp_type == "render_chain":
            self.render_chain_with_id[component.id] = component
        elif comp_type == "study_mode":
            self.study_mode_with_id[component.id] = component
        elif comp_type == "language":
            self.language_with_id[component.used_for] = component

    def unregister(self, component):
        comp_type = component.component_type
        used_for = component.used_for if type(component.used_for) in \
            (tuple, list) else [component.used_for]
        for used_for_i in used_for:
            # Different components (e.g. Pronouncers) could be 'used_for' the
            # same Component (e.g. a Language).
            if component in self.components[used_for_i][comp_type]:
                self.components[used_for_i][comp_type].remove(component)
        if component.component_type == "card_type":
            del self.card_type_with_id[component.id]
        elif component.component_type == "render_chain":
            del self.render_chain_with_id[component.id]

    def add_gui_to_component(self, component_name, gui_component, in_front=False):

        """Typical use case for this is when a plugin has a GUI component
        which obviously does not live inside libmnemosyne, and which needs to
        be added at a later stage.

        """

        for used_for in self.components:
            for component_type in self.components[used_for]:
                for component in self.components[used_for][component_type]:
                    if component.__class__.__name__ == component_name:
                        if in_front:
                            component.gui_components.insert(0, gui_component)
                        else:
                            component.gui_components.append(gui_component)


    def all(self, comp_type, used_for=None):

        """For components for which there can be many active at once."""

        # If 'used_for' is not a class, we can just retrieve it.
        if used_for == None or isinstance(used_for, str):
            try:
                return self.components[used_for][comp_type]
            except:
                return []
        # Otherwise, we also take inheritance into account. First, we see
        # if there is a component registered for the exact type.
        try:
            return self.components[used_for][comp_type]
        except Exception as e:
            # See if there is a component registered for the parent class.
            # We need to do this both for the case where 'used_for' is a
            # tuple and a single class.
            if isinstance(used_for, tuple):
                tuple_class_keys = \
                    [_key for _key in self.components.keys() if \
                    not isinstance(_key, str) and not (_key == None) \
                    and isinstance(_key, tuple)]
                for key in tuple_class_keys:
                    if issubclass(used_for[0], key[0]) and \
                       issubclass(used_for[1], key[1]):
                        try:
                            return self.components[key][comp_type]
                        except:
                            return []
                return []
            else:
                non_tuple_class_keys = \
                    [_key for _key in self.components.keys() if \
                    not isinstance(_key, str) and not (_key == None) \
                    and not isinstance(_key, tuple)]
                for key in non_tuple_class_keys:
                    if issubclass(used_for, key):
                        try:
                            return self.components[key][comp_type]
                        except:
                            return []
                return []

    def current(self, comp_type, used_for=None):

        """For components for which there can be only one active at any
        time.

        """

        all = self.all(comp_type, used_for)
        if all == []:
            return None
        else:
            return all[-1]

    def deactivate_all(self):
        for used_for in self.components:
            for comp_type in self.components[used_for]:
                for component in self.components[used_for][comp_type]:
                    if not isinstance(component, type):
                        component.deactivate()
        # Following line deactivated to work around
        # https://bugreports.qt.io/browse/QTBUG-52988
        #self.components = {}
        self.card_type_with_id = {}

    def debug(self, msg):

        """Log a debugging message if debugging is enabled.

        """

        if self.debug_file:
            self.debug_file.write(str(msg + "\n").encode('UTF-8'))


# A component manager stores the entire session state of a user through the
# different components it registers. To enable multiple users to use a single
# instance of libmnemosyne simultaneously, we store a component manager
# instance for each user.

_component_managers = {}

def clear_component_managers():

    """Used for the testsuite to prevent multiple component managers hanging
    around.

    """

    user_ids = list(_component_managers.keys())
    for user_id in user_ids:
        unregister_component_manager(user_id)

def new_component_manager():
    return ComponentManager()

def register_component_manager(component_manager, user_id):
    global _component_managers
    _component_managers[user_id] = component_manager

def unregister_component_manager(user_id):
    global _component_managers
    if user_id in _component_managers:
        del _component_managers[user_id]

def migrate_component_manager(old_user_id, new_user_id):
    global _component_managers
    # Work around a test suite issue where both client and server share the
    # same component manager, potentially causing race conditions.
    if old_user_id not in _component_managers:
        return
    _component_managers[new_user_id] = _component_managers[old_user_id]
    del _component_managers[old_user_id]
