#
# google_pronouncer.py <Peter.Bienstman@UGent.be>
#

from gtts import gTTS

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.pronouncer import Pronouncer


class GooglePronouncer(Pronouncer):

    used_for = "ar"  # TMP. Or get in from card_type language?
    popup_menu_text = "Insert Google text-to-speech..."

    def download_tmp_audio_file(self, foreign_text):

        """Returns a temporary filename with the audio."""

        tts = gTTS(foreign_text, lang=self.used_for)
        filename = expand_path("__GTTS__TMP__.mp3", self.database().media_dir())
        tts.save(filename)
        return filename
