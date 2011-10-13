#
# file_format.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component


class FileFormat(Component):

    component_type = "file_format"
    description = ""
    filename_filter = ""  # E.g. "XML Files (*.xml *XML)"
    import_possible = False
    export_possible = False

    def retranslate(self):
        self.description = _(self.description)
        self.filename_filter = _(self.filename_filter)
    
    def do_import(self, filename, extra_tag_name=None):
        raise NotImplementedError

    def do_export(self, filename, extra_tag_name=None):
        raise NotImplementedError    

