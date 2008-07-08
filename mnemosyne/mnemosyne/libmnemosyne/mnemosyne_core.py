##############################################################################
#
# Mnemosyne core <Peter.Bienstman@UGent.be>
#
##############################################################################

import gettext
_ = gettext.gettext

import random, time, os, string, sys, cPickle, md5, struct, logging, re
import shutil, datetime, bz2, gzip, copy, cStringIO 

# TODO: remove global imports

from mnemosyne.libmnemosyne.exceptions import *
from mnemosyne.libmnemosyne.card_types import *
from mnemosyne.libmnemosyne.card import *
from mnemosyne.libmnemosyne.fact import *
from mnemosyne.libmnemosyne.category import *

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

def get_basedir():
    return basedir



##############################################################################
#
# Global variables
#
##############################################################################

time_of_start = None
import_time_of_start = None
days_since_start = None

thinking_time = 0
time_of_last_question = 0

upload_thread = None
load_failed = False

revision_queue = []


config = {}



##############################################################################
#
# Register plugin hooks.
#
##############################################################################

plugin_hooks = {}

def register_plugin_hook(name, plugin_function):

    global plugin_hooks

    plugin_hooks[name] = plugin_function



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
# init_config
#
# TODO: make sure this does not get called when upgrading
#
##############################################################################

def init_config():
    global config
 
    config.setdefault("first_run", True)
    config.setdefault("path", "default.mem")
    config.setdefault("import_dir", basedir)
    config.setdefault("import_format", "XML")
    config.setdefault("reset_learning_data_import", False)
    config.setdefault("export_dir", basedir)
    config.setdefault("export_format", "XML")
    config.setdefault("reset_learning_data_export", False)    
    config.setdefault("import_img_dir", basedir)
    config.setdefault("import_sound_dir", basedir)    
    config.setdefault("user_id",md5.new(str(random.random())).hexdigest()[0:8])
    config.setdefault("keep_logs", True)
    config.setdefault("upload_logs", True)
    config.setdefault("upload_server", "mnemosyne-proj.dyndns.org:80")    
    config.setdefault("log_index", 1)
    config.setdefault("hide_toolbar", False)
    config.setdefault("QA_font", None)
    config.setdefault("list_font", None)
    config.setdefault("left_align", False)
    config.setdefault("non_latin_font_size_increase", 0)
    config.setdefault("check_duplicates_when_adding", True)
    config.setdefault("allow_duplicates_in_diff_cat", True)
    config.setdefault("grade_0_cards_at_once", 5)
    config.setdefault("last_add_vice_versa", False)
    config.setdefault("last_add_category", "<default>")
    config.setdefault("3_sided_input", False) # TODO: remove
    config.setdefault("column_0_width", None)
    config.setdefault("column_1_width", None)
    config.setdefault("column_2_width", None)    
    config.setdefault("sort_column", None)
    config.setdefault("sort_order", None)    
    config.setdefault("show_intervals", "never")
    config.setdefault("only_editable_when_answer_shown", False)
    config.setdefault("locale", None)
    config.setdefault("show_daily_tips", True)
    config.setdefault("tip", 0)
    config.setdefault("backups_to_keep", 5)
    config.setdefault("day_starts_at", 3)
	
    # Update paths if the location has migrated.

    if _old_basedir:

        for key in ['import_dir', 'export_dir', 'import_img_dir',
                    'import_sound_dir']:

            if config[key] == _old_basedir:
                config[key] = basedir
				
    # Recreate user id and log index from history folder in case the
    # config file was accidentally deleted.

    if get_config("log_index") == 1:
    
        dir = os.listdir(unicode(os.path.join(basedir, "history")))
        history_files = [x for x in dir if x[-4:] == ".bz2"]
        history_files.sort()
        if history_files:
            last = history_files[-1]
            user, index = last.split('_')
            index = int(index.split('.')[0])+1



##############################################################################
#
# get_config
#
##############################################################################

def get_config(key):
    return config[key]



##############################################################################
#
# set_config
#
##############################################################################

def set_config(key, value):
    global config
    config[key] = value



##############################################################################
#
# load_config
#
##############################################################################

def load_config():
    global config

    # Read pickled config object.

    try:
        config_file = file(os.path.join(basedir, "config"), 'rb')
        for k,v in cPickle.load(config_file).itercards():
            config[k] = v
    except:
        pass

    # Set defaults.

    init_config()

    # Load user config file.

    sys.path.insert(0, basedir)

    config_file_c = os.path.join(basedir, "config.pyc")
    if os.path.exists(config_file_c):
        os.remove(config_file_c)
    
    config_file = os.path.join(basedir, "config.py")

    if os.path.exists(config_file):
        try:
            import config as _config
            for var in dir(_config):
                if var in config.keys():
                    set_config(var, getattr(_config, var))
        except:
            raise ConfigError(stack_trace=True)



##############################################################################
#
# save_config
#
##############################################################################

def save_config():

    try:
        config_file = file(os.path.join(basedir, "config"), 'wb')
        cPickle.dump(config, config_file)
    except:
        raise SaveError()



##############################################################################
#
# run_plugins
#
##############################################################################

def run_plugins():

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
# StartTime
#
# TODO: remove obsolete code?
#
##############################################################################

class StartTime:

    def __init__(self, start_time):
        
        h = get_config("day_starts_at")

        # Compatibility code for older versions.
        
        t = time.localtime(start_time) # In seconds from Unix epoch in UTC.
        self.time = time.mktime([t[0],t[1],t[2], h,0,0, t[6],t[7],t[8]])

        # New implementation.

        self.date = datetime.datetime.fromtimestamp(self.time).date()

    # Since this information is frequently needed, we calculate it once
    # and store it in a global variable, which is updated when the database
    # loads and in rebuild_revision_queue.
    
    def update_days_since(self):
        
        global days_since_start

        # If this is a database with the obsolete time stamp, update it
        # with a date attribute. The adjustment for 'day_starts_at' is not
        # relevant here, as we only store the date part.
        
        if not getattr(self, 'date', None):
            self.date = datetime.datetime.fromtimestamp(self.time).date()
        
        # Now calculate the difference in days.
        
        h = get_config("day_starts_at")
        adjusted_now = datetime.datetime.now() - datetime.timedelta(hours=h)
        dt = adjusted_now.date() - self.date
        
        days_since_start = dt.days



##############################################################################
#
# new_database
#
##############################################################################

def new_database(path):

    global config, time_of_start, load_failed

    if len(cards) > 0:
        unload_database()

    load_failed = False

    time_of_start = StartTime(time.time())
    config["path"] = path

    logger.info("New database")

    save_database(contract_path(path, basedir))



##############################################################################
#
# load_database
#
##############################################################################

database_header_line \
    = "--- Mnemosyne Data Base --- Format Version %s ---" \
      % mnemosyne.version.dbVersion

def load_database(path):

    global config, time_of_start, categories, category_by_name, cards
    global load_failed
  
    path = expand_path(path, basedir)
        
    if list_is_loaded():
        unload_database()

    if not os.path.exists(path):
        load_failed = True
        raise LoadError()

    try:
        infile = file(path, 'rb')
        header_line = infile.readline().rstrip()
            
        if not header_line.startswith("--- Mnemosyne Data Base"):
            infile = file(path, 'rb')

        db = cPickle.load(infile)

        time_of_start = db[0]
        categories    = db[1]
        cards         = db[2]
        
        infile.close()

        time_of_start.update_days_since()

        load_failed = False

    except:
        load_failed = True
        
        raise InvalidFormatError(stack_trace=True)

    for c in categories:
        category_by_name[c.name] = c
    for c in categories:
        remove_category_if_unused(c)

    config["path"] = contract_path(path, basedir)

    logger.info("Loaded database %d %d %d", scheduled_cards(), \
                non_memorised_cards(), number_of_cards())

    if "after_load" in plugin_hooks:
        plugin_hooks["after_load"]()



##############################################################################
#
# save_database
#
##############################################################################

def save_database(path):

    global config

    path = expand_path(path, basedir)

    if load_failed == True: # Don't erase a database which failed to load.
        return
        
    try:
        
        # Write to a backup file first, as shutting down Windows can
        # interrupt the dump command and corrupt the database.
        
        outfile = file(path + "~", 'wb')
        
        print >> outfile, database_header_line

        db = [time_of_start, categories, cards]
        cPickle.dump(db, outfile)

        outfile.close()

        shutil.move(path + "~", path) # Should be atomic.
        
    except:
        raise SaveError()

    config["path"] = contract_path(path, basedir)



##############################################################################
#
# unload_database
#
##############################################################################

def unload_database():

    global cards, revision_queue, categories, category_by_name
        
    save_database(config["path"])
    
    logger.info("Saved database %d %d %d", scheduled_cards(), \
                non_memorised_cards(), number_of_cards())        
    cards = []
    revision_queue = []
        
    categories = []
    category_by_name = {}
    
    return True



##############################################################################
#
# backup_database
#
##############################################################################

def backup_database():

    if number_of_cards() == 0:
        return

    backupdir = unicode(os.path.join(basedir, "backups"))

    # Export to XML. Create only a single file per day.

    db_name = os.path.basename(config["path"])[:-4]

    filename = db_name + "-" +\
               datetime.date.today().strftime("%Y%m%d") + ".xml"
    filename = os.path.join(backupdir, filename)

    export_XML(filename, get_category_names(), reset_learning_data=False)

    # Compress the file.

    f = gzip.GzipFile(filename + ".gz", 'w')
    for l in file(filename):
        f.write(l)
    f.close()

    os.remove(filename)

    # Only keep the last logs.

    if get_config("backups_to_keep") < 0:
        return

    files = [f for f in os.listdir(backupdir) if f.startswith(db_name + "-")]
    files.sort()
    if len(files) > get_config("backups_to_keep"):
        os.remove(os.path.join(backupdir, files[0]))

    

##############################################################################
#
# list_is_loaded
#
##############################################################################

def list_is_loaded():
    return len(cards) != 0



##############################################################################
#
# expand_path
#
#   Make relative path absolute and normalise slashes.
#
##############################################################################

def expand_path(p, prefix=None):
    
    # By default, make paths relative to the database location.

    if prefix == None:
        prefix = os.path.dirname(get_config("path"))

    # If there was no dirname in the last statement, it was a relative
    # path and we set the prefix to the basedir.
    
    if prefix == '':
        prefix = get_basedir()

    if (    ( (len(p) > 1) and p[0] == "/") \
         or ( (len(p) > 2) and p[1] == ":") ): # Unix or Windows absolute path.
        return os.path.normpath(p)
    else:  
        return os.path.normpath(os.path.join(prefix, p))



##############################################################################
#
# contract_path
#
#   Make absolute path relative and normalise slashes.
#
##############################################################################

def contract_path(p, prefix=None):

    # By default, make paths relative to the database location.

    if prefix == None:
        prefix = os.path.dirname(get_config("path"))

    # If there was no dirname in the last statement, it was a relative
    # path and we set the prefix to the basedir.
    
    if prefix == '':
        prefix = get_basedir()

    if (    ( (len(p) > 1) and p[0] == "/") \
         or ( (len(p) > 2) and p[1] == ":") ): # Unix or Windows absolute path.
        try:
            return p.split(prefix)[1][1:]
        except:
            return p            
    else:
        return p



##############################################################################
#
# set_non_latin_font_size
#
#   Useful to increase size of non-latin unicode characters.
#
##############################################################################

def set_non_latin_font_size(old_string, font_size):

    def in_latin_plane(ucode):
        
        # Basic Latin (US-ASCII): {U+0000..U+007F}
        # Latin-1 (ISO-8859-1): {U+0080..U+00FF}
        # Latin Extended: {U+0100..U+024F}
        # IPA Extensions: {U+0250..U+02AF}\
        # Spacing Modifier Letters: {U+02B0..U+02FF}
        # Combining Diacritical Marks: {U+0300..U+036F}  
        # Greek: {U+0370..U+03FF}
        # Cyrillic: {U+0400..U+04FF}
        # Latin Extended Additional
        # Greek Extended
        
        plane = ((0x0000,0x04FF), (0x1E00,0x1EFF), (0x1F00,0x1FFF))
        for i in plane:
            if ucode > i[0] and ucode < i[1]:
                return True
        return False

    if old_string == "":
        return old_string
    
    new_string = ""
    in_tag = False
    in_protect = 0
    in_unicode_substring = False
    
    for i in range(len(old_string)):
        if not in_latin_plane(ord(old_string[i])) and not in_protect:

            # Don't substitute within XML tags, or file names get messed up.
            
            if in_tag or in_unicode_substring == True:
                new_string += old_string[i]
            else:
                in_unicode_substring = True
                new_string += '<font style=\"font-size:' + str(font_size) +\
                              'pt\">' + old_string[i]
        else:
            
            # First check for tag start/end.
            
            if old_string[i] == '<':
                in_tag = True
            elif old_string[i] == '>':
                in_tag = False

            # Test for <protect> tags.

            if old_string[i:].startswith('<protect>'):
                in_protect += 1
            elif old_string[i:].startswith('</protect>'):
                in_protect = max(0, in_protect - 1)

            # Close tag.
               
            if in_unicode_substring == True:
                in_unicode_substring = False
                new_string += '</font>' + old_string[i]
            else:
                new_string += old_string[i]
                
    # Make sure to close the last tag.
              
    if not in_latin_plane(ord(old_string[-1])) and not in_protect:
        new_string += '</font>'

    # Now we can strip all the <protect> tags.

    new_string = new_string.replace('<protect>', '').replace('</protect>', '')
    
    return new_string



##############################################################################
#
# process_latex
#
##############################################################################

def process_latex(latex_command):

    latex_command = latex_command.replace("&lt;", "<") 

    error_str = _("<b>Problem with latex. Are latex and dvipng installed?</b>")
    
    latexdir  = os.path.join(basedir, "latex")
    imag_name = md5.new(latex_command.encode("utf-8")).hexdigest() + ".png"
    imag_file = os.path.join(latexdir, imag_name)

    if not os.path.exists(imag_file):
        
        os.chdir(latexdir)
        
        if os.path.exists("tmp1.png"):
            os.remove("tmp1.png")
    
        f = file("tmp.tex", 'w')
        for line in file("preamble"): 
            print >> f, line,
        print >> f, latex_command.encode("utf-8")
        for line in file("postamble"): 
            print >> f, line,       
        f.close()

        os.system("latex -interaction=nonstopmode tmp.tex "+\
                  " 2>&1 1>latex_out.txt")

        f = file("dvipng")       
        os.system(f.readline().rstrip())
        f.close()

        if not os.path.exists("tmp1.png"):
            return error_str

        shutil.copy("tmp1.png", imag_name)

    return "<img src=\"" + latexdir + "/"+imag_name+"\" align=middle>"



##############################################################################
#
# preprocess
#
#   Do some text preprocessing of Q/A strings and handle special tags.
#
##############################################################################

# The regular expressions to find the latex tags are global so they don't
# get recompiled all the time. match.group(1) identifies the text between
# the tags (thanks to the parentheses), match.group() is the text plus the
# tags.

re1 = re.compile(r"<latex>(.+?)</latex>", re.DOTALL | re.IGNORECASE)
re2 = re.compile(r"<\$>(.+?)</\$>",       re.DOTALL | re.IGNORECASE)
re3 = re.compile(r"<\$\$>(.+?)</\$\$>",   re.DOTALL | re.IGNORECASE)

def preprocess(s):

    # Process <latex>...</latex> tags.
    
    for match in re1.finditer(s):   
        imgtag = process_latex(match.group(1))
        s = s.replace(match.group(), imgtag)
    
    # Process <$>...</$> (equation) tags.

    for match in re2.finditer(s):
        imgtag = process_latex("$" + match.group(1) + "$")
        s = s.replace(match.group(), imgtag)
     
    # Process <$$>...</$$> (displaymath) tags.

    for match in re3.finditer(s):
        imgtag = process_latex("\\begin{displaymath}" + match.group(1) \
                               + "\\end{displaymath}")
        s = s.replace(match.group(), "<center>" + imgtag + "</center>")
    
    # Escape literal < (unmatched tag) and new line from string.
    
    hanging = []
    open = 0
    pending = 0

    for i in range(len(s)):
        if s[i] == '<':
            if open != 0:
                hanging.append(pending)
                pending = i
                continue
            open += 1
            pending = i
        elif s[i] == '>':
            if open > 0:
                open -= 1

    if open != 0:
        hanging.append(pending)

    new_s = ""
    for i in range(len(s)):
        if s[i] == '\n':
            new_s += "<br>"
        elif i in hanging:
            new_s += "&lt;"
        else:
            new_s += s[i]

    
    # Fill out relative paths for src tags (e.g. img src or sound src).

    i = new_s.lower().find("src")
    
    while i != -1:
        
        start = new_s.find("\"", i)
        end   = new_s.find("\"", start+1)

        if end == -1:
            break

        old_path = new_s[start+1:end]

        new_s = new_s[:start+1] + expand_path(old_path) + new_s[end:]

        # Since new_s is always longer now, we can start searching
        # from the previous end tag.
        
        i = new_s.lower().find("src", end+1)
    
    return new_s





##############################################################################
#
# anonymise_id
#
#   Returns anonymous version of id (_0, _1, ...), but keeps card's
#   original id intact.
#
##############################################################################

id_to_anon = {}

def anonymise_id(card):
    
    global id_to_anon

    if '.' in card.id:
        old_id, suffix = card.id.split('.', 1)
    else:
        old_id, suffix = card.id, ''

    if suffix:
        suffix = '.' + suffix
    
    return id_to_anon.setdefault(old_id, '_'+str(len(id_to_anon)))+suffix



##############################################################################
#
# unanonymise_id
#
#   Create a new id from an anonymous one, and updates card's id with it.
#
##############################################################################

anon_to_id = {}

def unanonymise_id(card):
    
    global anon_to_id
    
    if '.' in card.id:
        old_id, suffix = card.id.split('.', 1)
    else:
        old_id, suffix = card.id, ''

    if suffix:
        suffix = '.' + suffix

    if old_id.startswith('_'):
        if old_id in anon_to_id:
            card.id = anon_to_id[old_id] + suffix
        else:
            card.new_id()
            anon_to_id[old_id] = card.id
            card.id += suffix

    return card.id



##############################################################################
#
# import_file
#
##############################################################################

def import_file(filename, fformat_name, default_cat_name,
                reset_learning_data=False):

    global load_failed, revision_queue, anon_to_id

    # If no database is active, create one.

    if not time_of_start:
        new_database(config["path"])

    # Call import function according to file format name.

    default_cat = get_category_by_name(default_cat_name)
    fformat = get_file_format_from_name(fformat_name)
    imported_cards = fformat.import_function(filename, default_cat,
                                             reset_learning_data)

    # Add new cards.
    
    for card in imported_cards:
                    
        # Check for duplicates.

        for i in get_cards():
            if i.q == card.q and i.a == card.a:
                if get_config("check_duplicates_when_adding") == True:
                    if get_config("allow_duplicates_in_diff_cat") == False:
                        break
                    elif i.cat == card.cat:
                        break
        else:
            cards.append(card)
            
            if card.is_due_for_retention_rep():
                revision_queue[0:0] = [card]
                
            interval = card.next_rep - days_since_start
            logger.info("Imported card %s %d %d %d %d %d",
                        card.id, card.grade, card.ret_reps,
                        card.last_rep, card.next_rep, interval)

    # Clean up.

    remove_category_if_unused(default_cat)

    load_failed = False

    anon_to_id = {}



##############################################################################
#
# export_file
#
##############################################################################

def export_file(filename, fformat_name,
                cat_names_to_export, reset_learning_data):

    global id_to_anon
    
    # Call export function according to file format name.

    fformat = get_file_format_from_name(fformat_name)

    fformat.export_function(filename, cat_names_to_export, \
                            reset_learning_data)

    id_to_anon = {}






##############################################################################
#
# add_new_card
#
##############################################################################

def add_new_card(grade, question, answer, cat_name, id=None):

    global cards, load_failed

    card = Card()
    
    card.q     = question
    card.a     = answer
    card.cat   = get_category_by_name(cat_name)
    card.grade = grade
    
    card.acq_reps = 1
    card.acq_reps_since_lapse = 1

    card.last_rep = days_since_start
    
    card.easiness = average_easiness()

    if id == None:
        card.new_id()
    else:
        card.id = id 
    
    new_interval  = calculate_initial_interval(grade)
    new_interval += calculate_interval_noise(new_interval)
    card.next_rep = days_since_start + new_interval
    
    cards.append(card)    

    logger.info("New card %s %d %d", card.id, card.grade, new_interval)

    load_failed = False
    
    return card



##############################################################################
#
# delete_card
#
##############################################################################

def delete_card(e):

    old_cat = e.cat
    
    cards.remove(e)
    rebuild_revision_queue()
    remove_category_if_unused(old_cat)

    logger.info("Deleted card %s", e.id)




##############################################################################
#
# start_thinking
#
##############################################################################

def start_thinking():

    global thinking_time, time_of_last_question

    thinking_time = 0
    time_of_last_question = time.time()



##############################################################################
#
# pause_thinking
#
##############################################################################

def pause_thinking():

    global thinking_time

    if time_of_last_question != 0:
        thinking_time += time.time() - time_of_last_question



##############################################################################
#
# unpause_thinking
#
##############################################################################

def unpause_thinking():

    global time_of_last_question
    
    if time_of_last_question != 0:
        time_of_last_question = time.time()



##############################################################################
#
# stop_thinking
#
##############################################################################

def stop_thinking():

    global thinking_time, time_of_last_question
    
    thinking_time += time.time() - time_of_last_question
    time_of_last_question = 0




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
        print "Failed to remove lock file."
        print traceback_string()
