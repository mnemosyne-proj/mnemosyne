##############################################################################
#
# pickle.py <Peter.Bienstman@UGent.be>
#
#  TODO: abstract out logging messages so that they are automatically the
#  same in the other databases?
#
##############################################################################

import logging, os, cPickle, datetime, gzip, shutil
import mnemosyne.version

from mnemosyne.libmnemosyne.database import Database
from mnemosyne.libmnemosyne.config import config
from mnemosyne.libmnemosyne.start_date import start_date
from mnemosyne.libmnemosyne.utils import expand_path, contract_path
from mnemosyne.libmnemosyne.exceptions import *
from mnemosyne.libmnemosyne.category import Category
from mnemosyne.libmnemosyne.plugin_manager import plugin_manager

log = logging.getLogger("mnemosyne")

database_header_line \
        = "--- Mnemosyne Data Base --- Format Version %s ---" \
          % mnemosyne.version.dbVersion

    

##############################################################################
#
# Pickle
#
##############################################################################

class Pickle(Database):
    
    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self):

        self.categories = []
        self.facts = []
        self.cards = []
        
        self.load_failed = False



    ##########################################################################
    #
    # new
    #
    ##########################################################################

    def new(self, path):

        if self.is_loaded != 0:
            self.unload()

        self.load_failed = False

        start_date.init()

        config["path"] = path

        log.info("New database")

        self.save(contract_path(path, config.basedir))



    ##########################################################################
    #
    # load
    #
    ##########################################################################

    # TODO: will we check the version string?

    def load(path):

        path = expand_path(path, config.basedir)

        if self.is_loaded():
            unload_database()

        if not os.path.exists(path):
            self.load_failed = True
            raise IOError

        try:
            infile = file(path, 'rb')
            header_line = infile.readline().rstrip()

            if not header_line.startswith("--- Mnemosyne Data Base"):
                infile = file(path, 'rb')

            db = cPickle.load(infile)

            start_date.start = db[0]
            self.categories  = db[1]
            self.facts       = db[2]
            self.cards       = db[3]

            infile.close()

            self.load_failed = False

        except:
            self.load_failed = True

            raise InvalidFormatError(stack_trace=True)

        for c in self.categories:
            remove_category_if_unused(c)

        config["path"] = contract_path(path, basedir)

        log.info("Loaded database %d %d %d", scheduled_cards(), \
                    non_memorised_cards(), number_of_cards())

        for f in plugin_manager.get_all_plugins("after_load"):
            if f.active:
                f.run()



    ##########################################################################
    #
    # save
    #
    ##########################################################################

    def save(self, path):

        path = expand_path(path, config.basedir)
        
        # Don't erase a database which failed to load.
        
        if self.load_failed == True:
    
            return

        try:

            # Write to a backup file first, as shutting down Windows can
            # interrupt the dump command and corrupt the database.

            outfile = file(path + "~", 'wb')

            print >> outfile, database_header_line

            # This unfortunately fails.. Bug in sip?
            db = [start_date.start, self.categories, self.facts, self.cards]
            #cPickle.dump(db, outfile)

            outfile.close()

            shutil.move(path + "~", path) # Should be atomic.

        except:
            print traceback_string()
            raise SaveError()

        config["path"] = contract_path(path, config.basedir)



    ##########################################################################
    #
    # unload_database
    #
    ##########################################################################

    def unload_database():

        self.save(config["path"])

        log.info("Saved database %d %d %d", self.scheduled_count(), \
                    self.non_memorised_count(), self.card_count())
        
        self.categories = []
        self.facts = []
        self.cards = []

        get_scheduler().clear_queue()

        return True



    ##########################################################################
    #
    # backup_database
    #
    ##########################################################################

    def backup_database():

        if not self.is_loaded():
            return

        backupdir = unicode(os.path.join(config.basedir, "backups"))

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

        if config["backups_to_keep"] < 0:
            return

        files = [f for f in os.listdir(backupdir) if f.startswith(db_name + "-")]
        files.sort()
        if len(files) > config["backups_to_keep"]:
            os.remove(os.path.join(backupdir, files[0]))

    ##########################################################################
    #
    # is_loaded
    #
    ##########################################################################

    def is_loaded(self):
        return len(self.facts) != 0
    
    def add_category(self, category):
        raise NotImplementedError

    def modify_category(self, id, modified_category):
        raise NotImplementedError
    
    def delete_category(self, category):
        raise NotImplementedError


    ##########################################################################
    #
    # get_or_create_category_with_name
    #
    # TODO: benchmark this and see if we need a dictionary category_by_name.
    #
    ##########################################################################

    def get_or_create_category_with_name(self, name):

        if name not in (c.name for c in self.categories):    
            category = Category(name)
            self.categories.append(category)
            return category
        else:
            for c in self.categories:
                if c.name == name:
                    return c
            

    
    ##########################################################################
    #
    # remove_category_if_unused
    #
    # TODO: implement
    #
    ##########################################################################

    def remove_category_if_unused(self, cat):

        for card in self.cards:
            if cat.name == card.cat.name:
                break
        else:
            del category_by_name[cat.name]
        categories.remove(cat)

    
    def add_fact(self, fact):
        self.load_failed = False
        self.facts.append(fact)

    def modify_fact(self, id, modified_fact):
        raise NotImplementedError
    
    def delete_fact(self, fact):
        raise NotImplementedError
    
    def add_card(self, card): # should also link fact to new card
        self.load_failed = False
        self.cards.append(card)
        # The cylic reference here seems to break the pickle operation..
        card.fact.cards.append(card) # TODO: fix

    def modify_card(self, id, modified_card):
        raise NotImplementedError
    
    def delete_card(self, id, card):
        raise NotImplementedError
    
    ##########################################################################
    #
    # delete_card
    #
    ##########################################################################

    def delete_card(c):

        old_cat = c.cat

        cards.remove(c)
        rebuild_revision_queue()
        remove_category_if_unused(old_cat)

        log.info("Deleted card %s", c.id)


    ##########################################################################
    #
    # category_names
    #
    ##########################################################################
    
    def category_names(self):
        return (c.name for c in self.categories)

    
    ##########################################################################
    #
    # card_count
    #
    ##########################################################################

    def card_count(self):
        return len(self.cards)



    ##########################################################################
    #
    # non_memorised_count
    #
    ##########################################################################

    def non_memorised_count(self):
        return sum(1 for c in self.cards if (c.grade < 2) and \
                                             c.is_in_active_category())



    ##########################################################################
    #
    # scheduled_count
    #
    #   Number of cards scheduled within 'days' days.
    #
    ##########################################################################

    def scheduled_count(self, days=0):
        
        days_from_start = start_date.days_since_start()
        
        return sum(1 for c in self.cards if (c.grade >= 2) and \
                            c.is_in_active_category() and \
                           (days_since_start >= c.next_rep - days))



    ##########################################################################
    #
    # active_cards
    #
    #   Number of cards in an active category.
    #
    ##########################################################################

    def active_count(self):
        return sum(1 for c in self.cards if c.is_in_active_category())



    ##########################################################################
    #
    # average_easiness
    #
    ##########################################################################

    def average_easiness(self):

        if len(self.cards) == 0:
            return 2.5
        else:
            return sum(c.easiness for c in self.cards) / len(self.cards)



    ##########################################################################
    #
    # cards_due_for_ret_rep
    #
    ##########################################################################
    
    def cards_due_for_ret_rep(self, sort_key):
        
        days_from_start = start_date.days_since_start()
        
        c = [c for c in self.cards if (c.grade >= 2) and \
                            c.is_in_active_category() and \
                           (days_since_start >= c.next_rep)]

        c.sort(key=sort_key)

        return c



    ##########################################################################
    #
    # cards_due_for_final_review
    #
    ##########################################################################
    
    def cards_due_for_final_review(self, grade):
       
        return (c for c in self.cards if c.grade == grade and c.lapses > 0 \
                                        and c.is_in_active_category())


    ##########################################################################
    #
    # cards_new_memorising
    #
    ##########################################################################
    
    def cards_new_memorising(self, grade):
       
        return (c for c in self.cards if c.grade == grade and c.lapses == 0 \
                     and c.acq_reps > 1 and c.is_in_active_category())
