##############################################################################
#
# pickle.py <Peter.Bienstman@UGent.be>
#
##############################################################################

_cards = []
_facts = []



##############################################################################
#
# Pickle
#
##############################################################################

class Pickle(Database):

    pass



# TODO: Integrate code dumped below


##############################################################################
#
# new_database
#
##############################################################################

def new_database(path):

    global load_failed

    if list_is_loaded():
        unload_database()

    load_failed = False

    initialise_time_of_start()
    set_config("path", path)

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

    set_config("path", contract_path(path, basedir))

    logger.info("Loaded database %d %d %d", scheduled_cards(), \
                non_memorised_cards(), number_of_cards())

    if "after_load" in function_hooks:
        for f in function_hooks["after_load"]:
            f()



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

        # TODO: fix storage, as these variables are no longer available here.
        
        db = [time_of_start, categories, cards]
        cPickle.dump(db, outfile)

        outfile.close()

        shutil.move(path + "~", path) # Should be atomic.
        
    except:
        pass
        #print traceback_string()
        #raise SaveError()

    set_config("path", contract_path(path, basedir))



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
# list_is_loaded
#
##############################################################################

def list_is_loaded():
    return len(cards) != 0   

##############################################################################
#
# number_of_cards
#
##############################################################################

def number_of_cards():
    return len(cards)



##############################################################################
#
# non_memorised_cards
#
##############################################################################

def non_memorised_cards():
    return sum(1 for i in cards if i.is_due_for_acquisition_rep())



##############################################################################
#
# scheduled_cards
#
#   Number of cards scheduled within 'days' days.
#
##############################################################################

def scheduled_cards(days=0):
    return sum(1 for i in cards if i.is_due_for_retention_rep(days))



##############################################################################
#
# active_cards
#
#   Number of cards in an active category.
#
##############################################################################

def active_cards():
    return sum(1 for i in cards if i.is_in_active_category())



##############################################################################
#
# average_easiness
#
##############################################################################

def average_easiness():

    if len(cards) == 0:
        return 2.5
    if len(cards) == 1:
        return cards[0].easiness
    else:
        return sum(i.easiness for i in cards) / len(cards)
