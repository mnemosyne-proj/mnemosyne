#
# libmnemosyne <Peter.Bienstman@UGent.be>
#

import os
import sys

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import expand_path, traceback_string
from mnemosyne.libmnemosyne.component_manager import new_component_manager, \
    register_component_manager, unregister_component_manager


class Mnemosyne(Component):

    """This class groups the functionality needed to initialise and finalise
    Mnemosyne in a typical scenario.

    """

    def __init__(self, resource_limited=False):
        self.components = [
         ("mnemosyne.libmnemosyne.databases.SQLite",
          "SQLite"),
         ("mnemosyne.libmnemosyne.configuration",
          "Configuration"),
         ("mnemosyne.libmnemosyne.loggers.sql_logger",
          "SqlLogger"), 
         ("mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne",
          "SM2Mnemosyne"),
         ("mnemosyne.libmnemosyne.stopwatch",
          "Stopwatch"),         
         ("mnemosyne.libmnemosyne.card_types.front_to_back",
          "FrontToBack"),
         ("mnemosyne.libmnemosyne.card_types.both_ways",
          "BothWays"),
         ("mnemosyne.libmnemosyne.card_types.three_sided",
          "ThreeSided"),
         ("mnemosyne.libmnemosyne.card_types.both_ways",
          "FrontToBackToBothWays"),
         ("mnemosyne.libmnemosyne.card_types.both_ways",
          "BothWaysToFrontToBack"),
         ("mnemosyne.libmnemosyne.card_types.three_sided",
          "FrontToBackToThreeSided"),
         ("mnemosyne.libmnemosyne.card_types.three_sided",
          "BothWaysToThreeSided"),
         ("mnemosyne.libmnemosyne.card_types.three_sided",
          "ThreeSidedToFrontToBack"),
         ("mnemosyne.libmnemosyne.card_types.three_sided",
          "ThreeSidedToBothWays"),
         ("mnemosyne.libmnemosyne.renderers.html_css",
          "HtmlCss"),
         ("mnemosyne.libmnemosyne.filters.escape_to_html",
          "EscapeToHtml"),
         ("mnemosyne.libmnemosyne.filters.expand_paths",
          "ExpandPaths"),
         ("mnemosyne.libmnemosyne.filters.latex",
          "Latex"),
         ("mnemosyne.libmnemosyne.filters.html5_media",
          "Html5Media"),
         ("mnemosyne.libmnemosyne.controllers.default_controller",
          "DefaultController"),
         ("mnemosyne.libmnemosyne.review_controllers.SM2_controller",
          "SM2Controller"),
         ("mnemosyne.libmnemosyne.card_types.map",
          "MapPlugin"),
         ("mnemosyne.libmnemosyne.card_types.cloze",
          "ClozePlugin"),
         ("mnemosyne.libmnemosyne.plugins.cramming_plugin",
          "CrammingPlugin"),
         ("mnemosyne.libmnemosyne.statistics_pages.schedule",
          "Schedule"),
         ("mnemosyne.libmnemosyne.statistics_pages.grades",
          "Grades"),
         ("mnemosyne.libmnemosyne.statistics_pages.easiness",
          "Easiness"),
         ("mnemosyne.libmnemosyne.statistics_pages.current_card",
          "CurrentCard"),
         ("mnemosyne.libmnemosyne.file_formats.mnemosyne1_mem",
          "Mnemosyne1Mem")]
        self.extra_components_for_plugin = {}
        self.resource_limited = resource_limited

    def initialise(self, basedir, filename=None):
        self.component_manager = new_component_manager()
        self.register_components()
        self.config().basedir = basedir
        self.config().resource_limited = self.resource_limited 
        self.activate_components()
        self.initialise_error_handling()
        register_component_manager(self.component_manager,
                                   self.config()["user_id"])
        self.execute_user_plugin_dir()
        self.activate_saved_plugins()
        # Loading the database should come after all user plugins have been
        # loaded, since these could be needed e.g. for a card type in the
        # database.
        self.load_database(filename)
        self.log().started_program()
        self.log().started_scheduler()
        self.log().loaded_database()
        # Finally, we can activate the main widget.
        self.main_widget().activate()

    def register_components(self):

        """We register all components, but don't activate them yet, because in
        order to activate certain components, certain other components already
        need to be registered. Also, the activation needs to happen in a
        predefined order, and we don't want to burden UI writers with listing
        the components in the correct order.

        """

        for module_name, class_name in self.components:
            exec("from %s import %s" % (module_name, class_name))
            exec("component = %s" % class_name)
            if component.instantiate == Component.IMMEDIATELY:
                component = component(self.component_manager)
            self.component_manager.register(component)
        for plugin_name in self.extra_components_for_plugin:
            for module_name, class_name in \
                    self.extra_components_for_plugin[plugin_name]:
                exec("from %s import %s" % (module_name, class_name))
                exec("component = %s" % class_name)           
                self.component_manager.add_component_to_plugin(\
                    plugin_name, component)
            
    def activate_components(self):
        
        """Now that everything is registered, we can activate the components
        in the correct order: first config, followed by log.
        
        """
        
        for component in  ["config", "log", "database", "scheduler",
                           "controller"]:
            try:
                self.component_manager.get_current(component).activate()
            except RuntimeError, e:
                self.main_widget().error_box(str(e))

    def initialise_error_handling(self):
        if sys.platform == "win32":
            error_log = os.path.join(self.config().basedir, "error_log.txt")
            sys.stderr = file(error_log, "a")
                    
    def execute_user_plugin_dir(self):
        # When updating from 1.x, move the plugin directory.
        if self.config()["path"].endswith(".mem"):       
            plugin_dir = os.path.join(self.config().basedir, "plugins")
            new_plugin_dir = os.path.join(self.config().basedir, "plugins_1.x")            
            if os.path.exists(plugin_dir):
                import shutil
                shutil.move(plugin_dir, new_plugin_dir)
                return
        # Else, proceed nomally. 
        basedir = self.config().basedir
        plugindir = unicode(os.path.join(basedir, "plugins"))
        sys.path.insert(0, plugindir)
        for component in os.listdir(plugindir):
            if component.endswith(".py"):
                try:
                    __import__(component[:-3])
                except:
                    from mnemosyne.libmnemosyne.translator import _
                    msg = _("Error when running plugin:") \
                          + "\n" + traceback_string()
                    self.main_widget().error_box(msg)

    def activate_saved_plugins(self):
        for plugin in self.config()["active_plugins"]:
            try:
                for p in self.plugins():
                    if plugin == p.__class__.__name__:
                        p.activate()
                        break
            except:
                from mnemosyne.libmnemosyne.translator import _
                msg = _("Error when running plugin:") \
                      + "\n" + traceback_string()
                self.main_widget().error_box(msg)

    def load_database(self, filename):
        if not filename:
            filename = self.config()["path"]
        filename = expand_path(filename, self.config().basedir)
        try:
            if not os.path.exists(filename):
                self.database().new(filename)
            elif filename.endswith(".mem"):  # Do upgrade.
                new_filename = filename.replace(".mem", ".db")
                self.database().new(new_filename)
                for format in self.component_manager.get_all("file_format"):
                    if format.__class__.__name__ == "Mnemosyne1Mem":
                        format.do_import(filename)
            else:
                self.database().load(filename)
        except RuntimeError, e:
            # Making sure the GUI is in a correct state when no database is
            # loaded would require a lot of extra code, and this is only a
            # corner case anyhow. So, as workaround, we create a temporary
            # database.
            from mnemosyne.libmnemosyne.translator import _
            self.main_widget().error_box(str(e))
            self.main_widget().error_box(_("Creating temporary database."))
            filename = os.path.join(os.path.split(filename)[0], "___TMP___" \
                                    + self.database().suffix)
            self.database().new(filename)
        self.controller().update_title()

    def finalise(self):
        # Saving the config should happen before we deactivate the plugins,
        # otherwise they are not restored upon reload.
        self.config().save()
        user_id = self.config()["user_id"]
        # We need to log before we unload the database.
        self.log().saved_database()
        self.log().stopped_program()
        # Now deactivate the database, such that deactivating plugins with
        # card types does not raise an error about card types in use.
        self.database().deactivate()
        self.component_manager.unregister(self.database())
        # Then do the other components.
        self.component_manager.deactivate_all()
        unregister_component_manager(user_id)
        
        
