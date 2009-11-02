
#
# pickle.py <Peter.Bienstman@UGent.be>
#

import os
import shutil
import random
import cPickle
import mnemosyne.version

from mnemosyne.libmnemosyne.tag import Tag
from mnemosyne.libmnemosyne.database import Database
from mnemosyne.libmnemosyne.utils import traceback_string
from mnemosyne.libmnemosyne.utils import expand_path, contract_path
from mnemosyne.libmnemosyne.translator import _


class Pickle(Database):

    """A simple storage backend, mainly for testing purposes and to help
    flesh out the design. It has some issues:

    * Due to an obscure bug in SIP, we need to replace the card type
    info in fact by a card type id, otherwise we get:

    File "/usr/lib/python2.5/copy_reg.py", line 70, in _reduce_ex
    state = base(self)
    TypeError: the sip.wrapper type cannot be instantiated or sub-classed

    * It is wasteful in memory during queries.
    
    Also, it does not have all the features of the SQL database. Notably,
    it is missing activity criteria, review history, and the handling
    of media files and card types.
    
    """

    version = "4"
    suffix = ".p"

    def __init__(self, component_manager):
        Database.__init__(self, component_manager)
        self.tags = []
        self.facts = []
        self.cards = []
        self.global_variables = {"version": self.version}
        self.load_failed = False
        
    def database_name(self):
        if not self.is_loaded():
            return None
        else:
            return os.path.basename(self.config()["path"]).\
                   split(self.database().suffix)[0]
        
    def new(self, path):
        if self.is_loaded():
            self.unload()
        path = expand_path(path, self.config().basedir)
        self.load_failed = False
        self.save(contract_path(path, self.config().basedir))
        self.config()["path"] = contract_path(path, self.config().basedir)
        self.log().new_database()
        
    def load(self, path):
        if self.is_loaded():
            self.unload()
        path = expand_path(path, self.config().basedir)
        if not os.path.exists(path):
            self.load_failed = True
            raise RuntimeError, _("File does not exist.")
        try:
            infile = file(path, 'rb')
            db = cPickle.load(infile)
            self.tags = db[0]
            self.facts = db[1]
            self.cards = db[2]
            self.global_variables = db[3]
            infile.close()
            self.load_failed = False
        except:
            self.load_failed = True
            raise RuntimeError, _("Invalid file format.") \
                  + "\n" + traceback_string()

        # Check database version.
        if self.global_variables["version"] != self.version:
            self.load_failed = True
            raise RuntimeError, _("Unable to load file: database version mismatch.")
        
        # Deal with clones and plugins, also plugins for parent classes.
        # Because of the sip bugs, card types here are actually still card
        # type ids.
        plugin_needed = set()
        clone_needed = []
        active_id = set(card_type.id for card_type in self.card_types())
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
            found = False
            for plugin in self.plugins():
                for component in plugin.components:
                    if component.component_type == "card_type" and \
                           component.id == card_type_id:
                        found = True
                        try:
                            plugin.activate()
                        except:
                            self.load_failed = True
                            raise RuntimeError, \
                                  _("Error when running plugin:") \
                                  + "\n" + traceback_string()
            if not found:
                self.load_failed = True
                raise RuntimeError, \
                      _("Missing plugin for card type with id:") \
                      + " " + card_type_id
            
        # Create necessary clones.
        for parent_type_id, clone_name in clone_needed:
            parent_instance = self.card_type_by_id(parent_type_id)
            try:
                parent_instance.clone(clone_name)
            except NameError:
                # In this case the clone was already created by loading the
                # database earlier.
                pass
            
        # Work around a sip bug: don't store card types, but their ids.
        for f in self.facts:
            f.card_type = self.card_type_by_id(f.card_type)    
        self.config()["path"] = contract_path(path, self.config().basedir)
        for f in self.component_manager.get_all("hook", "after_load"):
            f.run()
        # We don't log the database load here, as we prefer to log the start
        # of the program first.
        
    def save(self, path=None):
        # Don't erase a database which failed to load.
        if self.load_failed == True:
            return -1
        if not path:
            path = self.config()["path"]
        path = expand_path(path, self.config().basedir)
        # Update version.
        self.global_variables["version"] = self.version
        # Work around a sip bug: don't store card types, but their ids.
        for f in self.facts:
            f.card_type = f.card_type.id
        try:
            # Write to a backup file first, as shutting down Windows can
            # interrupt the dump command and corrupt the database.
            outfile = file(path + "~", 'wb')
            db = [self.tags, self.facts, self.cards,
                  self.global_variables]
            cPickle.dump(db, outfile)
            outfile.close()
            shutil.move(path + "~", path) # Should be atomic.
        except:
            raise RuntimeError, _("Unable to save file.") \
                  + "\n" + traceback_string()
        self.config()["path"] = contract_path(path, self.config().basedir)
        # Work around sip bug again.
        for f in self.facts:
            f.card_type = self.card_type_by_id(f.card_type)
        # We don't log every save, as that would result in an event after
        # every review.

    def unload(self):
        for f in self.component_manager.get_all("hook", "before_unload"):
            f.run()
        self.backup()
        self.log().dump_to_txt_log()
        if len(self.facts) == 0:
            return True
        self.save(self.config()["path"])
        self.tags = []
        self.facts = []
        self.cards = []
        self.global_variables = {"version": self.version}
        return True
    
    def abandon(self):
        self.tags = []
        self.facts = []
        self.cards = []
        self.global_variables = {"version": self.version}
    
    def backup(self):
        print "Backup not implemented"
        
    def is_loaded(self):
        return len(self.facts) != 0
    
    # Tags.
    
    def add_tag(self, tag):
        tag._id = tag.id
        self.tags.append(tag)
        
    def get_tag(self, id, id_is_internal):
        return [c for c in self.tags if c.id == id][0]
    
    def update_tag(self, tag):
        return # Happens automatically.

    def delete_tag(self, tag):
        for tag_i in self.tags:
            if tag_i.id == tag.id:
                self.tags.remove(tag_i)
                del tag_i
                return

    def get_or_create_tag_with_name(self, name):
        for tag in self.tags:
            if tag.name == name:
                return tag
        tag = Tag(name)
        self.tags.append(tag)
        return tag

    def remove_tag_if_unused(self, tag):
        for c in self.cards:
            if tag in c.tags:
                break
        else:
            self.tags.remove(tag)
            del tag

    # Facts.
    
    def add_fact(self, fact):
        fact._id = fact.id
        self.load_failed = False
        self.facts.append(fact)
    
    def get_fact(self, id, id_is_internal):
        return [f for f in self.facts if f.id == id][0]
    
    def update_fact(self, fact):
        return # Happens automatically.

    def delete_fact_and_related_data(self, fact):
        related_cards = [c for c in self.cards if c.fact == fact]
        for c in related_cards:
            self.delete_card(c)
        self.facts.remove(fact)
        del fact

    # Cards.
        
    def add_card(self, card):
        card._id = card.id
        self.load_failed = False
        self.cards.append(card)

    def get_card(self, id, id_is_internal):
        return [c for c in self.cards if c.id == id][0]
    
    def update_card(self, card, repetition_only=False):
        return # Happens automatically.
            
    def delete_card(self, card):
        old_cat = card.tags
        self.cards.remove(card)
        for cat in old_cat:
            self.remove_tag_if_unused(cat)    
        self.log().deleted_card(card)
        del card
        
    # Queries.

    def tag_names(self):
        return [c.name for c in self.tags]

    def cards_from_fact(self, fact):
        return [c for c in self.cards if c.fact == fact]

    def count_related_cards_with_next_rep(self, card, next_rep):
        return len([c for c in self.cards if c.fact == card.fact and \
            c != card and c.next_rep == next_rep and c.grade >= 2])

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

    def scheduled_count(self, timestamp):
        return sum(1 for c in self.cards if c.active and (c.grade >= 2) and \
                           (timestamp >= c.next_rep))

    def active_count(self):
        return len([c for c in self.cards if c.active])

    # Card queries used by the scheduler.
    
    def _list_to_generator(self, list, sort_key, limit):
        if list == None:
            raise StopIteration
        if sort_key != "random" and sort_key != "":
            list.sort(key=lambda c : getattr(c, sort_key))
        elif sort_key == "random":
            random.shuffle(list)
        if limit >= 0 and len(list) > limit:
            list = list[:limit]
        for c in list:
            yield (c.id, c.fact.id)

    def cards_due_for_ret_rep(self, timestamp, sort_key="", limit=-1):
        cards = [c for c in self.cards if c.active and \
                 c.grade >= 2 and timestamp >= c.next_rep]        
        return self._list_to_generator(cards, sort_key, limit)

    def cards_due_for_final_review(self, grade, sort_key="", limit=-1):
        cards = [c for c in self.cards if c.active and \
                 c.grade == grade and c.lapses > 0]
        return self._list_to_generator(cards, sort_key, limit)
                                      
    def cards_new_memorising(self, grade, sort_key="", limit=-1):
        cards = [c for c in self.cards if c.active and \
                 c.grade == grade and c.lapses == 0]
        return self._list_to_generator(cards, sort_key, limit)
                                      
    def cards_unseen(self, sort_key="", limit=-1):
        cards = [c for c in self.cards if c.active and c.grade == -1]
        return self._list_to_generator(cards, sort_key, limit)
                                      
    def cards_learn_ahead(self, timestamp, sort_key="", limit=-1):
        cards = [c for c in self.cards if c.active and \
                 c.grade >= 2 and timestamp < c.next_rep]
        return self._list_to_generator(cards, sort_key, limit)

    # Extra commands for custom schedulers.

    def set_scheduler_data(self, scheduler_data):
        for card in self.cards:
            card.scheduler_data = scheduler_data

    def cards_with_scheduler_data(self, scheduler_data, sort_key="", limit=-1):
        cards = [c for c in self.cards if c.active and \
                 c.scheduler_data == scheduler_data]
        return self._list_to_generator(cards, sort_key, limit)

    def scheduler_data_count(self, scheduler_data):
        return len([c for c in self.cards if c.active
                    and c.scheduler_data == scheduler_data])    
        
