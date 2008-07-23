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
from mnemosyne.libmnemosyne.plugin_manager import plugin_manager

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
    initialise_system_plugins()



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

    from mnemosyne.libmnemosyne.plugin_manager import get_database  

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
# initialise_system_plugins
#
#  These are now hard coded, but if needed, an application could
#  override this.
#
##############################################################################

def initialise_system_plugins():

    # Database.

    from mnemosyne.libmnemosyne.databases.pickle import Pickle

    plugin_manager.register_plugin("database", Pickle())    

    # UI controllers.
    
    from mnemosyne.libmnemosyne.ui_controllers.SM2_controller \
                                                   import SM2Controller
    
    plugin_manager.register_plugin("ui_controller", SM2Controller())

    # Scheduler.

    from mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne \
                                                   import SM2Mnemosyne
    
    plugin_manager.register_plugin("scheduler", SM2Mnemosyne())    
    
    # Card types.

    # These are registered in the GUI, because it's easier to do so
    # once the card widgets are known.
    
    # Filters.

    # File formats.

    # Function hooks.



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

