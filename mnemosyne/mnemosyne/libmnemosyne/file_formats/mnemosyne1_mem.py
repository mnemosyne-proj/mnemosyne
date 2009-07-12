#
# mnemosyne1_mem.py <Peter.Bienstman@UGent.be>
#

import sys
import pickle

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.file_format import FileFormat


class Mnemosyne1Mem(FileFormat):
    
    description = _("Mnemosyne 1.x *.mem files")
    filename_filter = _("Mnemosyne 1.x databases") + " (*.mem)"
    import_possible = True
    export_possible = False
    
    def do_import(self, filename, tag_name=None, reset_learning_data=False):
        # Mimick 1.x module structure.
        class MnemosyneCore(object):                          
            class StartTime:                                    
                pass                                            
            class Category:                                     
                pass                                            
            class Item:                                         
                pass
        sys.modules["mnemosyne.core"] = object()       
        sys.modules["mnemosyne.core.mnemosyne_core"] = MnemosyneCore()
        # Load data.
        try:                                                    
            memfile = file(filename, "rb")
            header = memfile.readline()
            start_time, categories, items = pickle.load(memfile)
        except:
            self.main_widget().error_box(_("Unable to open file."))
        # Convert to 2.x data structures.

        from PyQt4 import QtCore, QtGui
        progress = QtGui.QProgressDialog(_("Importing cards..."), "",
                                       0, len(items), self.main_widget())
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setCancelButton(None)

        count = 0
        for item in items:
            progress.setValue(count)
            
            # Front-to-back cards.
            card_type = self.card_type_by_id("1")
            fact_data = {"q": item.q, "a": item.a}
            self.controller().create_new_cards(fact_data, card_type, grade=-1,
                                               tag_names="<default>")
            count += 1
            progress.setValue(count)

