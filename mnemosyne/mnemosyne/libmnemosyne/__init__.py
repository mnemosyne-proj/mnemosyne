##############################################################################
#
# libmnemosyne <Peter.Bienstman@UGent.be>
#
##############################################################################

##############################################################################
#
# This file contains functionality to initialise libmnemosyne in a typical
# scenario. None of these are called automatically upon importing the
# library, so these routines can be overridden to suit specific
# requirements.
#
##############################################################################

from libmnemosyne.config import *

import logging
log = logging.getLogger("mnemosyne")



##############################################################################
#
# Global variables
#
##############################################################################

upload_thread = None

# TODO: needs to be cleaned up with a better mechanism to prevent overwriting
# a database which failed to load.

load_failed = False



##############################################################################
#
# initialise
#
##############################################################################

def initialise(basedir):

    global upload_thread

    config = Config(basedir)

    lockfile = file(join(basedir,"MNEMOSYNE_LOCK"),'w')
    lockfile.close()

    # TODO: Create default database if none exists?

    libmnemosyne.logger.archive_old_log()
    
    libmnemosyne.logger.start_logging()

    if get_config("upload_logs") == True:
        upload_thread = libmnemosyne.logger.Uploader()
        upload_thread.start()
            
    log.info("Program started : Mnemosyne " + libmnemosyne.version \
             + " " + os.name + " " + sys.platform)

    # Write errors to a file (otherwise this causes problem on Windows).

    if sys.platform == "win32":
        error_log = os.path.join(basedir, "error_log.txt")
        sys.stderr = file(error_log, 'a')

    # Run system plugins. (these are now hard coded, but if needed, an
    # application could override this.

    run_system_plugins()

    # Run user plugins.

    run_user_plugins()



##############################################################################
#
# run_system_plugins
#
#  These are now hard coded, but if needed, an application could
#  override this.
#
##############################################################################

def run_system_plugins():

    # Card types.

    pass

    


##############################################################################
#
# run_user_plugins
#
##############################################################################

def run_user_plugins():

    basedir = config[basedir] # TODO: improve syntax

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

    if upload_thread:
        print "Waiting for uploader thread to stop..."
        upload_thread.join()
        print "done!"
    
    log.info("Program stopped")
    
    try:
        os.remove(os.path.join(basedir,"MNEMOSYNE_LOCK"))
    except OSError:
        print "Failed to remove lock file."
        print traceback_string()

