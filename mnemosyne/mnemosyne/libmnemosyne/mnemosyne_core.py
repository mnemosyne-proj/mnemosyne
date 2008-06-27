##############################################################################
#
# Mnemosyne core <Peter.Bienstman@UGent.be>
#
##############################################################################

import random, time, os, string, sys, cPickle, md5, struct, logging, re
import shutil, datetime, bz2, gzip, copy, cStringIO 

from mnemosyne.libmnemosyne.exceptions import *
import mnemosyne.version

logger = logging.getLogger("mnemosyne")



##############################################################################
#
# basedir
#
##############################################################################

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

items = []
revision_queue = []

categories = []
category_by_name = {}

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
# If set to None, the system's locale will be used.
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
    config.setdefault("grade_0_items_at_once", 5)
    config.setdefault("last_add_vice_versa", False)
    config.setdefault("last_add_category", "<default>")
    config.setdefault("3_sided_input", False)
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
        for k,v in cPickle.load(config_file).iteritems():
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
##############################################################################

class StartTime:

    def __init__(self, start_time):

        # Reset to 3.00 am by default.

        h = get_config("day_starts_at")

        t = time.localtime(start_time)
        self.time = time.mktime([t[0],t[1],t[2], h,0,0, t[6],t[7],t[8]])

    # Since this information is frequently needed, we calculate it once
    # and store it in a global variable, which is updated when the database
    # loads and in rebuild_revision_queue.
    
    def update_days_since(self):
        global days_since_start
        days_since_start = int( (time.time() - self.time) / 60. / 60. / 24.)

    
    
##############################################################################
#
# Item
#
##############################################################################

class Item:

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self):

        self.id = 0
        
        self.q         = None
        self.a         = None
        self.cat       = None
        
        self.reset_learning_data()

    ##########################################################################
    #
    # reset_learning_data
    #
    ##########################################################################

    def reset_learning_data(self):

        self.grade                = 0
        self.easiness             = 2.5
        
        self.acq_reps             = 0
        self.ret_reps             = 0
        self.lapses               = 0
        self.acq_reps_since_lapse = 0
        self.ret_reps_since_lapse = 0
        
        self.last_rep  = 0 # In days since beginning.
        self.next_rep  = 0 #

    ##########################################################################
    #
    # new_id
    #
    ##########################################################################
    
    def new_id(self):

        digest = md5.new(self.q.encode("utf-8") + self.a.encode("utf-8") + \
                         time.ctime()).hexdigest()
        self.id = digest[0:8]
        
    ##########################################################################
    #
    # sort_key
    #
    ##########################################################################

    def sort_key(self):
        return self.next_rep
    
    ##########################################################################
    #
    # sort_key_newest
    #
    ##########################################################################

    def sort_key_newest(self):
        return self.acq_reps + self.ret_reps
    
    ##########################################################################
    #
    # is_new
    #
    ##########################################################################
    
    def is_new(self):
        return (self.acq_reps == 0) and (self.ret_reps == 0)
    
    ##########################################################################
    #
    # is_due_for_acquisition_rep
    #
    ##########################################################################
    
    def is_due_for_acquisition_rep(self):
        return (self.grade < 2) and (self.cat.active == True)
    
    ##########################################################################
    #
    # is_due_for_retention_rep
    #
    #  Due for a retention repetion within 'days' days?
    #
    ##########################################################################
    
    def is_due_for_retention_rep(self, days=0):
        return (self.grade >= 2) and (self.cat.active == True) and \
               (days_since_start >= self.next_rep - days)

    ##########################################################################
    #
    # days_since_last_rep
    #
    ##########################################################################
    
    def days_since_last_rep(self):
        return days_since_start - self.last_rep

    ##########################################################################
    #
    # days_until_next_rep
    #
    ##########################################################################
    
    def days_until_next_rep(self):
        return self.next_rep - days_since_start
    
    ##########################################################################
    #
    # is_in_active_category
    #
    ##########################################################################

    def is_in_active_category(self):
        return (self.cat.active == True)

    ##########################################################################
    #
    # qualifies_for_learn_ahead
    #
    ##########################################################################
    
    def qualifies_for_learn_ahead(self):
        return (self.grade >= 2) and (self.cat.active == True) and \
               (days_since_start < self.next_rep) 
        
    ##########################################################################
    #
    # change_category
    #
    ##########################################################################
    
    def change_category(self, new_cat_name):

        old_cat = self.cat
        self.cat = get_category_by_name(new_cat_name)
        remove_category_if_unused(old_cat)



##############################################################################
#
# items_are_inverses
#
##############################################################################

def items_are_inverses(item1, item2):

    if item1.q == item2.a and item2.q == item1.a:
        return True
    else:
        return False



##############################################################################
#
# get_items
#
##############################################################################

def get_items():
    return items



##############################################################################
#
# get_item_by_id
#
##############################################################################

def get_item_by_id(id):
    try:
        return [i for i in items if i.id == id][0]
    except:
        return None



##############################################################################
#
# number_of_items
#
##############################################################################

def number_of_items():
    return len(items)



##############################################################################
#
# non_memorised_items
#
##############################################################################

def non_memorised_items():
    return sum(1 for i in items if i.is_due_for_acquisition_rep())



##############################################################################
#
# scheduled_items
#
#   Number of items scheduled within 'days' days.
#
##############################################################################

def scheduled_items(days=0):
    return sum(1 for i in items if i.is_due_for_retention_rep(days))



##############################################################################
#
# active_items
#
#   Number of items in an active category.
#
##############################################################################

def active_items():
    return sum(1 for i in items if i.is_in_active_category())



##############################################################################
#
# average_easiness
#
##############################################################################

def average_easiness():

    if len(items) == 0:
        return 2.5
    if len(items) == 1:
        return items[0].easiness
    else:
        return sum(i.easiness for i in items) / len(items)



##############################################################################
#
# Category
#
##############################################################################

class Category:
    
    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, name, active=True):

        self.name = name
        self.active = active

    ##########################################################################
    #
    # in_use
    #
    ##########################################################################

    def in_use(self):

        used = False

        for e in items:
            if self.name == e.cat.name:
                used = True
                break

        return used



##############################################################################
#
# get_categories
#
##############################################################################

def get_categories():
    return categories



##############################################################################
#
# get_category_names
#
##############################################################################

def get_category_names():
    return category_by_name.keys()



##############################################################################
#
# ensure_category_exists
#
##############################################################################

def ensure_category_exists(name):

    global category_by_name, categories

    if name not in category_by_name.keys():
        category = Category(name)
        categories.append(category)
        category_by_name[name] = category



##############################################################################
#
# get_category_by_name
#
##############################################################################

def get_category_by_name(name):

    global category_by_name

    ensure_category_exists(name)
    return category_by_name[name]



##############################################################################
#
# remove_category_if_unused
#
##############################################################################

def remove_category_if_unused(cat):

    global items, category_by_name, categories

    for item in items:
        if cat.name == item.cat.name:
            break
    else:
        del category_by_name[cat.name]
        categories.remove(cat)



##############################################################################
#
# new_database
#
##############################################################################

def new_database(path):

    global config, time_of_start, load_failed

    if len(items) > 0:
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

    global config, time_of_start, categories, category_by_name, items
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
        items         = db[2]
        
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

    logger.info("Loaded database %d %d %d", scheduled_items(), \
                non_memorised_items(), number_of_items())

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

        db = [time_of_start, categories, items]
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

    global items, revision_queue, categories, category_by_name
        
    save_database(config["path"])
    
    logger.info("Saved database %d %d %d", scheduled_items(), \
                non_memorised_items(), number_of_items())        
    items = []
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

    if number_of_items() == 0:
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
    return len(items) != 0



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
    in_unicode_substring = False
    
    for i in range(len(old_string)):
        if not in_latin_plane(ord(old_string[i])):

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
                
            if in_unicode_substring == True:
                in_unicode_substring = False
                new_string += '</font>' + old_string[i]
            else:
                new_string += old_string[i]
                
    # Make sure to close the last tag.
              
    if not in_latin_plane(ord(old_string[-1])):
        new_string += '</font>'

    return new_string



##############################################################################
#
# process_latex
#
##############################################################################

def process_latex(latex_command):

    latex_command = latex_command.replace("&lt;", "<") 

    error_str = "<b>Problem with latex. Are latex and dvipng installed?</b>"
    
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
# FileFormat
#
# Each file format that Mnemosyne supports is identified by a name (a string).
# Additionally, a file format needs a file name filter (a string), a function
# to import data from a file of the respective type, and a function to export
# data in the respective format.
#
# The file format name will appear in the import and export dialogues.
# Therefore, they shall be easy to understand by a user, e.g. "Text
# with tab-separated Q/A".
#
# The file name filter has to be given in Qt format, e. g. "XML Files (*.xml
# *XML)". It will be used in the file selection dialogues.
#
# TODO-dh: Think about creating a directory, where each .py file is read at
#     startup.  With such a mechanism, adding additional file formats would
#     not even demand any code change in Mnemosyne's core.
#
##############################################################################

file_formats = []

class FileFormat:

    def __init__(self, name, filter="",
                 import_function=False, export_function=False):

        self.name = name
        self.filter = filter
        self.import_function = import_function
        self.export_function = export_function



##############################################################################
#
# register_file_format
#
##############################################################################

def register_file_format(name, filter="",
                         import_function=False, export_function=False):

    global file_formats
    
    file_formats.append(FileFormat(name, filter,
                                   import_function, export_function))
    
    file_formats.sort(lambda x,y: cmp(x.name, y.name))



##############################################################################
#
# get_importable_file_formats
#
##############################################################################

def get_importable_file_formats():
     return [f for f in file_formats if f.import_function]



##############################################################################
#
# get_exportable_file_formats
#
##############################################################################

def get_exportable_file_formats():
     return [f for f in file_formats if f.export_function]



##############################################################################
#
# get_file_format_from_name
#
##############################################################################

def get_file_format_from_name(name):

    for fformat in file_formats:
        if name == fformat.name:
            return fformat

    raise InvalidFormatError()



##############################################################################
#
# anonymise_id
#
#   Returns anonymous version of id (_0, _1, ...), but keeps item's
#   original id intact.
#
##############################################################################

id_to_anon = {}

def anonymise_id(item):
    
    global id_to_anon

    if '.' in item.id:
        old_id, suffix = item.id.split('.', 1)
    else:
        old_id, suffix = item.id, ''

    if suffix:
        suffix = '.' + suffix
    
    return id_to_anon.setdefault(old_id, '_'+str(len(id_to_anon)))+suffix



##############################################################################
#
# unanonymise_id
#
#   Create a new id from an anonymous one, and updates item's id with it.
#
##############################################################################

anon_to_id = {}

def unanonymise_id(item):
    
    global anon_to_id
    
    if '.' in item.id:
        old_id, suffix = item.id.split('.', 1)
    else:
        old_id, suffix = item.id, ''

    if suffix:
        suffix = '.' + suffix

    if old_id.startswith('_'):
        if old_id in anon_to_id:
            item.id = anon_to_id[old_id] + suffix
        else:
            item.new_id()
            anon_to_id[old_id] = item.id
            item.id += suffix

    return item.id



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
    imported_items = fformat.import_function(filename, default_cat,
                                             reset_learning_data)

    # Add new items.
    
    for item in imported_items:
                    
        # Check for duplicates.

        for i in get_items():
            if i.q == item.q and i.a == item.a:
                if get_config("check_duplicates_when_adding") == True:
                    if get_config("allow_duplicates_in_diff_cat") == False:
                        break
                    elif i.cat == item.cat:
                        break
        else:
            items.append(item)
            
            if item.is_due_for_retention_rep():
                revision_queue[0:0] = [item]
                
            interval = item.next_rep - days_since_start
            logger.info("Imported item %s %d %d %d %d %d",
                        item.id, item.grade, item.ret_reps,
                        item.last_rep, item.next_rep, interval)

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
# XML_Importer
#
##############################################################################

from xml.sax import saxutils, make_parser
from xml.sax.handler import feature_namespaces

class XML_Importer(saxutils.DefaultHandler):
    
    def __init__(self, default_cat=None, reset_learning_data=False):
        self.reading, self.text = {}, {}
        
        self.reading["cat"] = False
        self.reading["Q"]   = False
        self.reading["A"]   = False

        self.default_cat = default_cat
        self.reset_learning_data = reset_learning_data

        self.imported_items = []

    def to_bool(self, string):
        if string == '0':
            return False
        else:
            return True
    
    def startElement(self, name, attrs):
        global import_time_of_start
        
        if name == "mnemosyne":
            if attrs.get("time_of_start"):
                import_time_of_start \
                  = StartTime(long(attrs.get("time_of_start")))
            else:
                import_time_of_start = time_of_start
                
        elif name == "item":
            self.item = Item()
            
            self.item.id = 0
            if attrs.get("id"):
                self.item.id = attrs.get("id")

            self.item.grade = 0
            if attrs.get("gr"):
                self.item.grade = int(attrs.get("gr"))

            self.item.easiness = average_easiness()
            if attrs.get("e"):
                self.item.easiness = float(attrs.get("e"))

            self.item.acq_reps = 0
            if attrs.get("ac_rp"):
                self.item.acq_reps = int(attrs.get("ac_rp"))

            self.item.ret_reps = 0
            if attrs.get("rt_rp"):
                self.item.ret_reps = int(attrs.get("rt_rp"))
                
            self.item.lapses = 0
            if attrs.get("lps"):
                self.item.lapses = int(attrs.get("lps"))
                
            self.item.acq_reps_since_lapse = 0
            if attrs.get("ac_rp_l"):
                self.item.acq_reps_since_lapse = int(attrs.get("ac_rp_l"))

            self.item.ret_reps_since_lapse = 0
            if attrs.get("rt_rp_l"):
                self.item.ret_reps_since_lapse = int(attrs.get("rt_rp_l"))
                
            self.item.last_rep = 0
            if attrs.get("l_rp"):
                self.item.last_rep = int(attrs.get("l_rp"))
                
            self.item.next_rep = 0
            if attrs.get("n_rp"):
                self.item.next_rep = int(float(attrs.get("n_rp")))
                
        elif name == "category":
            self.active = self.to_bool(attrs.get("active"))
            self.text["name"] = None

        else:
            self.reading[name] = True
            self.text[name] = ""

    def characters(self, ch):
        for name in self.reading.keys():
            if self.reading[name] == True:
                self.text[name] += ch

    def endElement(self, name):

        self.reading[name] = False

        if name == "cat":

            cat_name = self.text["cat"]
            self.item.cat = get_category_by_name(cat_name)

        elif name == "Q":

            self.item.q = self.text["Q"]

        elif name == "A":

            self.item.a = self.text["A"]

        elif name == "item":

            if self.item.id == 0:
                self.item.new_id()

            if self.item.id.startswith('_'):
                unanonymise_id(self.item)

            if self.item.cat == None:
                self.item.cat = self.default_cat

            if self.reset_learning_data == True:
                self.item.reset_learning_data()
                self.item.easiness = average_easiness()

            self.imported_items.append(self.item)

        elif name == "category":

            name = self.text["name"]
            if (name != None):
                ensure_category_exists(name)
            get_category_by_name(name).active = self.active



##############################################################################
#
# memaid_XML_Importer
#
##############################################################################

class memaid_XML_Importer(saxutils.DefaultHandler):
    
    def __init__(self, default_cat=None, reset_learning_data=False):
        self.reading, self.text = {}, {}
        
        self.reading["cat"] = False
        self.reading["Q"]   = False
        self.reading["A"]   = False

        self.default_cat = default_cat
        self.reset_learning_data = reset_learning_data

        self.imported_items = []

    def to_bool(self, string):
        if string == '0':
            return False
        else:
            return True
    
    def startElement(self, name, attrs):
        global import_time_of_start
        
        if name == "memaid":
            if attrs.get("time_of_start"):
                import_time_of_start \
                  = StartTime(long(attrs.get("time_of_start")))
            else:
                import_time_of_start = time_of_start
                
        elif name == "item":
            self.item = Item()

            self.item.id        = long(attrs.get("id"))
            self.item.grade     =  int(attrs.get("gr"))
            self.item.next_rep  =  int(attrs.get("tm_t_rpt"))
            self.item.ret_reps  =  int(attrs.get("rp"))
            interval            =  int(attrs.get("ivl"))
            self.item.last_rep  = self.item.next_rep - interval
            self.item.easiness  = average_easiness()

        elif name == "category":
            self.active = self.to_bool(attrs.get("scheduled"))
        else:
            self.reading[name] = True
            self.text[name] = ""

    def characters(self, ch):
        for name in self.reading.keys():
            if self.reading[name] == True:
                self.text[name] += ch

    def endElement(self, name):

        self.reading[name] = False

        if name == "cat":

            cat_name = self.text["cat"]
            self.item.cat = get_category_by_name(cat_name)

        elif name == "Q":

            self.item.q = self.text["Q"]

        elif name == "A":

            self.item.a = self.text["A"]

        elif name == "item":

            if self.item.id == 0:
                self.item.new_id()

            if self.item.cat == None:
                self.item.cat = self.default_cat

            if self.reset_learning_data == True:
                self.item.reset_learning_data()
                self.item.easiness = average_easiness()

            self.imported_items.append(self.item)

        elif name == "category":

            name = self.text["name"]
            if (name != None):
                ensure_category_exists(name)
            get_category_by_name(name).active = self.active



##############################################################################
#
# class smconv_XML_Importer
# 
# Author: Felix Engel <Felix.Engel@fcenet.de>
# 
# Import the xml file created by the smconv.pl script to Mnemosyne.
# smconv.pl is available at http://smconvpl.sourceforge.net and reads
# SuperMemo for Palm databases and exports them to XML.
#
# In order to import the generated XML into mnemosyne, care must be taken
# to ensure the correct charset encoding of the input file. In my case,
# the palm databases are "windows-1252". The xml file generated by smconv.pl
# was set to "us-ascii". This makes the XML parser fail. For me, changing
# the xml header to <?xml version="1.0" encoding="windows-1252"?>  worked
# well. However, your mileage may vary.
#
# Restrictions:
#
#  - SM for Palm has six fields for each card. Templates can be used to
#    format these fields and to control whether they are part of  the
#    question or of the answer. However this class assumes that the first
#    field is the question and the second field is the answer.
#  - No error handling. If the XML is not well formed or if fields are
#    missing, the behaviour is unpredictable.
#
##############################################################################

class smconv_XML_Importer(saxutils.DefaultHandler):
    
    def __init__(self, default_cat=None, reset_learning_data=False):
        
        self.reading, self.text = {}, {}
        
        self.reading["cat"] = False
        self.reading["Q"]   = False
        self.reading["A"]   = False

        self.default_cat = default_cat
        self.reset_learning_data = reset_learning_data

        self.imported_items = []
        self.lapses = 0
        self.recalls = 0
        self.difficulty = 40 
        self.difficulty_prev = 40
        self.datecommit = ""
        self.interval = 0
        self.interval_prev = 0
        self.commit = 0

    def to_bool(self, string):
        if string == '0':
            return False
        else:
            return True
   
    def reset_elements(self):
        
        self.lapses = 0
        self.recalls = 0
        self.difficulty = 40 
        self.difficulty_prev = 40
        self.datecommit = ""
        self.interval = 0
        self.interval_pref = 0

    def startElement(self, name, attrs):
	
        global import_time_of_start
        
	# I cannot guarantee, when the header will be read, so
	# I use the epoch for now. Times will be normalized,
	# once the whole database has been read.
	
        if name == "card":
            self.item = Item();
            if attrs.get("commit"):
                self.commit = attrs.get("commit")
            if attrs.get("category"):
                self.category = attrs.get("category")

        elif name == "card_other":
            if attrs.get("lapses"):
                self.lapses = int(attrs.get("lapses"))
            if attrs.get("recalls"):
                self.recalls = int(attrs.get("recalls"))
            if attrs.get("difficulty"):
                self.difficulty = int(attrs.get("difficulty"))
            if attrs.get("difficulty_prev"):
                self.difficulty_prev = int(attrs.get("difficulty_prev"))
            if attrs.get("datecommit"):
                self.datecommit = attrs.get("datecommit")
            if attrs.get("datenexttest"):
                self.datenexttest = attrs.get("datenexttest")
            if attrs.get("interval"):
                self.interval = int(attrs.get("interval"))
            if attrs.get("interval_prev"):
                self.interval_prev = int(attrs.get("interval_prev"))

        elif name == "card_field":
            if attrs.get("idx") == "1":
                self.reading["Q"] = True
                self.text["Q"] = ""
            if  attrs.get("idx") == "2":
                self.reading["A"] = True
                self.text["A"] = ""
	elif name == "header":
            if attrs.get("datecommit"):
                start_time = attrs.get("datecommit")
                try:
                    struct_t = time.strptime(attrs.get("datecommit"),\
                                             "%Y-%m-%d")
                    t_sec = time.mktime(struct_t)
                    import_time_of_start = StartTime(t_sec); 
                except:
                    import_time_of_start = StartTime(0); 
			
	else: # Default action: do nothing.
            return

    def characters(self, ch):
        for name in self.reading.keys():
            if self.reading[name] == True:
                self.text[name] += ch

    def guess_grade(self):
        
	# Very easy items are scarce in SM and must be easiest grade.
        
	if self.difficulty < 10:
		return 5

	# Assign passing grades, based upon whether the difficulty has
	# changed.
        
	if self.difficulty > self.difficulty_prev:
		return 2

	if self.difficulty == self.difficulty_prev:
		return 3

	if self.difficulty < self.difficulty_prev:
		return 4

	# If the interval becomes shorter, it must have been a failure.
        
	if self.interval < self.interval_prev:
            return 1

    def endElement(self, name):
        
	if name == "card":
            
            # Try to derive an easines factor EF from [1.3 .. 3.2] from
            # difficulty d from [1% .. 100%]. 
            # The math below is set to translate
            # difficulty=100% --> easiness = 1.3
            # difficulty=40% --> easiness = 2.5
            # difficulty=1% --> easiness = 3.2
            
            import math
            dp = self.difficulty * 0.01

            # Small values should be easy, large ones hard.
            
            if dp > 0.4:
                self.item.easiness = 1.28 - 1.32 * math.log(dp)
            else:
                self.item.easiness = 4.2 - (1.139 * math.exp(dp) )

            # Grades are 0-5. In SM for Palm there are commited and uncommited 
            # cards. Uncommited cards go to grade 0.
            # Otherwise try to extrapolate something from difficulty in SM
            # I have implemented guess_grade such, that the distribution of
            # grades looks reasonable for my test database of 4000 entries.
            # By "reasonable" I mean than most of the entries should be 
            # at grade 4. I've been learning that database for 4 years, so the
            # cards should have converged by now.
                
            if self.commit == False:
                self.item.grade = 0
            else:
                self.item.grade = self.guess_grade()

            self.item.lapses = self.lapses
		
            # Handle dates, assume starttime to be the epoch.
            # Need to determine last_rep and next_rep.

            try:
                struct_t = time.strptime(self.datenexttest,"%Y-%m-%d")
            except:
                print "Failed to parse time - using zero."

            t_sec = int(0)

            try:
                t_sec = time.mktime(struct_t)
            except:
                print "mktime failed - using zero."

            self.item.next_rep = int(t_sec / 86400)

            # last_rep is interval in days before next_rep.

            self.item.last_rep = self.item.next_rep - self.interval

            # Try to fill acquisiton reps and retention reps.
            # Since SM statistics are only available for commited
            # cards, I take acq_reps = 0 and ret_reps = lapses + recalls.
            
            self.item.ret_reps = self.lapses + self.recalls

            self.item.cat = get_category_by_name(self.category)
            self.imported_items.append(self.item)
		
	elif name == "card_field":
            if self.reading["Q"]:
                self.reading["Q"] = False
                self.item.q = self.text["Q"]
                self.text["Q"] = ""
            if self.reading["A"]:
                self.reading["A"] = False
                self.item.a = self.text["A"]
                self.text["A"] = ""

	elif name == "smconv_pl":
            
            # During the import, there was no guarantee that the start time
            # has already been read. Now, at the smconv_pl closing tag, the
            # import_time_of_start variable has been set. Update all imported
            # items accordingly.

            now = import_time_of_start.time
            diff = int(now / 86400)
            for i in self.imported_items:
                i.next_rep = i.next_rep - diff
                i.last_rep = i.last_rep - diff



##############################################################################
#
# import_XML
#
#   Note that we do not register separate file formats for Mnemosyne and
#   Memaid XML. We're able to figure out the difference on our own and do not
#   need to put this burden on the user.
#
##############################################################################

def import_XML(filename, default_cat, reset_learning_data=False):
    global items

    # Determine if we import a Mnemosyne or a Memaid file.

    handler = None

    f = None
    try:
        f = file(filename)
    except:
        try:
            f = file(unicode(filename).encode("latin"))
        except:
            raise LoadError()
    
    l = f.readline()
    l += f.readline();    
    if "mnemosyne" in l:
        handler = XML_Importer(default_cat, reset_learning_data)
    elif "smconv_pl" in l:
    	handler = smconv_XML_Importer(default_cat, reset_learning_data)
    else:
        handler = memaid_XML_Importer(default_cat, reset_learning_data)
        
    f.close()

    # Parse XML file.
    
    parser = make_parser()
    parser.setFeature(feature_namespaces, 0)
    parser.setContentHandler(handler)

    try:
        # Use cStringIo to avoid a crash in sax when filename has unicode
        # characters.
        s = file(filename).read()
        f = cStringIO.StringIO(s)
        parser.parse(f)
    except Exception, e:
        raise XMLError(stack_trace=True)

    # Calculate offset with current start date.
    
    cur_start_date =        time_of_start.time
    imp_start_date = import_time_of_start.time
    
    offset = long(round((cur_start_date - imp_start_date) / 60. / 60. / 24.))
        
    # Adjust timings.

    if reset_learning_data == False:
        if cur_start_date <= imp_start_date :
            for item in handler.imported_items:
                item.last_rep += abs(offset)
                item.next_rep += abs(offset)
        else:
            time_of_start.time = imp_start_date
            for item in items:
                item.last_rep += abs(offset)
                item.next_rep += abs(offset)

    return handler.imported_items



##############################################################################
#
# encode_cdata
#
##############################################################################

def encode_cdata(s):
    return saxutils.escape(s.encode("utf-8"))



##############################################################################
#
# write_item_XML
#
##############################################################################

def write_item_XML(e, outfile, reset_learning_data=False):

    if reset_learning_data == False:
        print >> outfile, "<item id=\""+str(e.id) + "\"" \
                         + " gr=\""+str(e.grade) + "\"" \
                         + " e=\""+ "%.3f" % e.easiness + "\"" \
                         + " ac_rp=\""+str(e.acq_reps) + "\"" \
                         + " rt_rp=\""+str(e.ret_reps) + "\""  \
                         + " lps=\""+str(e.lapses) + "\"" \
                         + " ac_rp_l=\""+str(e.acq_reps_since_lapse) + "\"" \
                         + " rt_rp_l=\""+str(e.ret_reps_since_lapse) + "\"" \
                         + " l_rp=\""+str(e.last_rep) + "\"" \
                         + " n_rp=\""+str(e.next_rep) + "\">"
    else:
        print >> outfile, "<item id=\"" + anonymise_id(e) + "\">"

    print >> outfile, " <cat>" + encode_cdata(e.cat.name) + "</cat>"
    print >> outfile, " <Q>" + encode_cdata(e.q) + "</Q>"
    print >> outfile, " <A>" + encode_cdata(e.a) + "</A>"
    print >> outfile, "</item>"



##############################################################################
#
# bool_to_digit
#
##############################################################################

def bool_to_digit(b):
    
    if b == True:
        return "1"
    else:
        return "0"



##############################################################################
#
# write_category_XML
#
##############################################################################

def write_category_XML(category, outfile, reset_learning_data):

    if reset_learning_data == True:
        active = True
    else:
        active = category.active
    
    print >> outfile, "<category active=\"" \
          + bool_to_digit(active) + "\">"
    print >> outfile, " <name>" + encode_cdata(category.name) + "</name>"
    print >> outfile, "</category>"



##############################################################################
#
# export_XML
#
##############################################################################

def export_XML(filename, cat_names_to_export, reset_learning_data):
        
    try:
        outfile = file(filename,'w')
    except:
        return False

    print >> outfile, """<?xml version="1.0" encoding="UTF-8"?>"""

    print >> outfile, "<mnemosyne core_version=\"1\"",

    if reset_learning_data == False:
        print >> outfile, "time_of_start=\"" + \
              str(long(time_of_start.time))+"\"",

    print >> outfile, ">"
    
    for cat in categories:
        if cat.name in cat_names_to_export:
            write_category_XML(cat, outfile, reset_learning_data)

    for e in items:
        if e.cat.name in cat_names_to_export:
            write_item_XML(e, outfile, reset_learning_data)

    print >> outfile, """</mnemosyne>"""

    outfile.close()

    return True


register_file_format("XML",
                     filter="XML files (*.xml *.XML)",
                     import_function=import_XML,
                     export_function=export_XML)

register_file_format("Supermemo for Palm through smconv.pl",
                     filter="XML files (*.xml *.XML)",
                     import_function=import_XML,
                     export_function=None)



##############################################################################
#
# process_html_unicode
#
#   Parse html style escaped unicode (e.g. &#33267;)
#
##############################################################################

re0 = re.compile(r"&#(.+?);", re.DOTALL | re.IGNORECASE)

def process_html_unicode(s):

    for match in re0.finditer(s):   
        u = unichr(int(match.group(1)))  # Integer part.
        s = s.replace(match.group(), u)  # Integer part with &# and ;.
        
    return s



##############################################################################
#
# import_txt
#
#   Question and answers on a single line, separated by tabs.
#   Or, for three-sided cards: written form, pronunciation, translation,
#   separated by tabs.
#
##############################################################################

def import_txt(filename, default_cat, reset_learning_data=False):
    
    global items

    imported_items = []

    # Parse txt file.

    avg_easiness = average_easiness()

    f = None
    try:
        f = file(filename)
    except:
        try:
            f = file(filename.encode("latin"))
        except:
            raise LoadError()
    
    for line in f:
        
        try:
            line = unicode(line, "utf-8")
        except:
            try:
                line = unicode(line, "latin")
            except:
                raise EncodingError()

        line = line.rstrip()
        line = process_html_unicode(line)
        
        if len(line) == 0:
            continue

        if line[0] == u'\ufeff': # Microsoft Word unicode export oddity.
            line = line[1:]

        fields = line.split('\t')

        # Three sided card.

        if len(fields) >= 3:

            # Card 1.
            
            item = Item()
            
            item.q = fields[0]
            item.a = fields[1] + '\n' + fields[2]
            item.easiness = avg_easiness
            item.cat = default_cat
            item.new_id()
                    
            imported_items.append(item)

            id = item.id

            # Card 2.
            
            item = Item()
            
            item.q = fields[2]
            item.a = fields[0] + '\n' + fields[1]
            item.easiness = avg_easiness
            item.cat = default_cat
            item.id = id + '.tr.1'
                    
            imported_items.append(item)

        # Two sided card.
        
        elif len(fields) == 2:
            
            item = Item()
            
            item.q = fields[0]
            item.a = fields[1]
            item.easiness = avg_easiness
            item.cat = default_cat
            item.new_id()
                    
            imported_items.append(item)
            
        else:
            raise MissingAnswerError(info=line)

    return imported_items



##############################################################################
#
# export_txt
#
#   Newlines are converted to <br> to keep items on a single line.
#
##############################################################################

def export_txt(filename, cat_names_to_export, reset_learning_data=False):

    try:
        outfile = file(filename,'w')
    except:
        return False

    for e in items:
        if e.cat.name in cat_names_to_export:
            question = e.q.encode("utf-8")
            question = question.replace("\t", " ")
            question = question.replace("\n", "<br>")
            
            answer = e.a.encode("utf-8")
            answer = answer.replace("\t", " ")
            answer = answer.replace("\n", "<br>")
            
            print >> outfile, question + "\t" + answer

    outfile.close()

    return True
    

register_file_format("Text with tab separated Q/A",
                     filter="Text files (*.txt *.TXT)",
                     import_function=import_txt,
                     export_function=export_txt)


##############################################################################
#
# import_txt_2
#
#   Question and answers each on a separate line.
#
##############################################################################

def import_txt_2(filename, default_cat, reset_learning_data=False):
    
    global items

    imported_items = []

    # Parse txt file.

    avg_easiness = average_easiness()

    f = None
    try:
        f = file(filename)
    except:
        try:
            f = file(filename.encode("latin"))
        except:
            raise LoadError()

    Q_A = []
    
    for line in f:
        
        try:
            line = unicode(line, "utf-8")
        except:
            try:
                line = unicode(line, "latin")
            except:
                raise EncodingError()

        line = line.rstrip()
        line = process_html_unicode(line)
        
        if len(line) == 0:
            continue

        if line[0] == u'\ufeff': # Microsoft Word unicode export oddity.
            line = line[1:]

        Q_A.append(line)

        if len(Q_A) == 2:
            
            item = Item()

            item.q = Q_A[0]
            item.a = Q_A[1]    
        
            item.easiness = avg_easiness
            item.cat = default_cat
            item.new_id()
                    
            imported_items.append(item)

            Q_A = []

    return imported_items

register_file_format("Text with Q and A each on separate line",
                     filter="Text files (*.txt *.TXT)",
                     import_function=import_txt_2,
                     export_function=False)



##############################################################################
#
# Functions for importing and exporting files in SuperMemo's text file format:
# A line starting with 'Q: ' holds a question, a line starting with 'A: '
# holds an answer.  Several consecutive question lines form a multi line
# question, several consecutive answer lines form a multi line answer.  After
# the answer lines, learning data may follow.  This consists of a line like
# 'I: REP=8 LAP=0 EF=3.200 UF=2.370 INT=429 LAST=27.01.06' and a line like
# 'O: 36'.  After each item (even the last one) there must be an empty line.
#
##############################################################################

def read_line_sm7qa(f):

    line = f.readline()

    if not line:
        return False

    # Supermemo uses the octet 0x03 to represent the accented u character.
    # Since this does not seem to be a standard encoding, we simply replace
    # this.
    
    line = line.replace("\x03", "\xfa")

    try:
        line = unicode(line, "utf-8")
    except:
        try:
            line = unicode(line, "latin")
        except:
            raise EncodingError()
        
    line = line.rstrip()
    line = process_html_unicode(line)

    return line



def import_sm7qa(filename, default_cat, reset_learning_data=False):

    global items

    # Parse txt file.

    avg_easiness = average_easiness()

    f = None
    try:
        f = file(filename)
    except:
        try:
            f = file(filename.encode("latin"))
        except:
            raise LoadError()

    imported_items = []
    state = "ITEM-START"
    next_state = None
    error = False

    while not error and state != "END-OF-FILE":

        line = read_line_sm7qa(f)

        # Perform the actions of the current state and calculate
        # the next state.

        if state == "ITEM-START":
            
            # Expecting a new item to start, or the end of the input file.
            
            if line == False:
                next_state = "END-OF-FILE"
            elif line == "":
                next_state = "ITEM-START"
            elif line.startswith("Q:"):
                question = line[2:].strip()
                repetitions = 0
                lapses = 0
                easiness = avg_easiness
                interval = 0
                last = 0
                next_state = "QUESTION"
            else:
                error = True
        elif state == "QUESTION":
            
            # We have already read the first question line. Further question
            # lines may follow, or the first answer line.

            if line == False:
                error = True
            elif line.startswith("Q:"):
                question = question + "\n" + line[2:].strip()
                next_state = "QUESTION"
            elif line.startswith("A:"):
                answer = line[2:].strip()
                next_state = "ANSWER"
            else:
                error = True
        elif state == "ANSWER":
            
            # We have already read the first answer line. Further answer
            # lines may follow, or the lines with the learning data.
            # Otherwise, the item has to end with either an empty line or with
            # the end of the input file.

            if line == False:
                next_state = "END-OF-FILE"
            elif line == "":
                next_state = "ITEM-START"
            elif line.startswith("A:"):
                answer = answer + "\n" + line[2:].strip()
                next_state = "ANSWER"
            elif line.startswith("I:"):
                attributes = line[2:].split()
                if len(attributes) != 6:
                    error = True
                else:
                    if ( attributes[0].startswith("REP=")
                            and attributes[1].startswith("LAP=")
                            and attributes[2].startswith("EF=")
                            and attributes[4].startswith("INT=")
                            and attributes[5].startswith("LAST=") ):
                        repetitions = int(attributes[0][4:])
                        lapses = int(attributes[1][4:])
                        easiness = float(attributes[2][3:])
                        interval = int(attributes[4][4:])
                        if attributes[5] == "LAST=0":
                            last = 0
                        else:
                            last = time.strptime(attributes[5][5:], "%d.%m.%y")
                    else:
                        error = True
                next_state = "LEARNING-DATA"
            else:
                error = True
        elif state == "LEARNING-DATA":
            
            # We have already read the first line of the learning data. The
            # second line with the learning data has to follow.
            
            if line == False:
                error = True
            elif line.startswith("O:"): # This line is ignored.
                next_state = "ITEM-END"
            else:
                error = True
        elif state == "ITEM-END":
            
            # We have already read all learning data. The item has to end
            # with either an empty line or with the end of the input file.
            
            if line == False:
                next_state = "END-OF-FILE"
            elif line == "":
                next_state = "ITEM-START"
            else:
                error = True

        # Perform the transition actions that are common for a set of
        # transitions.

        if ( (state == "ANSWER" and next_state == "END-OF-FILE")
                or (state == "ANSWER" and next_state == "ITEM-START")
                or (state == "ITEM-END" and next_state == "END-OF-FILE")
                or (state == "ITEM-END" and next_state == "ITEM-START") ):
            item = Item()

            if not reset_learning_data:
                
                # A grade information is not given directly in the file
                # format.  To make the transition to Mnemosyne smooth for a
                # SuperMemo user, we make sure that all items get queried in a
                # similar way as SuperMemo would have done it.
                
                if repetitions == 0:
                    
                    # The item is new, there are no repetitions yet.
                    # SuperMemo queries such items in a dedicated learning
                    # mode "Memorize new items", thus offering the user to
                    # learn as many new items per session as desired.  We
                    # achieve a similar behaviour by grading the item 0.
                    
                    item.grade = 0
                    
                elif repetitions == 1 and lapses > 0:
                    
                    # The learner had a lapse with the last repetition.
                    # SuperMemo users will expect such items to be queried
                    # during the next session.  Thus, to avoid confusion, we
                    # set the initial grade to 1.
                    
                    item.grade = 1
                    
                else:
                    
                    # There were either no lapses yet, or some successful
                    # repetitions since.
                    
                    item.grade = 4
                    
                item.easiness = easiness

                # There is no possibility to calculate the correct values for
                # item.acq_reps and item.ret_reps from the SuperMemo file
                # format.  Thus, to distinguish between a new item and an item
                # that already has some learning data, the values are set to 0
                # or 1.
                
                if repetitions == 0:
                    item.acq_reps = 0
                    item.ret_reps = 0
                else:
                    item.acq_reps = 1
                    item.ret_reps = 1

                item.lapses = lapses

                # The following information is not reconstructed from
                # SuperMemo: item.acq_reps_since_lapse

                item.ret_reps_since_lapse = max(0, repetitions - 1)

                # Calculate the dates for the last and next repetitions.  The
                # logic makes sure that the interval between last_rep and
                # next_rep is kept.  To do this, it may happen that last_rep
                # gets a negative value.
                
                if last == 0:
                    last_in_days = 0
                else:
                    last_absolute_sec = StartTime(time.mktime(last)).time
                    last_relative_sec = last_absolute_sec - time_of_start.time
                    last_in_days = last_relative_sec / 60. / 60. / 24.
                item.next_rep = long( max( 0, last_in_days + interval ) )
                item.last_rep = item.next_rep - interval

                # The following information from SuperMemo is not used:
                # UF, O_value

            item.q = saxutils.escape(question)
            item.a = saxutils.escape(answer)
            item.cat = default_cat

            item.new_id()

            imported_items.append(item)

        # Go to the next state.

        state = next_state

    if error:
        return False
    else:
        return imported_items


register_file_format("SuperMemo7 text in Q:/A: format",
                     filter="SuperMemo7 text files (*.txt *.TXT)",
                     import_function=import_sm7qa,
                     export_function=False)



##############################################################################
#
# Cuecard *.wcu importer/exporter by Chris Aakre (caaakre at gmail dot com).
#
# Issues: Does not handle sounds on import/export (not sure how to set it 
# up...help anyone?). Attribute tags are QuestionSound and AnswerSound.
#
##############################################################################

def import_wcu(filename, default_cat, reset_learning_data=False):
    
    global items
    imported_items = []
    avg_easiness = average_easiness()

    from xml.dom import minidom, Node
    f = None
    try:
        f = file(filename)
    except:
        try:
            f = file(unicode(filename).encode("latin"))
        except:
            raise LoadError()

    def wcuwalk(parent, cards, level=0):
        
        for node in parent.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                
                card = Item()
                
                if node.attributes.has_key("QuestionPicture"):
                    card.q='<img src="'+\
                            node.attributes.get("QuestionPicture").nodeValue+\
                            '"><br/>'+\
                            node.attributes.get("Question").nodeValue
                else:
                    card.q=node.attributes.get("Question").nodeValue
                    
                if node.attributes.has_key("AnswerPicture"):
                    card.a='<img src="'+\
                            node.attributes.get("AnswerPicture").nodeValue+\
                            '"><br/>'+\
                            node.attributes.get("Answer").nodeValue
                else:
                    card.a=node.attributes.get("Answer").nodeValue
                    
                card.easiness=avg_easiness
                card.cat = default_cat
                card.new_id()
                cards.append(card)
                
                wcuwalk(node, cards, level+1)

    wcuwalk(minidom.parse(filename).documentElement,imported_items)
    
    return imported_items



def export_wcu(filename, cat_names_to_export, reset_learning_data=False):
    
    try:
        if os.path.splitext(filename)[1] == '.wcu':
            outfile = file(filename,'w')
        else:
            outfile = file(filename+'.wcu','w')
    except:
        return False
    
    print >> outfile, '<?xml version="1.0" encoding="utf-8"?>'
    print >> outfile, '<CueCards Version="1">'
    
    for e in items:
        if e.cat.name in cat_names_to_export:
            question = e.q.encode("utf-8")
            question = question.replace("\n", "<br/>")
            answer = e.a.encode("utf-8")
            answer = answer.replace("\n", "<br/>")
            print >> outfile, '<Card Question="'+question+\
                  '" Answer="'+answer+'" History=""/>'

    print >> outfile, '</CueCards>'
    outfile.close()
    
    return True

register_file_format("Cuecard .wcu",
                     filter="Cuecard files (*.wcu *.WCU)",
                     import_function=import_wcu,
                     export_function=export_wcu)



##############################################################################
#
# calculate_initial_interval
#
##############################################################################

def calculate_initial_interval(grade):

    # If this is the first time we grade this item, allow for slightly
    # longer scheduled intervals, as we might know this item from before.

    interval = (0, 0, 1, 3, 4, 5) [grade]
    return interval



##############################################################################
#
# calculate_interval_noise
#
##############################################################################

def calculate_interval_noise(interval):

    if interval == 0:
        noise = 0
    elif interval == 1:
        noise = random.randint(0,1)
    elif interval <= 10:
        noise = random.randint(-1,1)
    elif interval <= 60:
        noise = random.randint(-3,3)
    else:
        a = .05 * interval
        noise = int(random.uniform(-a,a))

    return noise



##############################################################################
#
# add_new_item
#
##############################################################################

def add_new_item(grade, question, answer, cat_name, id=None):

    global items, load_failed

    item = Item()
    
    item.q     = question
    item.a     = answer
    item.cat   = get_category_by_name(cat_name)
    item.grade = grade
    
    item.acq_reps = 1
    item.acq_reps_since_lapse = 1

    item.last_rep = days_since_start
    
    item.easiness = average_easiness()

    if id == None:
        item.new_id()
    else:
        item.id = id 
    
    new_interval  = calculate_initial_interval(grade)
    new_interval += calculate_interval_noise(new_interval)
    item.next_rep = days_since_start + new_interval
    
    items.append(item)    

    logger.info("New item %s %d %d", item.id, item.grade, new_interval)

    load_failed = False
    
    return item



##############################################################################
#
# delete_item
#
##############################################################################

def delete_item(e):

    old_cat = e.cat
    
    items.remove(e)
    rebuild_revision_queue()
    remove_category_if_unused(old_cat)

    logger.info("Deleted item %s", e.id)



##############################################################################
#
# rebuild_revision_queue
#
##############################################################################

def rebuild_revision_queue(learn_ahead = False):
            
    global revision_queue
    
    revision_queue = []

    if len(items) == 0:
        return

    time_of_start.update_days_since()

    # Always add items that are due for revision.

    revision_queue = [i for i in items if i.is_due_for_retention_rep()]
    random.shuffle(revision_queue)

    # If the queue is empty, then add items which are not yet memorised.
    # Take only a limited number of grade 0 items from the unlearned items,
    # to avoid too long intervals between repetitions.
    
    if len(revision_queue) == 0:
        
        not_memorised = [i for i in items if i.is_due_for_acquisition_rep()]

        grade_0 = [i for i in not_memorised if i.grade == 0]
        grade_1 = [i for i in not_memorised if i.grade == 1]

        limit = get_config("grade_0_items_at_once")

        grade_0_selected = []

        if limit != 0:
            for i in grade_0:
                for j in grade_0_selected:
                    if items_are_inverses(i, j):
                        break
                else:
                    grade_0_selected.append(i)

                if len(grade_0_selected) == limit:
                    break

        random.shuffle(grade_0_selected)
        revision_queue[0:0] = grade_0_selected

        random.shuffle(grade_1)
        revision_queue[0:0] = grade_1
        
        random.shuffle(grade_0_selected)
        revision_queue[0:0] = grade_0_selected

    # If the queue is still empty, then simply return. The user can signal
    # that he wants to learn ahead by calling rebuild_revision_queue with
    # 'learn_ahead' set to True. Don't shuffle this queue, as it's more
    # useful to review the earliest scheduled items first.

    if len(revision_queue) == 0:
        
        if learn_ahead == False:
            return
        else:
            revision_queue = [i for i in items \
                              if i.qualifies_for_learn_ahead()]

            revision_queue.sort(key=Item.sort_key)



##############################################################################
#
# in_revision_queue
#
##############################################################################

def in_revision_queue(item):
    return item in revision_queue



##############################################################################
#
# remove_from_revision_queue
#
#   Remove a single instance of an item from the queue. Necessary when
#   the queue needs to be rebuilt, and there is still a question pending.
#
##############################################################################

def remove_from_revision_queue(item):
    
    global revision_queue
    
    for i in revision_queue:
        if i.id == item.id:
            revision_queue.remove(i)
            return



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
# get_new_question
#
##############################################################################

def get_new_question(learn_ahead = False):
            
    # Populate list if it is empty.
        
    if len(revision_queue) == 0:
        rebuild_revision_queue(learn_ahead)
        if len(revision_queue) == 0:
            return None

    # Pick the first question and remove it from the queue.

    item = revision_queue[0]
    revision_queue.remove(item)

    return item



##############################################################################
#
# process_answer
#
##############################################################################

def process_answer(item, new_grade, dry_run=False):

    global revision_queue, items

    # When doing a dry run, make a copy to operate on. Note that this
    # leaves the original in items and the reference in the GUI intact.

    if dry_run:
        item = copy.copy(item)

    # Calculate scheduled and actual interval, taking care of corner
    # case when learning ahead on the same day.
    
    scheduled_interval = item.next_rep    - item.last_rep
    actual_interval    = days_since_start - item.last_rep

    if actual_interval == 0:
        actual_interval = 1 # Otherwise new interval can become zero.

    if item.is_new():

        # The item is not graded yet, e.g. because it is imported.

        item.acq_reps = 1
        item.acq_reps_since_lapse = 1

        new_interval = calculate_initial_interval(new_grade)

        # Make sure the second copy of a grade 0 item doesn't show up again.

        if not dry_run and item.grade == 0 and new_grade in [2,3,4,5]:
            for i in revision_queue:
                if i.id == item.id:
                    revision_queue.remove(i)
                    break

    elif item.grade in [0,1] and new_grade in [0,1]:

        # In the acquisition phase and staying there.
    
        item.acq_reps += 1
        item.acq_reps_since_lapse += 1
        
        new_interval = 0

    elif item.grade in [0,1] and new_grade in [2,3,4,5]:

         # In the acquisition phase and moving to the retention phase.

         item.acq_reps += 1
         item.acq_reps_since_lapse += 1

         new_interval = 1

         # Make sure the second copy of a grade 0 item doesn't show up again.

         if not dry_run and item.grade == 0:
             for i in revision_queue:
                 if i.id == item.id:
                     revision_queue.remove(i)
                     break

    elif item.grade in [2,3,4,5] and new_grade in [0,1]:

         # In the retention phase and dropping back to the acquisition phase.

         item.ret_reps += 1
         item.lapses += 1
         item.acq_reps_since_lapse = 0
         item.ret_reps_since_lapse = 0

         new_interval = 0

         # Move this item to the front of the list, to have precedence over
         # items which are still being learned for the first time.

         if not dry_run:
             items.remove(item)
             items.insert(0,item)

    elif item.grade in [2,3,4,5] and new_grade in [2,3,4,5]:

        # In the retention phase and staying there.

        item.ret_reps += 1
        item.ret_reps_since_lapse += 1

        if actual_interval >= scheduled_interval:
            if new_grade == 2:
                item.easiness -= 0.16
            if new_grade == 3:
                item.easiness -= 0.14
            if new_grade == 5:
                item.easiness += 0.10
            if item.easiness < 1.3:
                item.easiness = 1.3
            
        new_interval = 0
        
        if item.ret_reps_since_lapse == 1:
            new_interval = 6
        else:
            if new_grade == 2 or new_grade == 3:
                if actual_interval <= scheduled_interval:
                    new_interval = actual_interval * item.easiness
                else:
                    new_interval = scheduled_interval
                    
            if new_grade == 4:
                new_interval = actual_interval * item.easiness
                
            if new_grade == 5:
                if actual_interval < scheduled_interval:
                    new_interval = scheduled_interval # Avoid spacing.
                else:
                    new_interval = actual_interval * item.easiness

        # Shouldn't happen, but build in a safeguard.

        if new_interval == 0:
            logger.info("Internal error: new interval was zero.")
            new_interval = scheduled_interval

        new_interval = int(new_interval)

    # When doing a dry run, stop here and return the scheduled interval.

    if dry_run:
        return new_interval

    # Add some randomness to interval.

    noise = calculate_interval_noise(new_interval)

    # Update grade and interval.
    
    item.grade    = new_grade
    item.last_rep = days_since_start
    item.next_rep = days_since_start + new_interval + noise
    
    # Don't schedule inverse or identical questions on the same day.

    for j in items:
        if (j.q == item.q and j.a == item.a) or items_are_inverses(item, j):
            if j != item and j.next_rep == item.next_rep and item.grade >= 2:
                item.next_rep += 1
                noise += 1
                
    # Create log entry.
        
    logger.info("R %s %d %1.2f | %d %d %d %d %d | %d %d | %d %d | %1.1f",
                item.id, item.grade, item.easiness,
                item.acq_reps, item.ret_reps, item.lapses,
                item.acq_reps_since_lapse, item.ret_reps_since_lapse,
                scheduled_interval, actual_interval,
                new_interval, noise, thinking_time)

    return new_interval + noise



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
    
    logger.info("Program stopped")

    os.remove(os.path.join(basedir,"MNEMOSYNE_LOCK"))
    
