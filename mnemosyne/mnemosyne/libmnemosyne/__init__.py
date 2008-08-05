##############################################################################
#
# libmnemosyne <Peter.Bienstman@UGent.be>
#
##############################################################################

##############################################################################
#
# This file contains functionality to initialise initialise and finalise
# libmnemosyne in a typical scenario.
#
# The initialise routine is not called automatically upon importing the
# library, so that it can be overridden to suit specific requirements.
#
##############################################################################

import logging, os, sys

import mnemosyne.version
from mnemosyne.libmnemosyne.config import config
from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.exceptions import *

# TODO: move these import to initialise, and automatically loop through
# all the contents of the directories?



log = logging.getLogger("mnemosyne")



##############################################################################
#
# initialise
#
#   Note: running user plugins is best done after the GUI has been created,
#   in order to be able to provide feedback about errors to the user.
#
##############################################################################

def initialise(basedir):

    config.initialise(basedir)
    initialise_lockfile()
    initialise_new_empty_database()        
    initialise_logging()
    initialise_error_handling()
    initialise_system_components()



##############################################################################
#
# initialise_lockfile
#
##############################################################################

def initialise_lockfile():

    lockfile = file(os.path.join(config.basedir,"MNEMOSYNE_LOCK"),'w')
    lockfile.close()



##############################################################################
#
# initialise_new_empty_database
#
##############################################################################

def initialise_new_empty_database():

    from mnemosyne.libmnemosyne.component_manager import get_database  

    filename = config["path"]

    if not os.path.exists(os.path.join(config.basedir, filename)):
        get_database().new(os.path.join(config.basedir, filename))

        

##############################################################################
#
# initialise_logging
#
##############################################################################

upload_thread = None

def initialise_logging():

    global upload_thread
    
    from mnemosyne.libmnemosyne.logger import archive_old_log, start_logging
    
    archive_old_log()
    
    start_logging()

    if config["upload_logs"]:
        upload_thread = libmnemosyne.logger.Uploader()
        upload_thread.start()
            
    log.info("Program started : Mnemosyne " + mnemosyne.version.version \
             + " " + os.name + " " + sys.platform)



##############################################################################
#
# initialise_error_handling
#
##############################################################################

def initialise_error_handling():

    # Write errors to a file (otherwise this causes problem on Windows).

    if sys.platform == "win32":
        error_log = os.path.join(basedir, "error_log.txt")
        sys.stderr = file(error_log, 'a')    



##############################################################################
#
# initialise_system_components
#
#  These are now hard coded, but if needed, an application could
#  override this.
#
##############################################################################

def initialise_system_components():

    # Database.

    from mnemosyne.libmnemosyne.databases.pickle import Pickle

    component_manager.register("database", Pickle())    


    # Scheduler.

    from mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne \
                                                   import SM2Mnemosyne
    
    component_manager.register("scheduler", SM2Mnemosyne())

    
    # Fact filters.

    from mnemosyne.libmnemosyne.filters.escape_to_html \
                                                   import EscapeToHtml
    
    component_manager.register("fact_filter", EscapeToHtml())
    

    # Card types.

    from mnemosyne.libmnemosyne.card_types.front_to_back import FrontToBack
    
    component_manager.register("card_type", FrontToBack())

    from mnemosyne.libmnemosyne.card_types.both_ways import BothWays
    
    component_manager.register("card_type", BothWays())

    from mnemosyne.libmnemosyne.card_types.three_sided import ThreeSided
    
    component_manager.register("card_type", ThreeSided())
    
    # Card Filters.

    # File formats.

    # Function hooks.

    
    # UI controllers.
    
    from mnemosyne.libmnemosyne.ui_controllers_review.SM2_controller \
                                                   import SM2Controller
    
    component_manager.register("ui_controller_review", SM2Controller())


##############################################################################
#
# initialise_user_plugins
#
##############################################################################

def initialise_user_plugins():

    basedir = config.basedir

    plugindir = unicode(os.path.join(basedir, "plugins"))
    
    sys.path.insert(0, plugindir)
    
    for plugin in os.listdir(plugindir):
        
        if plugin.endswith(".py"):
            try:
                __import__(plugin[:-3])
            except:
                raise PluginError(stack_trace=True)



##############################################################################
#
# finalise
#
##############################################################################

def finalise():

    global upload_thread

    if upload_thread:
        print "Waiting for uploader thread to stop..."
        upload_thread.join()
        print "done!"
    
    log.info("Program stopped")
    
    try:
        os.remove(os.path.join(config.basedir,"MNEMOSYNE_LOCK"))
    except OSError:
        print "Failed to remove lock file."
        print traceback_string()

