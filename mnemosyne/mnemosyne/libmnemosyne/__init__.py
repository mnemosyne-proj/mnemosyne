#
# libmnemosyne <Peter.Bienstman@UGent.be>
#

import os
import sys

from mnemosyne.libmnemosyne.utils import expand_path, traceback_string
from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.component_manager import config, log, plugins


class Mnemosyne(object):

    """This class groups the functionality needed to initialise and finalise
    Mnemosyne in a typical scenario.

    """

    components = [ #("mnemosyne.libmnemosyne.databases.pickle", "Pickle"),
        ("mnemosyne.libmnemosyne.databases.SQLite",
         "SQLite"),               
        ("mnemosyne.libmnemosyne.configuration",
         "Configuration"),          
        ("mnemosyne.libmnemosyne.loggers.txt_logger",
         "TxtLogger"),          
        ("mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne",
         "SM2Mnemosyne"),                   
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
        ("mnemosyne.libmnemosyne.ui_controllers_main.default_main_controller",
         "DefaultMainController"),
        ("mnemosyne.libmnemosyne.ui_controllers_review.SM2_controller",
         "SM2Controller"),
        ("mnemosyne.libmnemosyne.card_types.map",
         "MapPlugin"),
        ("mnemosyne.libmnemosyne.card_types.cloze",
         "ClozePlugin"),
        ("mnemosyne.libmnemosyne.schedulers.cramming",
         "CrammingPlugin") ]
    
    def __init__(self, resource_limited=False):
        self.resource_limited = resource_limited

    # Note: the main widget should already exist, otherwise we can't give
    # feedback to the user if errors occur.

    def initialise(self, basedir, filename=None, main_widget=None):
        self.initialise_translator()
        #self.initialise_components(self.components)
        for module_name, class_name in self.components:
            exec("from %s import %s" % (module_name, class_name))
            exec("component_manager.register(%s())" % class_name)
        config().set_basedir(basedir)
        print 'set basedir 1', config().basedir
        config().set_resource_limited(self.resource_limited)
        print 'set basedir 2', config().basedir
        for module_name, class_name in self.components:
            exec("%s().initialise()" % class_name)
            
        self.initialise_main_widget(main_widget)  
        self.check_lockfile(basedir)
        #config().initialise(basedir)
        #config().resource_limited = self.resource_limited
        self.initialise_error_handling()
        self.initialise_lockfile()
        #self.initialise_logging()   
        self.load_database(filename)
        self.initialise_user_components()
        self.activate_saved_plugins()
        from mnemosyne.libmnemosyne.component_manager import ui_controller_review
        ui_controller_review().new_question()

    def initialise_translator(self):
        if not self.resource_limited:
            import gettext
            component_manager.translator = gettext.gettext
        else:
            component_manager.translator = lambda x : x

    # We still need this while we are doing the conversion from instances
    # to classes.
    
    def initialise_system_components_old(self):
        # Database.
        #from mnemosyne.libmnemosyne.databases.pickle import Pickle
        #component_manager.register(Pickle())
        from mnemosyne.libmnemosyne.databases.SQLite import SQLite
        component_manager.register(SQLite())

        # Configuration.
        from mnemosyne.libmnemosyne.configuration import Configuration
        component_manager.register(Configuration())

         # Logger.
        from mnemosyne.libmnemosyne.loggers.txt_logger import TxtLogger
        component_manager.register(TxtLogger())   

        # Scheduler.
        from mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne \
                                                       import SM2Mnemosyne
        component_manager.register(SM2Mnemosyne())

        # Card types.
        from mnemosyne.libmnemosyne.card_types.front_to_back import FrontToBack
        component_manager.register(FrontToBack())
        from mnemosyne.libmnemosyne.card_types.both_ways import BothWays
        component_manager.register(BothWays())
        from mnemosyne.libmnemosyne.card_types.three_sided import ThreeSided
        component_manager.register(ThreeSided())

        # Card type converters.
        from mnemosyne.libmnemosyne.card_types.both_ways \
             import FrontToBackToBothWays
        component_manager.register(FrontToBackToBothWays())
        from mnemosyne.libmnemosyne.card_types.both_ways \
             import BothWaysToFrontToBack
        component_manager.register(BothWaysToFrontToBack())
        from mnemosyne.libmnemosyne.card_types.three_sided \
             import FrontToBackToThreeSided
        component_manager.register(FrontToBackToThreeSided())
        from mnemosyne.libmnemosyne.card_types.three_sided \
             import BothWaysToThreeSided
        component_manager.register(BothWaysToThreeSided())
        from mnemosyne.libmnemosyne.card_types.three_sided \
             import ThreeSidedToFrontToBack
        component_manager.register(ThreeSidedToFrontToBack())
        from mnemosyne.libmnemosyne.card_types.three_sided \
             import ThreeSidedToBothWays    
        component_manager.register(ThreeSidedToBothWays())

        # Renderer.
        from mnemosyne.libmnemosyne.renderers.html_css import HtmlCss
        component_manager.register(HtmlCss())

        # Filters.
        from mnemosyne.libmnemosyne.filters.escape_to_html \
                                                       import EscapeToHtml
        component_manager.register(EscapeToHtml())
        from mnemosyne.libmnemosyne.filters.expand_paths \
                                                       import ExpandPaths
        component_manager.register(ExpandPaths())
        from mnemosyne.libmnemosyne.filters.latex import Latex
        component_manager.register(Latex())

        # File formats.


        # UI controllers.
        from mnemosyne.libmnemosyne.ui_controllers_main.default_main_controller \
                                                       import DefaultMainController
        component_manager.register(DefaultMainController())
        from mnemosyne.libmnemosyne.ui_controllers_review.SM2_controller \
                                                       import SM2Controller
        component_manager.register(SM2Controller())

        # Plugins.
        from mnemosyne.libmnemosyne.card_types.map import MapPlugin   
        component_manager.register(MapPlugin())
        from mnemosyne.libmnemosyne.card_types.cloze import ClozePlugin   
        component_manager.register(ClozePlugin())
        from mnemosyne.libmnemosyne.schedulers.cramming import CrammingPlugin   
        component_manager.register(CrammingPlugin())
        
    def initialise_components(self, components):
        for module_name, class_name in components:
            exec("from %s import %s" % (module_name, class_name))
            exec("component_manager.register(%s())" % class_name)
        for module_name, class_name in components:
            exec("%s().initialise()" % class_name)

    def initialise_main_widget(self, main_widget):
        if not main_widget:
            from mnemosyne.libmnemosyne.ui_components.main_widget import \
                 MainWidget       
            main_widget = MainWidget()
        from mnemosyne.libmnemosyne.component_manager import ui_controller_main
        ui_controller_main().widget = main_widget
        main_widget.init_review_widget()
        main_widget.after_mnemosyne_init()

    def check_lockfile(self, basedir):
        if os.path.exists(os.path.join(basedir, "MNEMOSYNE_LOCK")):
            from mnemosyne.libmnemosyne.component_manager import \
                 ui_controller_main
            _ = component_manager.translator
            status = ui_controller_main().widget.question_box(
                _("Either Mnemosyne didn't shut down properly,") + "\n" +
                _("or another copy of Mnemosyne is still running.") + "\n" +
                _("Continuing in the latter case could lead to data loss!"),      
                _("&Exit"), _("&Continue"), "")
            if status == 0:
                sys.exit()
                
    def initialise_error_handling(self):

        """Write errors to a file (otherwise this causes problems on Windows)."""

        if sys.platform == "win32":
            error_log = os.path.join(config().basedir, "error_log.txt")
            sys.stderr = file(error_log, "a")
            
    def initialise_lockfile(self):
        lockfile = file(os.path.join(config().basedir, "MNEMOSYNE_LOCK"), 'w')
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
        except RuntimeError, e:
            # Making sure the GUI is in a correct state when no database is
            # loaded would require a lot of extra code, and this is only a
            # corner case anyhow. So, as workaround, we create a temporary
            # database.
            
            _ = component_manager.translator
            ui_controller_main().widget.error_box(str(e))
            ui_controller_main().widget.error_box\
                                          (_("Creating temporary deck."))
            filename = os.path.join(os.path.split(filename)[0], "___TMP___" \
                                    + database().suffix)
            database().new(filename)
        ui_controller_main().update_title()

    def initialise_user_components(self):
        basedir = config().basedir
        # The contents of the 'plugin' dir could contain both plugins and
        # as well as other components, but we needn't expose this subtlety to
        # the user.
        componentdir = unicode(os.path.join(basedir, "plugins"))
        sys.path.insert(0, componentdir)
        for component in os.listdir(componentdir):
            if component.endswith(".py"):
                try:
                    __import__(component[:-3])
                except:
                    _ = component_manager.translator
                    from mnemosyne.libmnemosyne.component_manager import \
                         ui_controller_main
                    msg = _("Error when running plugin:") \
                          + "\n" + traceback_string()
                    ui_controller_main().widget.error_box(msg)

    def activate_saved_plugins(self):
        for plugin in config()["active_plugins"]:
            try:
                for p in plugins():
                    if plugin == p.__class__:
                        p.activate()
                        break
            except:
                _ = component_manager.translator
                from mnemosyne.libmnemosyne.component_manager import \
                     ui_controller_main
                msg = _("Error when running plugin:") \
                      + "\n" + traceback_string()
                ui_controller_main().widget.error_box(msg)

    def finalise(self):
        _ = component_manager.translator
        config().save()
        component_manager.unregister_all()
        #if self.upload_thread:
        #    print _("Waiting for uploader thread to stop...")
        #    self.upload_thread.join()
        #    print _("done!")
        #log().program_stopped()
        try:
            os.remove(os.path.join(config().basedir, "MNEMOSYNE_LOCK"))
        except OSError:
            print _("Failed to remove lock file.") + "\n" + traceback_string()
        component_manager.components = {}
        component_manager.card_type_by_id = {}
