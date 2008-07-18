##############################################################################
#
# config.py <Peter.Bienstman@UGent.be>
#
##############################################################################

import md5, random, os, sys
from mnemosyne.libmnemosyne.mnemosyne_core import get_basedir

config = {}




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
# init_config
#
# TODO: make sure this does not get called when upgrading
#
##############################################################################

def init_config():
    global config

    basedir = get_basedir()
 
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
    config.setdefault("randomise_new_cards", False)
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

    # TODO: remove if obsolete, otherwise rework.
    
    #if _old__basedir:
#
#        for key in ['import_dir', 'export_dir', 'import_img_dir',
#                    'import_sound_dir']:
#
#            if config[key] == _old_basedir:
#                config[key] = get_basedir()
                
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
# load_config
#
##############################################################################

def load_config():
    global config

    basedir = get_basedir()

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
