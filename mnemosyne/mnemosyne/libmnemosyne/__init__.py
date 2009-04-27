#
# libmnemosyne <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

import os
import sys

from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.exceptions import MnemosyneError
from mnemosyne.libmnemosyne.exceptions import LoadErrorCreateTmp
from mnemosyne.libmnemosyne.exceptions import PluginError, traceback_string
from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.component_manager import config, log, plugins

    
class Mnemosyne(object):

    """This class groups the functionality needed to initialise and finalise
    Mnemosyne in a typical scenario.

    """

    def __init__(self, resource_limited=False):
        self.resource_limited = resource_limited
        self.upload_thread = None

    def initialise(self, basedir, filename=None, main_widget=None):
        self.initialise_error_handling()
        self.initialise_system_components()
        self.initialise_main_widget(main_widget)  
        self.check_lockfile(basedir)
        config().initialise(basedir)
        config().resource_limited = self.resource_limited
        self.initialise_lockfile(basedir)
        self.initialise_logging()   
        self.load_database(filename)
        self.initialise_user_plugins()
        self.activate_saved_plugins()
        from mnemosyne.libmnemosyne.component_manager import ui_controller_review
        ui_controller_review().new_question()

    def initialise_error_handling(self):

        """Write errors to a file (otherwise this causes problems on Windows)."""

        if sys.platform == "win32":
            error_log = os.path.join(config().basedir, "error_log.txt")
            sys.stderr = file(error_log, "a")

    def initialise_system_components(self):
        # Database.
        #from mnemosyne.libmnemosyne.databases.pickle import Pickle
        #component_manager.register("database", Pickle())
        from mnemosyne.libmnemosyne.databases.SQLite import SQLite
        component_manager.register("database", SQLite())

        # Configuration.
        from mnemosyne.libmnemosyne.configuration import Configuration
        component_manager.register("config", Configuration())

         # Logger.
        from mnemosyne.libmnemosyne.loggers.txt_logger import TxtLogger
        component_manager.register("log", TxtLogger())   

        # Scheduler.
        from mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne \
                                                       import SM2Mnemosyne
        component_manager.register("scheduler", SM2Mnemosyne())

        # Card types.
        from mnemosyne.libmnemosyne.card_types.front_to_back import FrontToBack
        component_manager.register("card_type", FrontToBack())
        from mnemosyne.libmnemosyne.card_types.both_ways import BothWays
        component_manager.register("card_type", BothWays())
        from mnemosyne.libmnemosyne.card_types.three_sided import ThreeSided
        component_manager.register("card_type", ThreeSided())

        # Card type converters.
        from mnemosyne.libmnemosyne.card_types.both_ways \
             import FrontToBackToBothWays
        component_manager.register("card_type_converter", FrontToBackToBothWays(),
                                   used_for=(FrontToBack, BothWays))  
        from mnemosyne.libmnemosyne.card_types.both_ways \
             import BothWaysToFrontToBack
        component_manager.register("card_type_converter", BothWaysToFrontToBack(),
                                   used_for=(BothWays, FrontToBack))
        from mnemosyne.libmnemosyne.card_types.three_sided \
             import FrontToBackToThreeSided
        component_manager.register("card_type_converter", FrontToBackToThreeSided(),
                                   used_for=(FrontToBack, ThreeSided))
        from mnemosyne.libmnemosyne.card_types.three_sided \
             import BothWaysToThreeSided
        component_manager.register("card_type_converter", BothWaysToThreeSided(),
                                   used_for=(BothWays, ThreeSided))
        from mnemosyne.libmnemosyne.card_types.three_sided \
             import ThreeSidedToFrontToBack
        component_manager.register("card_type_converter", ThreeSidedToFrontToBack(),
                                   used_for=(ThreeSided, FrontToBack))
        from mnemosyne.libmnemosyne.card_types.three_sided \
             import ThreeSidedToBothWays    
        component_manager.register("card_type_converter", ThreeSidedToBothWays(),
                                   used_for=(ThreeSided, BothWays))

        # Renderer.
        from mnemosyne.libmnemosyne.renderers.html_css import HtmlCss
        component_manager.register("renderer", HtmlCss())

        # Filters.
        from mnemosyne.libmnemosyne.filters.escape_to_html \
                                                       import EscapeToHtml
        component_manager.register("filter", EscapeToHtml())
        from mnemosyne.libmnemosyne.filters.expand_paths \
                                                       import ExpandPaths
        component_manager.register("filter", ExpandPaths())
        from mnemosyne.libmnemosyne.filters.latex import Latex
        component_manager.register("filter", Latex())

        # File formats.


        # UI controllers.
        from mnemosyne.libmnemosyne.ui_controllers_main.default_main_controller \
                                                       import DefaultMainController
        component_manager.register("ui_controller_main", DefaultMainController())
        from mnemosyne.libmnemosyne.ui_controllers_review.SM2_controller \
                                                       import SM2Controller
        component_manager.register("ui_controller_review", SM2Controller())

        # Plugins.
        from mnemosyne.libmnemosyne.card_types.map import Map   
        component_manager.register("plugin", Map())
        from mnemosyne.libmnemosyne.card_types.cloze import Cloze   
        component_manager.register("plugin", Cloze())

    def initialise_main_widget(self, main_widget):
        if not main_widget:
            from mnemosyne.libmnemosyne.main_widget import MainWidget       
            main_widget = MainWidget()
        from mnemosyne.libmnemosyne.component_manager import ui_controller_main
        ui_controller_main().widget = main_widget
        main_widget.init_review_widget()
        main_widget.after_mnemosyne_init()

    def check_lockfile(self, basedir):
        if os.path.exists(os.path.join(basedir, "MNEMOSYNE_LOCK")):
            from mnemosyne.libmnemosyne.component_manager import ui_controller_main
            status = ui_controller_main().widget.question_box(
                _("Either Mnemosyne didn't shut down properly,") + "\n" +
                _("or another copy of Mnemosyne is still running.") + "\n" +
                _("Continuing in the latter case could lead to data loss!"),      
                _("&Exit"), _("&Continue"), "")
            if status == 0:
                sys.exit()

    def initialise_lockfile(self, basedir):
        lockfile = file(os.path.join(basedir, "MNEMOSYNE_LOCK"), 'w')
        lockfile.close()

    def initialise_logging(self):
        log().archive_old_log()
        log().start_logging()
        log().program_started()
        if config()["upload_logs"] and not self.resource_limited:
            from mnemosyne.libmnemosyne.log_uploader import LogUploader
            self.upload_thread = LogUploader()
            self.upload_thread.start()

    def load_database(self, filename):
        from mnemosyne.libmnemosyne.component_manager import database
        from mnemosyne.libmnemosyne.component_manager import ui_controller_main
        if not filename:
            filename = config()["path"]
        filename = expand_path(filename, config().basedir)
        try:
            if not os.path.exists(filename):
                database().new(filename)
            else:
                database().load(filename)
        except MnemosyneError, e:
            ui_controller_main().widget.error_box(e)
            ui_controller_main().widget.error_box(LoadErrorCreateTmp())
            filename = os.path.join(os.path.split(filename)[0],"___TMP___" \
                                    + database().suffix)
            database().new(filename)

    def initialise_user_plugins(self):
        from mnemosyne.libmnemosyne.component_manager import ui_controller_main
        basedir = config().basedir
        plugindir = unicode(os.path.join(basedir, "plugins"))
        sys.path.insert(0, plugindir)
        for plugin in os.listdir(plugindir):
            if plugin.endswith(".py"):
                try:
                    __import__(plugin[:-3])
                except:
                    ui_controller_main().widget.\
                                    error_box(PluginError(stack_trace=True))

    def activate_saved_plugins(self):
        from mnemosyne.libmnemosyne.component_manager import ui_controller_main
        for plugin in config()["active_plugins"]:
            try:
                for p in plugins():
                    if plugin == p.__class__:
                        p.activate()
                        break
            except:
                ui_controller_main().widget.\
                                    error_box(PluginError(stack_trace=True))

    def finalise(self):
        config().save()
        if self.upload_thread:
            print _("Waiting for uploader thread to stop...")
            self.upload_thread.join()
            print _("done!")
        log().program_stopped()
        try:
            os.remove(os.path.join(config().basedir, "MNEMOSYNE_LOCK"))
        except OSError:
            print _("Failed to remove lock file.")
            print traceback_string()
        component_manager.components = {}
        component_manager.card_type_by_id = {}
