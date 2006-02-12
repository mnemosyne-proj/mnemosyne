##############################################################################
#
# Mnemosyne core <Peter.Bienstman@UGent.be>
#
##############################################################################

import random, time, os, string, sys, cPickle, md5, struct, logging
import traceback
logger = logging.getLogger("mnemosyne")



##############################################################################
#
# Global variables
#
##############################################################################

time_of_start = None
import_time_of_start = None

thinking_time = 0
time_of_last_question = 0

upload_thread = None

load_failed = False

items = []
import_items = []
revision_queue = []

categories = []
category_by_name = {}

config = {}



##############################################################################
#
# initialise
#
##############################################################################

def initialise():

    import mnemosyne_log

    global upload_thread, load_failed

    load_failed = False

    join   = os.path.join
    exists = os.path.exists
    
    # Set default paths.

    basedir = os.path.join(os.path.expanduser("~"), ".mnemosyne")

    if not exists(basedir):
        os.mkdir(basedir)
    
    if not exists(join(basedir,"config")):
        init_config()
        save_config()    
     
    if not exists(join(basedir,"default.mem")):
        new_database(join(basedir,"default.mem"))
    
    if not exists(join(basedir,"history")):
        os.mkdir(join(basedir,"history"))

    load_config()

    mnemosyne_log.archive_old_log()
    
    mnemosyne_log.start_logging()

    if get_config("upload_logs") == True:
        upload_thread = mnemosyne_log.Uploader()
        upload_thread.start()

    import mnemosyne.version
    logger.info("Program started : Mnemosyne " + mnemosyne.version.version)



##############################################################################
#
# init_config
#
##############################################################################

def init_config():
    global config

    basedir = os.path.join(os.path.expanduser("~"), ".mnemosyne")
 
    if not config.has_key("first_run"):        
        config["first_run"] = True
    if not config.has_key("path"):
        config["path"] = os.path.join(basedir, "default.mem")
    if not config.has_key("import_dir"):        
        config["import_dir"] = basedir
    if not config.has_key("user_id"):                          
        config["user_id"] = md5.new(str(random.random())).hexdigest()[0:8]
    if not config.has_key("keep_logs"):              
        config["keep_logs"] = True
    if not config.has_key("upload_logs"):              
        config["upload_logs"] = True
    if not config.has_key("upload_server"):              
        config["upload_server"] = "mnemosyne-proj.dyndns.org:80"    
    if not config.has_key("log_index"):              
        config["log_index"] = 1
    if not config.has_key("hide_toolbar"):         
        config["hide_toolbar"] = False
    if not config.has_key("QA_font"):               
        config["QA_font"] = None
    if not config.has_key("list_font"):               
        config["list_font"] = None
    if not config.has_key("left_align"):        
        config["left_align"] = False
    if not config.has_key("check_duplicates_when_adding"):      
        config["check_duplicates_when_adding"] = True
    if not config.has_key("allow_duplicates_in_diff_cat"):     
        config["allow_duplicates_in_diff_cat"] = True



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

    basedir = os.path.join(os.path.expanduser("~"), ".mnemosyne")

    try:
        config_file = file(os.path.join(basedir, "config"), 'r')
        for k,v in cPickle.load(config_file).iteritems():
            config[k] = v
    except:
        pass

    init_config()



##############################################################################
#
# save_config
#
##############################################################################

def save_config():
    basedir = os.path.join(os.path.expanduser("~"), ".mnemosyne")
    config_file = file(os.path.join(basedir,"config"), 'w')
    cPickle.dump(config, config_file)



##############################################################################
#
# StartTime
#
##############################################################################

class StartTime:

    def __init__(self, start_time):

        # Reset to 3.30 am

        t = time.localtime(start_time)
        self.time = time.mktime([t[0],t[1],t[2], 3,30,0, t[6],t[7],t[8]])

    def days_since(self):
        return long( (time.time() - self.time) / 60. / 60. / 24. )

        
    
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
        
        self.grade                = 0
        self.easiness             = 2.5
        
        self.acq_reps             = 0
        self.ret_reps             = 0
        self.lapses               = 0
        self.acq_reps_since_lapse = 0
        self.ret_reps_since_lapse = 0
        
        self.last_rep  = 0 # In days since beginning.
        self.next_rep  = 0 #
        
        self.q         = None
        self.a         = None
        self.cat       = None
    
    ##########################################################################
    #
    # new_id
    #
    ##########################################################################
    
    def new_id(self):

        digest = md5.new(self.q + self.a + time.ctime()).hexdigest()
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
               (time_of_start.days_since() >= self.next_rep - days)

    ##########################################################################
    #
    # qualifies_for_learn_ahead
    #
    ##########################################################################
    
    def qualifies_for_learn_ahead(self):
        return (self.grade >= 2) and (self.cat.active == True) and \
               (time_of_start.days_since() < self.next_rep) 
        
    ##########################################################################
    #
    # change_category
    #
    ##########################################################################
    
    def change_category(self, new_cat_name):

        global categories, category_by_name

        # Case 1: a new category was created.

        if new_cat_name not in category_by_name.keys():
            cat = Category(new_cat_name)
            categories.append(cat)
            category_by_name[new_cat_name] = cat

        old_cat = self.cat
        self.cat = category_by_name[new_cat_name]
    
        # Case 2: deleted last item of old_cat.

        if old_cat.in_use() == False:
            del category_by_name[old_cat.name]
            categories.remove(old_cat)



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
# get_category_by_name
#
##############################################################################

def get_category_by_name(name):
    return category_by_name[name]



##############################################################################
#
# get_category_names
#
##############################################################################

def get_category_names():
    return category_by_name.keys()



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

    save_database(path)



##############################################################################
#
# load_database
#
##############################################################################

def load_database(path):

    global config, time_of_start, categories, category_by_name, items
    global load_failed

    if list_is_loaded():
        unload_database()

    try:
        infile = file(path)
        db = cPickle.load(infile)

        time_of_start = db[0]
        categories    = db[1]
        items         = db[2]
        
        infile.close()

        load_failed = False

    except:

        load_failed = True
        
        return False

    for c in categories:
        if not c.in_use():
            categories.remove(c)
        else:
            category_by_name[c.name] = c

    config["path"] = path

    logger.info("Loaded database %d %d %d", scheduled_items(), \
                non_memorised_items(), number_of_items())
    
    return True



##############################################################################
#
# save_database
#
##############################################################################

def save_database(path):

    global config

    if load_failed == True: # Don't erase a database which failed to load.
        return False
        
    try:
        outfile = file(path,'w')

        db = [time_of_start, categories, items]
        cPickle.dump(db, outfile)

        outfile.close()
    except:
        return False

    config["path"] = path
    
    return True



##############################################################################
#
# unload_database
#
##############################################################################

def unload_database():

    global items, revision_queue, categories, category_by_name
        
    status = save_database(config["path"])
    if status == False:
        return False
    
    logger.info("Saved database %d %d %d", scheduled_items(), \
                non_memorised_items(), number_of_items())        
    items = []
    revision_queue = []
        
    categories = []
    category_by_name = {}
    
    return True



##############################################################################
#
# list_is_loaded
#
##############################################################################

def list_is_loaded():
    return len(items) != 0



##############################################################################
#
# escape
#
#   Escapes literal < (unmatched tag) and new line from string.
#
##############################################################################

def escape(old_string):
    
    hanging = []
    open = 0
    pending = 0

    for i in range(len(old_string)):
        if old_string[i] == '<':
            if open != 0:
                hanging.append(pending)
                pending = i
                continue
            open += 1
            pending = i
        elif old_string[i] == '>':
            if open > 0:
                open -= 1

    if open != 0:
        hanging.append(pending)

    new_string = ""
    for i in range(len(old_string)):
        if old_string[i] == '\n':
            new_string += "<br>"
        elif i in hanging:
            new_string += "&lt;"
        else:
            new_string += old_string[i]

    return new_string



##############################################################################
#
# write_item_XML
#
##############################################################################

def write_item_XML(e, outfile):
    
    print >> outfile, "<item id=\""+str(e.id) + "\"" \
                         + " gr=\""+str(e.grade) + "\"" \
                         + " e=\""+str(e.easiness) + "\"" \
                         + " ac_rp=\""+str(e.acq_reps) + "\"" \
                         + " rt_rp=\""+str(e.ret_reps) + "\""  \
                         + " lps=\""+str(e.lapses) + "\"" \
                         + " ac_rp_l=\""+str(e.acq_reps_since_lapse) + "\"" \
                         + " rt_rp_l=\""+str(e.ret_reps_since_lapse) + "\""  \
                         + " l_rp=\""+str(e.last_rep) + "\"" \
                         + " n_rp=\""+str(e.next_rep) + "\">"
    print >> outfile, " <cat><![CDATA["+e.cat.name+"]]></cat>"
    print >> outfile, " <Q><![CDATA["+e.q+"]]></Q>"
    print >> outfile, " <A><![CDATA["+e.a+"]]></A>"
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

def write_category_XML(category, outfile):
    
    print >> outfile, "<category active=\"" \
          + bool_to_digit(category.active) + "\">"
    print >> outfile, " <name><![CDATA["+category.name \
          +"]]></name>"
    print >> outfile, "</category>"

    

##############################################################################
#
# export_XML
#
##############################################################################

def export_XML(path, cat_names_to_export):
    
    outfile = file(path,'w')

    print >> outfile, """<?xml version="1.0" encoding="UTF-8"?>"""
    print >> outfile, "<mnemosyne core_version=\"0\" time_of_start=\""\
                      +str(long(time_of_start.time))+"\">"
    
    for cat in categories:
        if cat.name in cat_names_to_export:
            write_category_XML(cat, outfile)

    for e in items:
        if e.cat.name in cat_names_to_export:
            write_item_XML(e, outfile)

    print >> outfile, """</mnemosyne>"""

    outfile.close()



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
        else:
            self.reading[name] = True
            self.text[name] = ""

    def characters(self, ch):
        for name in self.reading.keys():
            if self.reading[name] == True:
                self.text[name] += ch

    def endElement(self, name):

        global import_items, categories, category_by_name
    
        self.reading[name] = False

        # An item ends with 'A'.
       
        if name == "A":

            self.item.q = unicode(self.text["Q"]).encode("utf-8")
            self.item.a = unicode(self.text["A"]).encode("utf-8")

            # Don't add if the item is already in the database.

            for i in get_items():
                if i.q == self.item.q and i.a == self.item.a:
                    return

            if "cat" in self.text.keys():
                cat_name = unicode(self.text["cat"]).encode("utf-8")
                if not cat_name in category_by_name.keys():
                    new_cat = Category(cat_name)
                    categories.append(new_cat)
                    category_by_name[cat_name] = new_cat
                self.item.cat = category_by_name[cat_name]
            else:
                self.item.cat = self.default_cat

            if self.item.id == 0:
                self.item.new_id()
                
            if self.reset_learning_data == True:
                self.item.new_id()
                self.item.grade    = 0
                self.item.ret_reps = 0
                self.item.next_rep = 0
                self.item.last_rep = 0

            import_items.append(self.item)

        # A category ends with 'name'.

        elif name == "name":
            
            name = unicode(self.text["name"]).encode("utf-8")
            
            if name not in category_by_name.keys():
                cat = Category(name, self.active)
                categories.append(cat)
                category_by_name[name] = cat



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

        global import_items, categories, category_by_name
    
        self.reading[name] = False

        # An item ends with 'A'.
       
        if name == "A":

            self.item.q = unicode(self.text["Q"]).encode("utf-8")
            self.item.a = unicode(self.text["A"]).encode("utf-8")

            # Don't add if the item is already in the database.

            for i in get_items():
                if i.q == self.item.q and i.a == self.item.a:
                    return

            if "cat" in self.text.keys():
                cat_name = unicode(self.text["cat"]).encode("utf-8")
                if not cat_name in category_by_name.keys():
                    new_cat = Category(cat_name)
                    categories.append(new_cat)
                    category_by_name[cat_name] = new_cat
                self.item.cat = category_by_name[cat_name]
            else:
                self.item.cat = self.default_cat

            if self.item.id == 0:
                self.item.new_id()

            if self.reset_learning_data == True:
                self.item.new_id()
                self.item.grade    = 0
                self.item.ret_reps = 0
                self.item.next_rep = 0
                self.item.last_rep = 0

            import_items.append(self.item)

        # A category ends with 'name'.

        elif name == "name":
            
            name = unicode(self.text["name"]).encode("utf-8")
            
            if name not in category_by_name.keys():
                cat = Category(name, self.active)
                categories.append(cat)
                category_by_name[name] = cat

             

##############################################################################
#
# import_XML
#
##############################################################################

def import_XML(filename, default_cat_name, reset_learning_data=False):
    
    global import_items, categories, category_by_name, load_failed
    global items, revision_queue

    # If no database is active, create one.

    if not time_of_start:
        new_database(config["path"])

    # Create default category if necessary.

    if default_cat_name not in category_by_name.keys():
        default_cat = Category(default_cat_name)
        categories.append(default_cat)
        category_by_name[default_cat_name] = default_cat
    else:
        default_cat = category_by_name[default_cat_name]

    # Determine if we import a Mnemosyne or a Memaid file.

    handler = None
    
    f = file(filename)
    f.readline()

    if "mnemosyne" in f.readline():
        handler = XML_Importer(default_cat, reset_learning_data)
    else:
        handler = memaid_XML_Importer(default_cat, reset_learning_data)
        
    f.close()

    # Parse XML file.

    parser = make_parser()
    parser.setFeature(feature_namespaces, 0)
    parser.setContentHandler(handler)

    try:
        parser.parse(file(filename))
    except Exception, e:
        print "Error parsing XML:\n"
        traceback.print_exc()
        return False

    # Calculate offset with current start date.
    
    cur_start_date =        time_of_start.time
    imp_start_date = import_time_of_start.time
    
    offset = long(round((cur_start_date - imp_start_date) / 60. / 60. / 24.))
        
    # Adjust timings.

    if reset_learning_data == False:
        if cur_start_date <= imp_start_date :
            for item in import_items:
                item.last_rep += abs(offset)
                item.next_rep += abs(offset)
        else:
            time_of_start.time = imp_start_date
            for item in items:
                item.last_rep += abs(offset)
                item.next_rep += abs(offset)
            
    # Add new items.
    
    for item in import_items:
                    
        items.append(item)
        
        if item.is_due_for_retention_rep():
            revision_queue[0:0] = [item]
            
        interval = time_of_start.days_since() - item.next_rep
        logger.info("Imported item %s %d %d %d %d %d",
                    item.id, item.grade, item.ret_reps,
                    item.last_rep, item.next_rep, interval)

    # Clean up.

    if default_cat.in_use() == False:
        del category_by_name[default_cat.name]
        categories.remove(default_cat)
        
    import_items = []

    load_failed = False

    return True



##############################################################################
#
# import_txt
#
##############################################################################

def import_txt(filename, default_cat_name):
    
    global categories, category_by_name, load_failed, items

    # If no database is active, create one.

    if not time_of_start:
        new_database(config["path"])

    # Create default category if necessary.

    if default_cat_name not in category_by_name.keys():
        default_cat = Category(default_cat_name)
        categories.append(default_cat)
        category_by_name[default_cat_name] = default_cat
    else:
        default_cat = category_by_name[default_cat_name]

    # Parse txt file.

    avg_easiness = average_easiness()

    f = file(filename, 'r')

    for line in f:
        
        item = Item()

        try:
            item.q, item.a = line.split('\t')
        except Exception, e:
            print "Error parsing txt file:\n"
            traceback.print_exc()
            return False

        #print item.q, item.a
     
        # Swallow EOL.

        if item.a[-2:] == '\r\n':
            item.a = item.a[:-2]
            
        if item.a[-1:] == '\n':
            item.a = item.a[:-1]

        # Encode utf-8.

        #item.q = item.q.encode("utf-8")
        #item.a = item.a.encode("utf-8")
        
        #print item.q, item.a
        
        # Don't add if the item is already in the database.

        unique = True
        
        for i in get_items():
            if i.q == item.q and i.a == item.a:
                unique = False
                continue

        if unique == False:
            continue
        
        item.easiness = avg_easiness
        item.cat = default_cat
        item.new_id()
                    
        items.append(item)
            
        interval = time_of_start.days_since() - item.next_rep
        logger.info("Imported item %s %d %d %d %d %d",
                    item.id, item.grade, item.ret_reps,
                    item.last_rep, item.next_rep, interval)

    # Clean up.

    if default_cat.in_use() == False:
        del category_by_name[default_cat.name]
        categories.remove(default_cat)

    load_failed = False

    return True



##############################################################################
#
# import_file
#
##############################################################################

def import_file(filename, default_cat_name, reset_learning_data=False):
    
    if filename[-4:] == '.xml' or filename[-4:] == '.XML':
        return import_XML(filename, default_cat_name, reset_learning_data)
        
    if filename[-4:] == '.txt' or filename[-4:] == '.TXT':
        return import_txt(filename, default_cat_name)

    return False



##############################################################################
#
# add_new_item
#
##############################################################################

def add_new_item(grade, question, answer, cat_name):

    global items, categories, category_by_name, load_failed

    if cat_name not in category_by_name.keys():
        cat = Category(cat_name)
        categories.append(cat)
        category_by_name[cat_name] = cat
    else:
        cat = category_by_name[cat_name]
    
    item = Item()
    
    item.q     = question
    item.a     = answer
    item.cat   = cat
    item.grade = grade

    item.easiness = average_easiness()
    
    item.new_id()

    new_interval = 0

    if grade == 2 or grade == 3:
        new_interval = random.randint(1,2)
    if grade == 4:
        new_interval = random.randint(2,3)
    if grade == 5:
        new_interval = random.randint(3,6)        
 
    item.next_rep = time_of_start.days_since() + new_interval
    
    items.insert(0,item)

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
    
    if old_cat.in_use() == False:
        del category_by_name[old_cat.name]
        categories.remove(old_cat)

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

    # Always add items that are due for revision.

    revision_queue = [i for i in items if i.is_due_for_retention_rep()]
    random.shuffle(revision_queue)

    # If the queue is empty, then add items which are not yet memorised.
    # Take only the first five grade 0 items from the unlearned items,
    # to avoid too long intervals between repetitions.
    
    if len(revision_queue) == 0:
        
        not_memorised = [i for i in items if i.is_due_for_acquisition_rep()]

        grade_0 = [i for i in not_memorised if i.grade == 0][0:5]
        grade_1 = [i for i in not_memorised if i.grade == 1]

        random.shuffle(grade_0)
        revision_queue[0:0] = grade_0

        random.shuffle(grade_1)
        revision_queue[0:0] = grade_1
        
        random.shuffle(grade_0)
        revision_queue[0:0] = grade_0

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
# still_exits
#
##############################################################################

def still_exits(item):
    return item in items



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

def process_answer(item, new_grade):

    global revision_queue

    scheduled_interval = item.next_rep              - item.last_rep
    actual_interval    = time_of_start.days_since() - item.last_rep

    rebuild_needed = False

    # In the acquisition phase and staying there.
    
    if item.grade in [0,1] and new_grade in [0,1]:

        item.acq_reps += 1
        item.acq_reps_since_lapse += 1
        
        new_interval = 0

    # In the acquisition phase and moving to the retention phase.

    if item.grade in [0,1] and new_grade in [2,3,4,5]:

         item.acq_reps += 1
         item.acq_reps_since_lapse += 1

         new_interval = 1

         # Make sure the second copy of a grade 0 item doesn't show up again.

         if item.grade == 0:
             for i in revision_queue:
                 if i.id == item.id:
                     revision_queue.remove(i)
                     break

    # In the retention phase and dropping back to the acquisition phase.

    if item.grade in [2,3,4,5] and new_grade in [0,1]:

         item.ret_reps += 1
         item.lapses += 1
         item.acq_reps_since_lapse = 0
         item.ret_reps_since_lapse = 0

         new_interval = 0

    # In the retention phase and staying there.

    if item.grade in [2,3,4,5] and new_grade in [2,3,4,5]:

        item.ret_reps += 1
        item.ret_reps_since_lapse += 1

        if actual_interval >= scheduled_interval:
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
            if new_grade == 3:
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

    # Add some randomness to interval.

    if new_interval == 0:
        noise = 0
    elif new_interval == 1:
        noise = random.randint(0,1)
    elif new_interval <= 10:
        noise = random.randint(-1,1)
    elif new_interval <= 60:
        noise = random.randint(-3,3)
    else:
        a = .05 * new_interval
        noise = int(random.uniform(-a,a))

    # Update grade and interval.
    
    item.grade    = new_grade
    item.last_rep = time_of_start.days_since()
    item.next_rep = time_of_start.days_since() + new_interval + noise

    # Don't schedule inverse or identical questions on the same day.

    for j in items:
        if (j.q == item.q and j.a == item.a) or \
           (j.q == item.a and j.a == item.q):
            if j != item and j.next_rep == item.next_rep and item.grade >= 2:
                item.next_rep += 1
                noise += 1
        
    logger.info("R %s %d %1.2f | %d %d %d %d %d | %d %d | %d %d | %1.1f",
                item.id, item.grade, item.easiness,
                item.acq_reps, item.ret_reps, item.lapses,
                item.acq_reps_since_lapse, item.ret_reps_since_lapse,
                scheduled_interval, actual_interval,
                new_interval, noise, thinking_time)
    


##############################################################################
#
# finalise
#
##############################################################################

def finalise():

    if upload_thread:
        print "Waiting for uploader thread to stop...",
        upload_thread.join()
        print "done!"
    
    logger.info("Program stopped")
    
