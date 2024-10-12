#
# tip_dlg.py <Johannes.Baiter@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.pyqt_ui.ui_tip_dlg import Ui_TipDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import TipDialog


class TipDlg(QtWidgets.QDialog, TipDialog, Ui_TipDlg):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.tips = []
        self.tips.append(_("""For optimal results, it's best to do your repetitions every day."""))
        self.tips.append(_("""You don't need to finish all your daily scheduled repetitions in a single session."""))
        self.tips.append(_("""If you've been away for a few days, don't worry about your backlog. Do as many cards as you feel like to catch up, the rest will be automatically rescheduled to the future in the most optimal way."""))
        self.tips.append(_("""Sister cards are cards which are based on the same information, e.g. a front-to-back card and the corresponding back-to-front card. Mnemosyne will avoid scheduling these on the same day."""))
        self.tips.append(_("""The 'Work on at most X non-memorised cards at the same time' setting determines how many cards you are trying to (re)learn at the same time. It does <b>not</b> tell you how many new cards you need to learn per day. You are the judge of that: you can learn more cards or less cards, depending on how you feel."""))
        self.tips.append(_("""In summary, try to do your repetitions every day, but don't worry too much about getting the 'Scheduled' counter to zero, and certainly not about getting the 'Not memorised' counter to zero."""))
        self.tips.append(_("""Grade 1 cards are different from grade 0 cards in the sense that they show up less often."""))
        self.tips.append(_("""Use 'Learn ahead of schedule' sparingly. For cramming before an exam, it's much better to use the cramming scheduler plugin."""))
        self.tips.append(_("""You can use keyboard shortcuts to do your repetitions. Enter, Return or Space stand for the default action. The number keys can be used for grading."""))
        self.tips.append(_("""You can select which cards you wish to study in the '(De)activate cards' menu option."""))
        self.tips.append(_("""It is recommended to put all your cards in a single database and use tag to organise them. Using '(De)activate cards' is much more convenient than having to load and unload several databases."""))
        self.tips.append(_("""You can add multiple tags to a card by separating tags with a comma in the 'Tag(s)' input field."""))
        self.tips.append(_("""You can organise tags in a hierarchy by using :: as separator, e.g. My book::Lesson 1."""))
        self.tips.append(_("""You can add images and sounds to your cards. Right-click on an input field when editing a card to bring up a pop-up menu to do so."""))
        self.tips.append(_("""You can make clones of existing card types. This allows you to format cards in this type independently from cards in the original type. E.g. you can make a clone of 'Vocabulary', call it 'Thai' and set a Thai font specifically for this card type without disturbing your other cards."""))
        self.tips.append(_("""If for a certain card type cloned from Vocabulary you don't need a pronunciation field, you can hide it by right-clicking on it and using the pop-up menu."""))
        self.tips.append(_("""You can use basic HTML tags in your cards to control their appearance. However, if you want all the fields in a certain card type to look the same, it's easier to use the 'Set card appearance' menu option."""))
        self.tips.append(_("""Using 'File - Sync', you can sync this machine with a remote server. Of course, that remote computer needs to have a server running, which can be started from the configuration screen on that remote machine."""))
        self.tips.append(_(""" If you want to sync a mobile device with this computer, don't use 'File - Sync', but first enable a sync server in the configuration dialog, and then start the sync from the mobile device."""))
        self.tips.append(_("""In the 'Activate cards' dialog, you can right-click on a saved set to rename or delete it."""))
        self.tips.append(_("""In the 'Activate cards' dialog, you can double-click on a saved set to activate it and close the dialog."""))
        self.tips.append(_("""Right-click on a tag name in the card browser to edit or delete it."""))
        self.tips.append(_("""Double-click on a card or tag name in the card browser to edit them."""))
        self.tips.append(_("""You can reorder columns in the card browser by dragging the header label."""))
        self.tips.append(_("""You can resize columns in the card browser by dragging between the header labels."""))
        self.tips.append(_("""In the card browser, cards with strike-through text are inactive in the current set."""))
        self.tips.append(_("""When editing or previewing cards from the card browser, PageUp/PageDown can be used to move to the previous/next card."""))
        self.tips.append(_("""In the search box of the card browser, you can use SQL wildcards like _ (matching a single character) and % (matching one or more characters)."""))
        self.tips.append(_("""In the 'Add cards' dialog, use Tab to move between different fields, Ctrl+Enter for 'Yet to learn', and Ctrl+2, etc. for the grades."""))
        self.tips.append(_("""In the 'Edit card' dialog, use Tab to move between different fields and Ctrl+Enter to close the dialog and accept the changes."""))
        self.tips.append(_("""Double-click on the name of a saved set in '(De)activate cards' to quickly activate it and close the dialog."""))
        self.tips.append(_("""If you single-click the name of a saved set in '(De)activate cards', modifications to the selected tags and card types are not saved to that set unless you press 'Save this set for later use' again. This allows you to make some quick-and-dirty temporary modifications."""))
        self.tips.append(_("""Mnemosyne can use LaTeX to render mathematical formulas, e.g. <$>x^2+y^2=z^2</$>. (For this, you need LaTeX and dvipng installed.)"""))
        self.tips.append(_("""The best way to backup your data is to copy your mnemosyne data directory and move it to a different drive. Mnemosyne keeps automatic backups, but that won't help you if that drive dies..."""))
        self.tips.append(_("""You can sort the cards in the 'Browse cards' dialog by by clicking on a column title. Clicking again changes the sort order."""))
        self.tips.append(_("""If you want more fine-grained control over LaTeX's behaviour, see the explanation of the <$$>...</$$> and <latex>...</latex> tags on Mnemosyne's website."""))
        self.tips.append(_("""For optimal performance, keep your drives defragmented."""))
        self.tips.append(_("""For optimal performance, do not put your database on a network drive."""))
        self.tips.append(_("""For optimal performance, run 'File - Compact' from time to time, especially after deleting many cards."""))
        self.tips.append(_("""Advanced users can customise more of Mnemosyne by editing the config.py file in their mnemosyne directory. They can also install additional plugins to customise Mnemosyne even further."""))
        self.tips.append(_("""You can follow the development of Mnemosyne on Twitter or Facebook."""))
        self.tips.append(_("""You can request new features and vote for exisiting requests at <a href="https://mnemosyne.uservoice.com/">uservoice</a>. This helps the developers decide what to work on next."""))
        self.tips.append(_("""Using the 'Manage card types' dialog, you can associate a language with a card type. This enables functionality like text-to-speech or dictionary lookup."""))
        self.tips.append(_("""If you've been using Mnemosyne for a long time, and your daily workload becomes too much, consider using the option to stop showing cards after they reach a number of successful repetitions."""))

        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        if self.config()["show_daily_tips"] == True:
            self.show_tips.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self.show_tips.setCheckState(QtCore.Qt.CheckState.Unchecked)
        # Note: the svg file does not seem to work under windows.
        #watermark = QtGui.QPixmap("pixmaps/mnemosyne.svg").\
        #    scaledToHeight(200, QtCore.Qt.TransformationMode.SmoothTransformation)
        watermark = QtGui.QPixmap("icons:mnemosyne.png")
        self.watermark.setPixmap(watermark)
        self.update_dialog()

    def activate(self):
        TipDialog.activate(self)
        self.exec()

    def update_dialog(self):
        # We need an extra modulo operation here to deal with the possibility
        # of decreasing the number of tips during upgrade.
        tip = self.config()["current_tip"] % len(self.tips)
        self.tip_label.setText(self.tips[tip])
        self.previous_button.setEnabled(tip != 0)
        self.next_button.setEnabled(tip != len(self.tips) - 1)

    def previous(self):
        self.config()["current_tip"] = \
            (self.config()["current_tip"] - 1) % len(self.tips)
        self.update_dialog()

    def next(self):
        self.config()["current_tip"] = \
            (self.config()["current_tip"] + 1) % len(self.tips)
        self.update_dialog()

    def reject(self):
        self.close()

    def closeEvent(self, event):
        self.config()["show_daily_tips"] = self.show_tips.isChecked()
        self.config()["current_tip"] = \
            (self.config()["current_tip"] + 1) % len(self.tips)
        event.accept()
