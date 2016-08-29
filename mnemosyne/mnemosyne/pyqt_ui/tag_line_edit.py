#
# tag_line_edit.py: Emilian Mihalache <emihalac@gmail.com>
#

from PyQt5 import QtCore, QtWidgets

class TagLineEdit(QtWidgets.QLineEdit):

    def __init__(self, parent = None):
        super(TagLineEdit, self).__init__(parent)
        # We need to have the popup object created in PyQt so that we can call
        # its protected methods (e.g. passing it the event() call).
        self.completer_popup_ = QtWidgets.QListView()
        self.last_highlighted_text_ = ""

    def setupCompleter(self):
        self.completer().setCompletionMode(\
            QtWidgets.QCompleter.PopupCompletion)
        # We need to store a Python reference to the popup object, otherwise
        # it will get destroyed and re-built as a Qt object (as opposed to 
        # a PyQt one), which would make its protected methods inaccessible 
        # again.
        self.completer().setPopup(self.completer_popup_)
        # Leaving the popup object to handle KeyUp/KeyDown events on its own 
        # makes it override the entire text of the QComboBox, deleting all 
        # previously-entered tags. We need to chase after it with a stick 
        # and make it give our tags back.
        self.completer().popup().installEventFilter(self)
        self.completer().highlighted[str].connect(self.handleHighlight)

    def keyPressEvent(self, key_event):
        super(TagLineEdit, self).keyPressEvent(key_event)
        completer = self.completer()
        if completer is None:
            print("Null completer object!")
            return
        completer.setCompletionPrefix(self.lastTagPrefix())
        if len(completer.completionPrefix()) < 1:
            completer.popup().hide()
            return
        cursor_rect_width = completer.popup().sizeHintForColumn(0) + \
                completer.popup().verticalScrollBar().sizeHint().width()
        cr = self.cursorRect()
        cr.setWidth(cursor_rect_width)
        completer.complete(cr)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            event_key = event.key()
            if event_key == QtCore.Qt.Key_Up or \
               event_key == QtCore.Qt.Key_Down:
                old_text = self.text()
                # Handing the event to the popup object results in strange
                # behavior where sometimes the QComboBox text is changed 
                # even though selection has not been confirmed.
                obj.event(event)
                # ... which is why we have to restore it.
                self.setText(old_text)
                return True
            elif event_key == QtCore.Qt.Key_Return or \
                 event_key == QtCore.Qt.Key_Enter:
                obj.hide()
                self.insertCompletion(self.last_highlighted_text_)
                return True
        return False

    def handleHighlight(self, highlightedText):
        self.last_highlighted_text_ = highlightedText

    def insertCompletion(self, completion):
        full_text = self.text()
        cursor_position = self.cursorPosition()
        last_relevant_comma_index = full_text[0:cursor_position].rfind(",")
        replaced_text = full_text[:last_relevant_comma_index] + completion + full_text[cursor_position:]
        print("----")
        print(full_text)
        print(completion)
        print(replaced_text)
        self.setText(replaced_text)

    def lastTagPrefix(self):
        full_text = self.text()
        cursor_position = self.cursorPosition()
        last_relevant_comma_index = full_text[0:cursor_position].rfind(",")
        return full_text[last_relevant_comma_index + 1:cursor_position].strip()
    
    