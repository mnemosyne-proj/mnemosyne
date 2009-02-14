#
# libmnemosyne <Peter.Bienstman@UGent.be>
#

"""This file contains functionality to initialise initialise and finalise
libmnemosyne in a typical scenario.

The initialise routine is not called automatically upon importing the
library, so that it can be overridden to suit specific requirements.

"""

import os
import sys

from mnemosyne.libmnemosyne.exceptions import PluginError, traceback_string
from mnemosyne.libmnemosyne.component_manager import config, log, plugins
from mnemosyne.libmnemosyne.component_manager import component_manager


def initialise(basedir):
    
    """Note: running user plugins is best done after the GUI has been created,
    in order to be able to provide feedback about errors to the user."""

    initialise_system_components()
    config().initialise(basedir)
    initialise_logging()
    initialise_lockfile()
    initialise_new_empty_database()
    initialise_error_handling()
    initialise_user_plugins()
    activate_saved_plugins()


def initialise_lockfile():
    lockfile = file(os.path.join(config().basedir, "MNEMOSYNE_LOCK"), 'w')
    lockfile.close()
    

def initialise_new_empty_database():
    from mnemosyne.libmnemosyne.component_manager import database
    filename = config()["path"]
    if not os.path.exists(os.path.join(config().basedir, filename)):
        database().new(os.path.join(config().basedir, filename))


upload_thread = None
def initialise_logging():
    global upload_thread
    from mnemosyne.libmnemosyne.log_uploader import LogUploader
    log().archive_old_log()
    log().start_logging()
    log().program_started()
    if config()["upload_logs"]:
        upload_thread = LogUploader()
        upload_thread.start()


def initialise_error_handling():
    
    """Write errors to a file (otherwise this causes problems on Windows)."""
    
    if sys.platform == "win32":
        error_log = os.path.join(basedir, "error_log.txt")
        sys.stderr = file(error_log, 'a')


def initialise_system_components():
    
    """These are now hard coded, but if needed, an application could 
    override this.
    
    """
    
    # Configuration.
    from mnemosyne.libmnemosyne.configuration import Configuration
    component_manager.register("config", Configuration())
    
     # Logger.
    from mnemosyne.libmnemosyne.loggers.txt_logger import TxtLogger
    component_manager.register("log", TxtLogger())   
    
    # Database.
    from mnemosyne.libmnemosyne.databases.pickle import Pickle
    component_manager.register("database", Pickle())
    
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


def initialise_user_plugins():
    basedir = config().basedir
    plugindir = unicode(os.path.join(basedir, "plugins"))
    sys.path.insert(0, plugindir)
    for plugin in os.listdir(plugindir):
        if plugin.endswith(".py"):
            try:
                __import__(plugin[:-3])
            except:
                raise PluginError(stack_trace=True)


def activate_saved_plugins():
    for plugin in config()["active_plugins"]:
        try:
            for p in plugins():
                if plugin == p.__class__:
                    p.activate()
                    break
        except:
            raise PluginError(stack_trace=True)


def finalise():
    global upload_thread
    if upload_thread:
        print "Waiting for uploader thread to stop..."
        upload_thread.join()
        print "done!"
    log().program_stopped()
    try:
        os.remove(os.path.join(config().basedir,"MNEMOSYNE_LOCK"))
    except OSError:
        print "Failed to remove lock file."
        print traceback_string()
