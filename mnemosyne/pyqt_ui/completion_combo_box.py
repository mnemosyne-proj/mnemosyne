#
# completion_combo_box.py: Emilian Mihalache <emihalac@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets
from mnemosyne.pyqt_ui.tag_line_edit import TagLineEdit


class CompletionComboBox(QtWidgets.QComboBox):

    def __init__(self, parent=None):
        super(CompletionComboBox, self).__init__(parent)

        tag_line_edit_ = TagLineEdit(self)
        self.setLineEdit(tag_line_edit_)

        # Disable builtin autocompletion.
        # We'll be replacing it with an autocompletion mechanism
        #  that can work with elements after the first one.
        #
        # This _needs_ to be called _after_ setLineEdit(),
        #  because setLineEdit() will create&store a new QCompleter,
        #  which we're deleting here.
        self.setCompleter(None)

    def refresh_completion_model(self):
        self.lineEdit().refresh_completion_model(self.model())
