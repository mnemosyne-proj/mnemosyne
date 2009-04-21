
#
# pickle.py <Peter.Bienstman@UGent.be>
#

import os
import gzip
import cPickle
import datetime
import shutil
import random
import mnemosyne.version

from mnemosyne.libmnemosyne.category import Category
from mnemosyne.libmnemosyne.database import Database
from mnemosyne.libmnemosyne.start_date import StartDate
from mnemosyne.libmnemosyne.utils import expand_path, contract_path
from mnemosyne.libmnemosyne.exceptions import traceback_string
from mnemosyne.libmnemosyne.exceptions import InvalidFormatError
from mnemosyne.libmnemosyne.exceptions import SaveError, LoadError
from mnemosyne.libmnemosyne.exceptions import PluginError, MissingPluginError
from mnemosyne.libmnemosyne.component_manager import component_manager, config
from mnemosyne.libmnemosyne.component_manager import ui_controller_review
from mnemosyne.libmnemosyne.component_manager import ui_controller_main
from mnemosyne.libmnemosyne.component_manager import log, scheduler, plugins
from mnemosyne.libmnemosyne.component_manager import card_types, database
from mnemosyne.libmnemosyne.component_manager import card_type_by_id


class Pickle(Database):

    """A simple storage backend, mainly for testing purposes and to help
    flesh out the design. It has some issues

    * Due to an obscure bug in SIP, we need to replace the card type
    info in fact by a card type id, otherwise we get:

    File "/usr/lib/python2.5/copy_reg.py", line 70, in _reduce_ex
    state = base(self)
    TypeError: the sip.wrapper type cannot be instantiated or sub-classed

    * It is wasteful in memory during queries.

    """

    version = "4"
    suffix = ".p"

    def __init__(self):
        self.start_date = None
        self.categories = []
        self.facts = []
        self.cards = []
        self.global_variables = {"version": self.version}
        self.load_failed = False

    def new(self, path):
        if self.is_loaded():
            self.unload()
        path = expand_path(path, config().basedir)
        self.load_failed = False
        self.start_date = StartDate()
        self.save(contract_path(path, config().basedir))
        config()["path"] = path
        log().new_database()

    def load(self, path):
        if self.is_loaded():
            self.unload()
        path = expand_path(path, config().basedir)
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
            self.global_variables = db[4]
            infile.close()
            self.load_failed = False
        except:
            self.load_failed = True
            raise InvalidFormatError(stack_trace=True)

        # Check database version.
        if self.global_variables["version"] != self.version:
            print "Warning: database version mismatch."
            self.load_failed = True
            raise LoadError
        
        # Deal with clones and plugins, also plugins for parent classes.
        # Because of the sip bugs, card types here are actually still card
        # type ids.
        plugin_needed = set()
        clone_needed = []
        active_id = set(card_type.id for card_type in card_types())
        for id in set(card.fact.card_type for card in self.cards):
            while "." in id: # Move up one level of the hierarchy.
                id, child_name = id.rsplit(".", 1)          
                if id.endswith("_CLONED"):
                    id = id.replace("_CLONED", "")
                    clone_needed.append((id, child_name))
                if id not in active_id:
                    plugin_needed.add(id)
            if id not in active_id:
                plugin_needed.add(id)
        
        # Activate necessary plugins.
        for card_type_id in plugin_needed:
            try:
                for plugin in plugins():
                    if plugin.provides == "card_type" and \
                       plugin.id == card_type_id:
                        plugin.activate()
                        break
                else:
                    self.__init__()
                    self.load_failed = True
                    raise MissingPluginError(info='id')
            except MissingPluginError:
                raise MissingPluginError(info=card_type_id)
            except:
                self.__init__()
                self.load_failed = True
                raise PluginError(stack_trace=True)
            
        # Create necessary clones.
        for parent_type_id, clone_name in clone_needed:
            parent_instance = card_type_by_id(parent_type_id)
            parent_instance.clone(clone_name)
            
        # Work around a sip bug: don't store card types, but their ids.
        for f in self.facts:
            f.card_type = card_type_by_id(f.card_type)    
        # TODO: This was to remove database inconsistencies. Still needed?
        #for c in self.categories:
        #    self.remove_category_if_unused(c)
        config()["path"] = contract_path(path, config().basedir)
        log().loaded_database()
        for f in component_manager.get_all("function_hook", "after_load"):
            f.run()

    def save(self, path=None):
        if not path:
            path = config()["path"]
        path = expand_path(path, config().basedir)
        # Update version.
        self.global_variables["version"] = self.version
        # Work around a sip bug: don't store card types, but their ids.
        for f in self.facts:
            f.card_type = f.card_type.id
        # Don't erase a database which failed to load.
        if self.load_failed == True:
            return -1
        try:
            # Write to a backup file first, as shutting down Windows can
            # interrupt the dump command and corrupt the database.
            outfile = file(path + "~", 'wb')
            db = [self.start_date, self.categories, self.facts, self.cards,
                  self.global_variables]
            cPickle.dump(db, outfile)
            outfile.close()
            shutil.move(path + "~", path) # Should be atomic.
        except:
            print traceback_string()
            raise SaveError
        config()["path"] = contract_path(path, config().basedir)
        # Work around sip bug again.
        for f in self.facts:
            f.card_type = card_type_by_id(f.card_type)

    def unload(self):
        if len(self.facts) == 0:
            return True
        self.save(config()["path"])
        log().saved_database()
        self.start_date = None
        self.categories = []
        self.facts = []
        self.cards = []
        self.global_variables = {"version": self.version}
        scheduler().clear_queue()
        return True

    def backup(self):
        # TODO: implement
        return

        if number_of_items() == 0 or get_config("backups_to_keep") == 0:
            return

        backupdir = os.path.join(basedir, "backups")

        # Export to XML. Create only a single file per day.

        db_name = os.path.basename(config["path"])[:-4]

        filename = db_name + "-" +\
                   datetime.date.today().strftime("%Y%m%d") + ".xml"
        filename = os.path.join(backupdir, filename)

        export_XML(filename, get_category_names(), reset_learning_data=False)

        # Compress the file.

        f = bz2.BZ2File(filename + ".bz2", 'wb', compresslevel=5)
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

    def is_loaded(self):
        return len(self.facts) != 0

    def set_start_date(self, start_date_obj):
        self.start_date = start_date_obj

    def days_since_start(self):
        return self.start_date.days_since_start()
    
    # Adding, modifying and deleting categories, facts and cards.
    
    def add_category(self, category):
        self.categories.append(category)

    def update_category(self, category):
        return # Happens automatically.

    def delete_category(self, category):
        for category_i in self.categories:
            if category_i.id == category.id:
                self.categories.remove(category_i)
                del category_i
                return
            
    # TODO: benchmark this and see if we need a dictionary category_by_name.

    def get_or_create_category_with_name(self, name):
        for category in self.categories:
            if category.name == name:
                return category
        category = Category(name)
        self.categories.append(category)
        return category

    def remove_category_if_unused(self, category):
        for c in self.cards:
            if category in c.categories:
                break
        else:
            self.categories.remove(category)
            del category

    def add_fact(self, fact):
        self.load_failed = False
        self.facts.append(fact)

    def update_fact(self, fact):
        return # Happens automatically.
        
    def add_card(self, card):
        self.load_failed = False
        self.cards.append(card)
        log().new_card(card)

    def update_card(self, card):
        return # Happens automatically.
    
    def delete_fact_and_related_data(self, fact):
        related_cards = [c for c in self.cards if c.fact == fact]
        for c in related_cards:
            self.delete_card(c)
        self.facts.remove(fact)
        current_card = ui_controller_review().card
        if current_card and current_card.fact == fact:
            scheduler().rebuild_queue()
        del fact
            
    def delete_card(self, card):
        old_cat = card.categories
        self.cards.remove(card)
        for cat in old_cat:
            self.remove_category_if_unused(cat)  
        if ui_controller_review().card == card:
            scheduler().rebuild_queue()     
        log().deleted_card(card)
        del card

    # Retrieving categories, facts, cards.

    def get_category(self, id):
        return [c for c in self.categories if c.id == id][0]
    
    def get_fact(self, id):
        return [f for f in self.facts if f.id == id][0]

    def get_card(self, id):
        return [c for c in self.cards if c.id == id][0]
    
    # Activate and set cards in view.

    def set_cards_active(self, card_types_fact_views, categories):
        return self._turn_on_cards("active", card_types_fact_views,
                                   categories)
    
    def set_cards_in_view(self, card_types_fact_views, categories):
        return self._turn_on_cards("in_view", card_types_fact_views,
                                   categories)    
    
    def _turn_on_cards(self, attr, card_types_fact_views, categories):
        # Turn off everything.
        for card in self.cards:
            setattr(card, attr, False)
        # Turn on active categories.                    
        for card in self.cards:        
            if set(card.categories).intersection(set(categories)):
                card.active = True
                setattr(card, attr, True)
        # Turn off inactive card types and views.
        for card in self.cards:
            if (card.fact.card_type, card.fact_view) not in \
              card_types_fact_views:
                setattr(card, attr, False)
        
    # Queries.

    def category_names(self):
        return [c.name for c in self.categories]

    def cards_from_fact(self, fact):
        return [c for c in self.cards if c.fact == fact]
          
    def has_fact_with_data(self, fact_data, card_type):
        for f in self.facts:
            if f.data == fact_data and f.card_type == card_type:
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

    def card_types_in_use(self):
        return set(card.fact.card_type for card in self.cards)
    
    def fact_count(self):
        return len(self.facts)
    
    def card_count(self):
        return len(self.cards)

    def non_memorised_count(self):
        return sum(1 for c in self.cards if c.active and (c.grade < 2))

    def scheduled_count(self, days=0):

        """Number of cards scheduled within 'days' days."""

        days_since_start = self.days_since_start()
        return sum(1 for c in self.cards if c.active and (c.grade >= 2) and \
                           (days_since_start >= c.next_rep - days))

    def active_count(self):
        return len([c for c in self.cards if c.active])

    def average_easiness(self):
        if len(self.cards) == 0:
            return 2.5
        else:
            cards = (c.easiness for c in self.cards if \
                     c.easiness > 0)
            return sum(cards) / len([cards])
            
    def list_to_generator(self, list, sort_key, limit):
        if list == None:
            raise StopIteration
        if sort_key != "random" and sort_key != "":
            list.sort(key=lambda c : getattr(c, sort_key))
        elif sort_key == "random":
            random.shuffle(list)
        if limit >= 0 and len(list) > limit:
            list = list[:limit]
        for x in list:
            yield x

    def cards_due_for_ret_rep(self, sort_key="", limit=-1):
        days_since_start = self.start_date.days_since_start()
        cards = [c for c in self.cards if c.active and c.grade >= 2 and \
                    days_since_start >= c.next_rep]        
        return self.list_to_generator(cards, sort_key, limit)

    def cards_due_for_final_review(self, grade, sort_key="", limit=-1):
        cards = [c for c in self.cards if c.active and c.grade == grade \
                 and c.lapses > 0]
        return self.list_to_generator(cards, sort_key, limit)
                                      
    def cards_new_memorising(self, grade, sort_key="", limit=-1):
        cards = [c for c in self.cards if c.active and c.grade == grade \
                 and c.lapses == 0 \
                    and c.unseen == False]
        return self.list_to_generator(cards, sort_key, limit)
                                      
    def cards_unseen(self, sort_key="", limit=-1):
        cards = [c for c in self.cards if c.active and c.grade < 2 \
                 and c.unseen == True]
        return self.list_to_generator(cards, sort_key, limit)
                                      
    def cards_learn_ahead(self, sort_key="", limit=-1):
        days_since_start = self.start_date.days_since_start()
        cards = [c for c in self.cards if c.active and c.grade >= 2 and \
                    days_since_start < c.next_rep]
        return self.list_to_generator(cards, sort_key, limit)
                                      
