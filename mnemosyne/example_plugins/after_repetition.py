#
# after_repetition.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.hook import Hook
from mnemosyne.libmnemosyne.plugin import Plugin


class Grade5DetectionHook(Hook):

    used_for = "after_repetition"

    def run(self, card):
        if card.grade == 5:
            self.main_widget().show_information("This was an easy card!")


class AfterRepetitionPlugin(Plugin):
    
    name = "Grade 5 detection"
    description = "Notice when a card is given grade 5."   
    components = [Grade5DetectionHook]
    supported_API_level = 3
    

# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(AfterRepetitionPlugin)

