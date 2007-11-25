##############################################################################
#
# Tip of the day dialog <Peter.Bienstman@UGent.be>
#
##############################################################################

from qt import *
from tip_frm import *
from mnemosyne.core import *


##############################################################################
#
# TipDlg
#
##############################################################################

class TipDlg(TipFrm):
    
    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, parent=None, name=None, modal=0, fl=0):
        
        TipFrm.__init__(self,parent,name,modal,fl)

        self.show_tips.setChecked(get_config("show_daily_tips"))
        
        self.tips = []

        self.tips.append(self.trUtf8("For optimal results, it's best to do your repetitions every day."""))

        self.tips.append(self.trUtf8("""If you've been away for a few days, don't worry about your backlog. Do as many cards as you feel like to catch up, the rest will be automatically rescheduled to the future."""))

        self.tips.append(self.trUtf8("""The 'number of grade 0 cards to learn at once' setting determines how many new cards you are trying to learn at the same time. It does <b>not</b> tell you how many new cards you need to learn per day. You are the judge of that: you can learn more cards or less cards, depending on how you feel."""))

        self.tips.append(self.trUtf8("""In summary, try to do your repetitions every day, but don't worry too much about getting the 'scheduled' counter to zero, and certainly not about getting the 'Not memorised' counter to zero."""))

        self.tips.append(self.trUtf8("""Grade 1 cards are different from grade 0 cards in the sense that they show up less often and are not subject to the 'number of grade 0 cards to learn at once' setting."""))

        self.tips.append(self.trUtf8("""You can use keyboard shortcuts to do your repetitions. Enter, Return or Space stand for the default action ('Show answer' or 'grade 4'). The number keys can be used for grading."""))

        self.tips.append(self.trUtf8("""You can select the categories you wish to study in the 'Activate categories' menu option."""))

        self.tips.append(self.trUtf8("""It is recommended to put all your cards in a single database and use categories to organise them. Using 'Activate categories' is much more convenient than have to load and unload several databases."""))

        self.tips.append(self.trUtf8("""You can import cards in a wide variety of formats: tab delimited txt files, Supermemo files, ... ."""))

        self.tips.append(self.trUtf8("""If you have cards in Word or Excel, export them to tab delimited txt files with UTF-8 unicode encoding to be able to import them into Mnemosyne."""))

        self.tips.append(self.trUtf8("""If you want to print out your cards, export them to a txt file which you can then print from your favourite Word processor."""))

        self.tips.append(self.trUtf8("""You can share your cards with someone else by exporting them to XML and choosing the 'Reset learning data' option on export."""))

        self.tips.append(self.trUtf8("""If you study a foreign language with a different script, the default font size is sometimes a bit small. If you want to increase the size of these characters but keep the size of English text, use the 'increase size of non-latin characters by X points' option."""))

        self.tips.append(self.trUtf8("""You can add images and sounds to your cards. Right-click on the question or answer field when editing a card to bring up a pop-up menu to do so."""))

        self.tips.append(self.trUtf8("""It is recommended to keep your sound and image files inside your .mnemosyne directory. That way, it's easier to transfer your data between different computers."""))

        self.tips.append(self.trUtf8("""When adding a three-sided card, two regular cards will be created. One with as question the written form and as answer the pronunciation and the translation, and one with as question the translation and as answer the written form and the pronunciation."""))

        self.tips.append(self.trUtf8("""You can use basic HTML tags in your cards to control their appearance."""))

        self.tips.append(self.trUtf8("""Mnemosyne can use LaTeX to render mathematical formulas, e.g. <$>x^2+y^2=z^2</$>. (For this, you need LaTeX and dvipng installed.)"""))

        self.tips.append(self.trUtf8("""The best way to backup your data is to copy your .mnemosyne directory (if you follow the recommended procedure to keep all your files there) and move it to a different drive. Mnemosyne keeps automatic XML-based backups in .mnemosyne/backups, but that won't help you if that drive dies... """))

        self.tips.append(self.trUtf8("""You can run Mnemosyne from a USB key. Copy C:\\Program Files\\Mnemosyne to your USB key, and then copy the .mnemosyne directory from your home directory to inside the Mnemosyne directory on the USB key."""))

        self.tips.append(self.trUtf8("""If you use Mnemosyne on multiple computers, there is a handy tool called Unison to help you synchronise your data. See the Mnemosyne website for more information."""))

        self.tips.append(self.trUtf8("""You can sort the cards in the 'Edit Deck' dialog by answer or by category by clicking on the corresponding column title. Clicking again changes the sort order."""))

        self.tips.append(self.trUtf8("""If you want more fine-grained control over LaTeX's behaviour, see the explanation of the <$$>...</$$> and <latex>...</latex> tags on Mnemosyne's website."""))

        self.tips.append(self.trUtf8("""Advanced users can customise more of Mnemosyne by editing the config.py file in their .mnemosyne directory. They can also install plugins to customise Mnemosyne even further."""))

        self.update_dialog()
        
    ##########################################################################
    #
    # update_dialog
    #
    ##########################################################################
    
    def update_dialog(self):
        
        tip = get_config("tip")
        self.tip_label.setText(self.tips[tip])
        self.previous_button.setEnabled(tip != 0)
        self.next_button.setEnabled(tip != len(self.tips)-1)
        
    ##########################################################################
    #
    # previous
    #
    ##########################################################################
    
    def previous(self):
        
        set_config("tip", (get_config("tip")-1) % len(self.tips))
        self.update_dialog()

    ##########################################################################
    #
    # next
    #
    ##########################################################################
    
    def next(self):
        
        set_config("tip", (get_config("tip")+1) % len(self.tips))
        self.update_dialog()

    ##########################################################################
    #
    # closeEvent
    #
    ##########################################################################

    def closeEvent(self, event):
        
        set_config("show_daily_tips",self.show_tips.isOn())
        set_config("tip", (get_config("tip")+1) % len(self.tips))
        event.accept()
