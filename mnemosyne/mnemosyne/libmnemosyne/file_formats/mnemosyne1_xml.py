from datetime import datetime
from xml.etree import cElementTree

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.file_formats.mnemosyne1x import MnemosyneCore
from mnemosyne.libmnemosyne.file_format import FileFormat
#from mnemosyne.libmnemosyne.file_formats.mnemosyne1_mem import

#TODO: This filter will share a lot of common code with the Mnemosyne1Mem
#      filter. Ideally we should try to put all of that code into an own
#      "_mnemosyne1_cards.py" module that both Mem- and XML-Filter will import
#      from. 
#   Question: Do we need to care about science logs?
#   Candidate functions/classes:
#       - do_import
#       - _import_mem_file (everything after the data is loaded)
#       - MnemosyneCore [+ dummy packages]
#       - _create_card_from_item
#            We would need to create an item-datastructure from the XML
#            first, but this should be worth the effort to avoid code-
#            duplication
#   Outline:
#       - Parse mnemosyne version and start_time
#       - Parse list of items from XML-file
#       - run _create_card_from_item on each item

class Mnemosyne1XML(FileFormat):

    description = _("Mnemosyne 1.x *.xml files")
    filename_filter = _("Mnemosyne 1.x XML files") + " (*.xml)"
    import_possible = True
    export_possible = False

    def do_import(self, filename, tag_name=None, reset_learning_data=False):
        #TODO: This is probably the same as with Mem-files, so we should
        #      probably refactor this into a single method
        pass

    def _import_xml_file(self, filename, tag_name=None,
                         reseat_learning_data=False):

        tree = cElementTree.parse(filename)
        if tree.getroot().get('core_version') != '1':
            raise Exception(_("Bad file version: Needs to be an Mnemosyne 1.x XML file."))

        starttime = MnemosyneCore.StartTime()
        starttime.time = datetime.fromtimestamp(
            tree.getroot().get('time_of_start'))

        catdict = {}
        categories = []
        for element in tree.findall('category'):
            category = MnemosyneCore.Category()
            category.name = element.find('name').text
            category.active = bool(element.get('active'))
            categories.append(category)
            catdict[category.name] = category

        items = []
        for element in tree.findall('item'):
            item = MnemosyneCore.Item()
            item.id = element.get('id') 
            item.q = element.find('Q').text
            item.a = element.find('A').text
            item.cat = catdict[element.find('cat').text]
            item.grade = int(element.get('gr'))
            item.easiness = float(element.get('e'))
            item.acq_reps = int(element.get('ac_rp'))
            item.ret_reps = int(element.get('rt_rp'))
            item.lapses = int(element.get('lps'))
            item.acq_reps_since_lapse = int(element.get('ac_rp_l'))
            item.ret_reps_since_lapse = int(element.get('rt_rp_l'))
            item.last_rep = int(element.get('l_rp'))
            # This is how 1.x reads it, but why can next_rep be float
            # while last_rep can safely be parsed as an int?
            item.next_rep = int(float(element.get('n_rp')))

            if element.get('u'):
                item.unseen = bool(element.get('u'))
            else:
                if item.acq_reps <= 1 and item.ret_reps == 0\
                        and item.grade == 0:
                    item.unseen = True
                else:
                    item.unseen = False

            items.append(item)
        return starttime, categories, items

            

        pass


