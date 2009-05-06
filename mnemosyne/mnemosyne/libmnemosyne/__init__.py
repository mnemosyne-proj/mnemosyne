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
        config().set_resource_limited(self.resource_limited)
        for module_name, class_name in self.components:
            exec("%s().initialise()" % class_name)
            
        self.initialise_main_widget(main_widget)  
        self.check_lockfile(basedir)
        self.initialise_error_handling()
        self.initialise_lockfile()  
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

    def remove_lockfile(self):
        _ = component_manager.translator
        try:
            os.remove(os.path.join(config().basedir, "MNEMOSYNE_LOCK"))
        except OSError:
            print _("Failed to remove lock file.") + "\n" + traceback_string()

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
        self.remove_lockfile()
        component_manager.unregister_all()
        

