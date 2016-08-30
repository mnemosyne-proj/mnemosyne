#
# completion_combo_box.py: Emilian Mihalache <emihalac@gmail.com>
#

from PyQt5 import QtCore, QtWidgets
from mnemosyne.pyqt_ui.tag_line_edit import TagLineEdit


class CompletionComboBox(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        super(CompletionComboBox, self).__init__(parent)
        tag_line_edit = TagLineEdit(self)

        # This performs QComboBox-internal setup of QCompleter object
        # on the QLineEdit object...
        self.setLineEdit(tag_line_edit)

        # ... which we have to wait for before doing our own
        # operations on that same QCompleter.
        tag_line_edit.setupCompleter()