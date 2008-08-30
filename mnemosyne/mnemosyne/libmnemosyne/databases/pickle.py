#
# pickle.py <Peter.Bienstman@UGent.be>
#

import os
import cPickle
import datetime
import gzip
import shutil
import mnemosyne.version

from mnemosyne.libmnemosyne.category import Category
from mnemosyne.libmnemosyne.database import Database
from mnemosyne.libmnemosyne.start_date import StartDate
from mnemosyne.libmnemosyne.utils import expand_path, contract_path
from mnemosyne.libmnemosyne.exceptions import InvalidFormatError
from mnemosyne.libmnemosyne.exceptions import SaveError, LoadError
from mnemosyne.libmnemosyne.component_manager import component_manager, config
from mnemosyne.libmnemosyne.component_manager import log, scheduler
from mnemosyne.libmnemosyne.component_manager import card_type_by_id


class Pickle(Database):

    """A simple storage backend, mainly for testing purposes and to help
    flesh out the design. It has several problems:

    * It does not support filtering operations, so it cannot
    activate and deactivate categories.

    * Due to an obscure bug in SIP, we need to replace the card type
    info in fact by a card type id, otherwise we get::

    File "/usr/lib/python2.5/copy_reg.py", line 70, in _reduce_ex
    state = base(self)
    TypeError: the sip.wrapper type cannot be instantiated or sub-classed

    * It is wasteful in memory during queries.

    It would be possible to work around all these limitations, but doing so
    would taint the design of the rest of the library.

    """

    def __init__(self):
        self.start_date = None
        self.categories = []
        self.facts = []
        self.cards = []
        self.fact_views = []
        self.load_failed = False

    def new(self, path):
        if self.is_loaded():
            self.unload()
        self.load_failed = False
        self.start_date = StartDate()
        config()["path"] = path
        log().new_database()
        self.save(contract_path(path, config().basedir))

    def load(self, path):
        path = expand_path(path, config().basedir)
        if self.is_loaded():
            unload_database()
        if not os.path.exists(path):
            self.load_failed = True
            raise LoadError
        try:
            infile = file(path, 'rb')
            db = cPickle.load(infile)
            self.start_date = db[0]
            self.categories = db[1]
            self.facts = db[2]
            self.cards = db[3]
            infile.close()
            self.load_failed = False
        except:
            self.load_failed = True
            raise InvalidFormatError(stack_trace=True)
        # Work around a sip bug: don't store card types, but their ids.
        for f in self.facts:
            f.card_type = card_type_by_id(f.card_type)
        # TODO: This was to remove database inconsistencies. Still needed?
        #for c in self.categories:
        #    self.remove_category_if_unused(c)
        config()["path"] = contract_path(path, config().basedir)
        log().loaded_database()
        for f in component_manager.get_all("after_load"):
            f.run()

    def save(self, path):
        path = expand_path(path, config().basedir)
        # Work around a sip bug: don't store card types, but their ids.
        for f in self.facts:
            f.card_type = f.card_type.id
        # Don't erase a database which failed to load.
        if self.load_failed == True:
            return
        try:
            # Write to a backup file first, as shutting down Windows can
            # interrupt the dump command and corrupt the database.
            outfile = file(path + "~", 'wb')
            db = [self.start_date, self.categories, self.facts, self.cards]
            cPickle.dump(db, outfile)
            outfile.close()
            shutil.move(path + "~", path) # Should be atomic.
        except:
            print traceback_string()
            raise SaveError()
        config()["path"] = contract_path(path, config().basedir)
        # Work around sip bug again.
        for f in self.facts:
            f.card_type = card_type_by_id(f.card_type)


    def unload(self):
        self.save(config()["path"])
        log().saved_database()
        self.start_date = None
        self.categories = []
        self.facts = []
        self.cards = []
        scheduler().clear_queue()
        return True

    def backup(self):
        # TODO: implement
        return

        if not self.is_loaded():
            return
        backupdir = unicode(os.path.join(config().basedir, "backups"))
        # Export to XML. Create only a single file per day.
        db_name = os.path.basename(config()["path"])[:-4]
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
        if config()["backups_to_keep"] < 0:
            return
        files = [f for f in os.listdir(backupdir) if f.startswith(db_name+"-")]
        files.sort()
        if len(files) > config()["backups_to_keep"]:
            os.remove(os.path.join(backupdir, files[0]))

    def is_loaded(self):
        return len(self.facts) != 0

    def set_start_date(self, start_date_obj):
        self.start_date = start_date_obj

    def days_since_start(self):
        return self.start_date.days_since_start()

    def add_category(self, category):
        raise NotImplementedError

    def modify_category(self, modified_category):
        raise NotImplementedError

    def delete_category(self, category):
        raise NotImplementedError

    # TODO: benchmark this and see if we need a dictionary category_by_name.

    def get_or_create_category_with_name(self, name):
        if all(name != c.name for c in self.categories):
            category = Category(name)
            self.categories.append(category)
            return category
        else:
            for c in self.categories:
                if c.name == name:
                    return c

    # TODO: we used to check on name here. OK to check on instance?

    def remove_category_if_unused(self, cat):
        for f in self.facts:
            if cat in f.cat:
                break
        else:
            self.categories.remove(cat)
            del cat

    def add_fact(self, fact):
        self.load_failed = False
        self.facts.append(fact)

    def update_fact(self, fact):
        return # Should happen automatically.

    def delete_fact_and_its_cards(self, fact):
        old_cat = fact.cat
        for c in self.cards:
            if c.fact == fact:
                self.cards.remove(c)
        self.facts.remove(fact)
        scheduler().rebuild_queue()
        for cat in old_cat:
            self.remove_category_if_unused(cat)
        log().deleted_card()

    def add_card(self, card):
        self.load_failed = False
        self.cards.append(card)
        log().new_card(card)

    def update_card(self, card):
        return # Should happen automatically.
        
    def cards_from_fact(self, fact):
        return [c for c in self.cards if c.fact == fact]
        
    def has_fact_with_data(self, fact_data):
        for f in self.facts:
            if f.data == fact_data:
                return True
        return False

    def duplicates_for_fact(self, fact):
        duplicates = []
        for f in self.facts:
            if f.card_type == fact.card_type and f != fact:
                for field in fact.card_type.unique_fields:
                    if f[field] == fact[field]:
                        duplicates.append(f)
                        break
        return duplicates

    def category_names(self):
        return (c.name for c in self.categories)

    def card_count(self):
        return len(self.cards)

    def non_memorised_count(self):
        return sum(1 for c in self.cards if (c.grade < 2))

    def scheduled_count(self, days=0):

        """ Number of cards scheduled within 'days' days."""

        days_since_start = self.days_since_start()
        return sum(1 for c in self.cards if (c.grade >= 2) and \
                           (days_since_start >= c.next_rep - days))

    def active_count(self):

        """Number of cards in an active category.  (Remember we don't
        support unactive categories in this database.)

        """

        return len(self.cards)

    def average_easiness(self):
        if len(self.cards) == 0:
            return 2.5
        else:
            return sum(c.easiness for c in self.cards) / len(self.cards)

    def set_filter(self, filter):
        print "SQL filtering not implemented in pickle database."

    # Note that in the SQL version, the following queries should use the
    # filter from above.
    
    def list_to_generator(self, list):
        if list == None:
            raise StopIteration
        for x in list:
            yield x

    def cards_due_for_ret_rep(self, sort_key=""):
        days_since_start = self.start_date.days_since_start()
        cards = [c for c in self.cards if c.grade >= 2 and \
                    days_since_start >= c.next_rep]        
        if sort_key:
            cards.sort(key=lambda c : getattr(c, sort_key))
        return self.list_to_generator(cards)

    def cards_due_for_final_review(self, grade, sort_key=""):
        cards = [c for c in self.cards if c.grade == grade and c.lapses > 0]
        if sort_key:
            cards.sort(key=lambda c : getattr(c, sort_key))
        return self.list_to_generator(cards)
                                      
    def cards_new_memorising(self, grade, sort_key=""):
        cards = [c for c in self.cards if c.grade == grade and c.lapses == 0 \
                    and c.unseen == False]        
        if sort_key:
            cards.sort(key=lambda c : getattr(c, sort_key))
        return self.list_to_generator(cards)
                                      
    def cards_unseen(self, sort_key=""):
        cards = [c for c in self.cards if c.unseen == True]
        if sort_key:
            cards.sort(key=lambda c : getattr(c, sort_key))
        return self.list_to_generator(cards)
                                      
    def cards_learn_ahead(self, sort_key=""):
        days_since_start = self.start_date.days_since_start()
        cards = [c for c in self.cards if c.grade >= 2 and \
                    days_since_start < c.next_rep]        
        if sort_key:
            cards.sort(key=lambda c : getattr(c, sort_key))
        return self.list_to_generator(cards)
                                      
