#
# file_format.py <Peter.Bienstman@gmail.com>
#

import os

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.component import Component


class FileFormat(Component):

    component_type = "file_format"
    description = ""
    extension = "" # E.g. ".xml"
    filename_filter = ""  # E.g. "XML Files (*.xml *XML)"
    import_possible = False
    export_possible = False

    def do_import(self, filename, extra_tag_name=None):

        """Make sure fileformats call this implementation first."""

        self.import_dir = os.path.dirname(os.path.abspath(filename))

