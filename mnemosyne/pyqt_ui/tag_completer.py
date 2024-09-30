from PyQt6 import QtCore, QtWidgets, QtGui

class TagCompleter(QtWidgets.QCompleter):
    def __init__(self, parent = None):
        super(TagCompleter, self).__init__(parent)
        self.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)

    def handle_prefix_change(self, new_prefix):
        if new_prefix:
            self.setCompletionPrefix(new_prefix)
            self.complete()

    def refresh_completion_model(self, new_model):
        """Sets the completion model that the completer will use.

        Ideally, we'd be able to just set the completion model once and then
        forget about it. However, this would result in unwanted behavior
        wherein word prefixes are added to the completion list by Qt.

        Example: user types in 'myf' and then selects the pop-up completion
        of 'myfancytag'. This results in 'myf' getting added as a potential
        completion suggestion, which is obviously wrong (... and infuriating
        to debug).

        That's why we only update the model: (1) at the start, with all
        available tags, and (2) when the user actually creates a new tag.
        """
        initial_tag_model_ = QtGui.QStandardItemModel()
        for index in range(0, new_model.rowCount()):
            initial_tag_model_.appendRow(new_model.item(index).clone())
        self.setModel(initial_tag_model_)
