#
# pronouncer.py <Peter.Bienstman@UGent.be>
#

import os
import datetime

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import make_filename_unique
from mnemosyne.libmnemosyne.utils import expand_path, contract_path


class Pronouncer(Component):

    """Generic text-to-speech service for words and sentences.

    A single component can handle multiple languages (e.g. Google TTS)
    and the language to be used can be determined through the language_id
    property of the card_type argument.

    A Pronouncer should register the languages it can handle in its __init__
    function.

    """

    component_type = "pronouncer"
    popup_menu_text = None # "Insert translation..."

    def default_filename(self, card_type, foreign_text):
        if len(foreign_text) < 10:
            filename = foreign_text + ".mp3"
        else:
            filename = datetime.datetime.today().strftime("%Y%m%d.mp3")
        local_dir = self.config()["tts_dir_for_card_type_id"]\
            .get(card_type.id, "")
        filename = os.path.join(local_dir, filename)
        full_path = expand_path(filename, self.database().media_dir())
        full_path = make_filename_unique(full_path)
        filename = contract_path(full_path, self.database().media_dir())
        return filename

    def download_tmp_audio_file(self, card_type, foreign_text):

        """Returns a temporary filename with the audio."""

        raise NotImplementedError

    def show_dialog(self, card_type, foreign_text):

        """Returns html audio tag to insert."""

        dialog = self.gui_components[0](\
            pronouncer=self, component_manager=self.component_manager)
        self.component_manager.register(dialog)
        dialog.activate(card_type, foreign_text)
        self.instantiated_gui_components.append(dialog)
        return dialog.text_to_insert

