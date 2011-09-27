#
# file_format.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class FileFormat(Component):

    component_type = "file_format"
    description = ""
    filename_filter = ""  # E.g. "XML Files (*.xml *XML)"
    import_possible = False
    export_possible = False
    
    def do_import(self, filename, tag_name=None, reset_learning_data=False):
        raise NotImplementedError

    def do_export(self, filename, tag_name=None, reset_learning_data=False):
        raise NotImplementedError    

