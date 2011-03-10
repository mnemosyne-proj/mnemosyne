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

    The automatic upgrades of the database can be turned off by setting
    'automatic_upgrade' to False. This is mainly useful for the testsuite.

    """

    def __init__(self, upload_science_logs):

        """For mobile clients, it is recommended that you set
        'upload_science_logs' to 'False'.
        
        We need to specify 'upload_science_logs' as an argument here, so
        that we can inject it on time to prevent the uploader thread from
        starting.

        """
        
        self.upload_science_logs = upload_science_logs
        self.component_manager = new_component_manager()
        self.components = [
         ("mnemosyne.libmnemosyne.databases.SQLite",
          "SQLite"),
         ("mnemosyne.libmnemosyne.configuration",
          "Configuration"),
         ("mnemosyne.libmnemosyne.loggers.database_logger",
          "DatabaseLogger"), 
         ("mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne",
          "SM2Mnemosyne"),
         ("mnemosyne.libmnemosyne.stopwatch",
          "Stopwatch"),         
         ("mnemosyne.libmnemosyne.card_types.front_to_back",
          "FrontToBack"),
         ("mnemosyne.libmnemosyne.card_types.both_ways",
          "BothWays"),
         ("mnemosyne.libmnemosyne.card_types.vocabulary",
          "Vocabulary"),
         ("mnemosyne.libmnemosyne.card_types.both_ways",
          "FrontToBackToBothWays"),
         ("mnemosyne.libmnemosyne.card_types.both_ways",
          "BothWaysToFrontToBack"),
         ("mnemosyne.libmnemosyne.card_types.vocabulary",
          "FrontToBackToVocabulary"),
         ("mnemosyne.libmnemosyne.card_types.vocabulary",
          "BothWaysToVocabulary"),
         ("mnemosyne.libmnemosyne.card_types.vocabulary",
          "VocabularyToFrontToBack"),
         ("mnemosyne.libmnemosyne.card_types.vocabulary",
          "VocabularyToBothWays"),
         ("mnemosyne.libmnemosyne.render_chains.default_render_chain",
          "DefaultRenderChain"),
         ("mnemosyne.libmnemosyne.render_chains.plain_text_chain",
          "PlainTextChain"), 
         ("mnemosyne.libmnemosyne.render_chains.sync_to_card_only_client",
          "SyncToCardOnlyClient"),
         ("mnemosyne.libmnemosyne.render_chains.card_browser_render_chain",
          "CardBrowserRenderChain"),  
         ("mnemosyne.libmnemosyne.filters.latex",
          "CheckForUpdatedLatexFiles"),
         ("mnemosyne.libmnemosyne.controllers.default_controller",
          "DefaultController"),
         ("mnemosyne.libmnemosyne.review_controllers.SM2_controller",
          "SM2Controller"),
         ("mnemosyne.libmnemosyne.card_types.map",
          "MapPlugin"),
         ("mnemosyne.libmnemosyne.card_types.cloze",
          "ClozePlugin"),
         ("mnemosyne.libmnemosyne.criteria.default_criterion",
          "DefaultCriterion"),
         ("mnemosyne.libmnemosyne.databases.SQLite_criterion_applier",
          "DefaultCriterionApplier"),   
         ("mnemosyne.libmnemosyne.plugins.cramming_plugin",
          "CrammingPlugin"),
         ("mnemosyne.libmnemosyne.statistics_pages.schedule",
          "Schedule"),
         ("mnemosyne.libmnemosyne.statistics_pages.retention_score",
          "RetentionScore"),
         ("mnemosyne.libmnemosyne.statistics_pages.cards_added",
          "CardsAdded"), 
         ("mnemosyne.libmnemosyne.statistics_pages.grades",
          "Grades"),
         ("mnemosyne.libmnemosyne.statistics_pages.easiness",
          "Easiness"),        
         ("mnemosyne.libmnemosyne.statistics_pages.current_card",
          "CurrentCard"),
         ("mnemosyne.libmnemosyne.file_formats.mnemosyne1_mem",
          "Mnemosyne1Mem")]
        self.extra_components_for_plugin = {}
        
    def initialise(self, data_dir=None, filename=None,
                   automatic_upgrades=True):
        self.register_components()
        if data_dir:
            self.config().data_dir = data_dir
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
        # Only now that the database is loaded, we can start writing log
        # events to it. This is why we log started_scheduler and
        # loaded_database manually.
        self.log().started_program()
        self.log().started_scheduler()
        self.log().loaded_database()
        # Upgrade if needed.
        if automatic_upgrades:
            from mnemosyne.libmnemosyne.upgrades.upgrade1 import Upgrade1
            Upgrade1(self.component_manager).run()  
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
        in the correct order: first config, followed by log, and then the
        rest.
        
        """

        # Activate config and inject necessary settings.
        try:
            self.component_manager.current("config").activate()
        except RuntimeError, e:
            self.main_widget().show_error(unicode(e))
        self.config()["upload_science_logs"] = self.upload_science_logs
        # Activate other components.
        for component in ["log", "database", "scheduler", "controller"]:
            try:
                self.component_manager.current(component).activate()
            except RuntimeError, e:
                self.main_widget().show_error(unicode(e))
        server = self.component_manager.current("sync_server")
        if server:
            server.activate()

    def initialise_error_handling(self):
        if sys.platform == "win32":
            error_log = os.path.join(self.config().data_dir, "error_log.txt")
            sys.stderr = file(error_log, "a")
                    
    def execute_user_plugin_dir(self):
        # Note that we put user plugins in the data_dir and not the
        # config_dir as there could be plugins (e.g. new card types) for
        # which the database does not make sense without them. 
        plugin_dir = unicode(os.path.join(self.config().data_dir, "plugins"))
        sys.path.insert(0, plugin_dir)
        for component in os.listdir(unicode(plugin_dir)):
            if component.endswith(".py"):
                try:
                    __import__(component[:-3])
                except:
                    from mnemosyne.libmnemosyne.translator import _
                    msg = _("Error when running plugin:") \
                          + "\n" + traceback_string()
                    self.main_widget().show_error(msg)

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
                self.main_widget().show_error(msg)

    def load_database(self, filename):
        if not filename:
            filename = self.config()["path"]
        filename = expand_path(filename, self.config().data_dir)
        try:
            if not os.path.exists(filename):
                self.database().new(filename)
            else:
                self.database().load(filename)
        except RuntimeError, e:
            # Making sure the GUI is in a correct state when no database is
            # loaded would require a lot of extra code, and this is only a
            # corner case anyhow. So, as workaround, we create a temporary
            # database.
            from mnemosyne.libmnemosyne.translator import _
            self.main_widget().show_error(unicode(e))
            self.main_widget().show_error(_("Creating temporary database."))
            filename = os.path.join(os.path.split(filename)[0], "___TMP___" \
                                    + self.database().suffix)
            self.database().new(filename)
        self.controller().update_title()

    def finalise(self):
        # Deactivate the sync server first, so that we make sure it reverts
        # to the right backup file in case of problems.
        server = self.component_manager.current("sync_server")
        if server:
            server.deactivate()
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
        
        
