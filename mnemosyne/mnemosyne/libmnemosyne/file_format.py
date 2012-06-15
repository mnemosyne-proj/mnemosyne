#
# file_format.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component


class FileFormat(Component):

    component_type = "file_format"
    description = ""
    filename_filter = ""  # E.g. "XML Files (*.xml *XML)"
    import_possible = False
    export_possible = False

    def do_import(self, filename, extra_tag_name=None):

        """Make sure fileformats call this implementation first."""

        self.import_dir = os.path.dirname(os.path.abspath(filename))

    def do_export(self, filename, extra_tag_name=None):
        raise NotImplementedError

