##############################################################################
#
# libmnemosyne <Peter.Bienstman@UGent.be>
#
##############################################################################

# global TODO:
# mixin plugin class?
# increase size of non latin, sound: make into GUI level filter
# private variables: prefix_


import gettext
_ = gettext.gettext

import mnemosyne.version

logger = logging.getLogger("mnemosyne")


# TODO: check if basedir code can be improved.

##############################################################################
#
# migrate_basedir
#
##############################################################################

def migrate_basedir(old, new):

    if os.path.islink(_old_basedir):

        print _("Not migrating %s to %s because ") % (old, new) \
                + _("it is a symlink.")
        return

    # Migrate Mnemosyne basedir to new location and create a symlink from 
    # the old one. The other way around is a bad idea, because a user
    # might decide to clean up the old obsolete directory, not realising
    # the new one is a symlink.
        
    print _("Migrating %s to %s") % (old, new)
    try:
        os.rename(old, new)
    except OSError:
        print _("Move failed, manual migration required.")
        return

    # Now create a symlink for backwards compatibility.

    try:
        os.symlink(new, old)
    except OSError:
        print _("Symlink creation failed (only needed for older versions).")



##############################################################################
#
# Create basedir
#
##############################################################################

if sys.platform == 'darwin':

    _old_basedir = os.path.join(os.path.expanduser("~"), ".mnemosyne")
    basedir = os.path.join(os.path.expanduser("~"), "Library", "Mnemosyne")

    if not os.path.exists(basedir) and os.path.exists(_old_basedir):
        migrate_basedir(_old_basedir, basedir)

else:
        
    _old_basedir = None
    basedir = os.path.join(os.path.expanduser("~"), ".mnemosyne")



##############################################################################
#
# get_basedir
#
##############################################################################

def get_basedir():
    return basedir

# TODO: remove global imports
# Move to a more logical position after get_basedir import issue is resolved.

from mnemosyne.libmnemosyne.exceptions import *
from mnemosyne.libmnemosyne.card import list_is_loaded
from mnemosyne.libmnemosyne.start_date import *
from mnemosyne.libmnemosyne.config import load_config, get_config, set_config


##############################################################################
#
# Global variables
#
##############################################################################


upload_thread = None
load_failed = False



##############################################################################
#
# initialise
#
##############################################################################

def initialise(basedir_ = None):

    import mnemosyne_log

    global upload_thread, load_failed, basedir

    load_failed = False

    join   = os.path.join
    exists = os.path.exists

    # Set default paths.

    if basedir_ != None:
        basedir = basedir_

    if not exists(basedir):
        os.mkdir(basedir)

    if not exists(join(basedir, "history")):
        os.mkdir(join(basedir, "history"))

    if not exists(join(basedir, "latex")):
        os.mkdir(join(basedir, "latex"))
        
    if not exists(join(basedir, "plugins")):
        os.mkdir(join(basedir, "plugins"))
        
    if not exists(join(basedir, "backups")):
        os.mkdir(join(basedir, "backups"))
         
    if not exists(join(basedir, "config")):
        init_config()
        save_config()    
     
    if not exists(join(basedir, "default.mem")):
        new_database(join(basedir, "default.mem"))
    
    lockfile = file(join(basedir,"MNEMOSYNE_LOCK"),'w')
    lockfile.close()

    load_config()

    mnemosyne_log.archive_old_log()
    
    mnemosyne_log.start_logging()

    if get_config("upload_logs") == True:
        upload_thread = mnemosyne_log.Uploader()
        upload_thread.start()

    # Create default latex preamble and postamble.

    latexdir  = join(basedir,  "latex")
    preamble  = join(latexdir, "preamble")
    postamble = join(latexdir, "postamble")
    dvipng    = join(latexdir, "dvipng")
    
    if not os.path.exists(preamble):
        f = file(preamble, 'w')
        print >> f, "\\documentclass[12pt]{article}"
        print >> f, "\\pagestyle{empty}" 
        print >> f, "\\begin{document}"
        f.close()

    if not os.path.exists(postamble):
        f = file(postamble, 'w')
        print >> f, "\\end{document}"
        f.close()

    if not os.path.exists(dvipng):
        f = file(dvipng, 'w')
        print >> f, "dvipng -D 200 -T tight tmp.dvi" 
        f.close()

    # Create default config.py.
    
    configfile = os.path.join(basedir, "config.py")
    if not os.path.exists(configfile):
        f = file(configfile, 'w')
        print >> f, \
"""# Mnemosyne configuration file.

# Align question/answers to the left (True/False)
left_align = False

# Keep detailed logs (True/False).
keep_logs = True

# Upload server. Only change when prompted by the developers.
upload_server = "mnemosyne-proj.dyndns.org:80"

# Set to True to prevent you from accidentally revealing the answer
# when clicking the edit button.
only_editable_when_answer_shown = False

# The translation to use, e.g. 'de' for German (including quotes).
# See http://www.mnemosyne-proj.org/help/translations.php for a list
# of available translations.
# If locale is set to None, the system's locale will be used.
locale = None

# The number of daily backups to keep. Set to -1 for no limit.
backups_to_keep = 5

# The moment the new day starts. Defaults to 3 am. Could be useful to
# change if you are a night bird.
day_starts_at = 3"""
        f.close()        
        
    logger.info("Program started : Mnemosyne " + mnemosyne.version.version \
                + " " + os.name + " " + sys.platform)

    # Write errors to a file (otherwise this causes problem on Windows).

    if sys.platform == "win32":
        error_log = os.path.join(basedir, "error_log.txt")
        sys.stderr = file(error_log, 'a')

        


##############################################################################
#
# run_user_plugins
#
##############################################################################

def run_user_plugins():

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
        print _("Waiting for uploader thread to stop...")
        upload_thread.join()
        print _("done!")
    
    logger.info("Program stopped")
    
    try:
        os.remove(os.path.join(basedir,"MNEMOSYNE_LOCK"))
    except OSError:
        print _("Failed to remove lock file.")
        print traceback_string()

