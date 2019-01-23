#
# google_pronouncer.py <Peter.Bienstman@UGent.be>
#

from gtts import gTTS

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.pronouncer import Pronouncer


class GooglePronouncer(Pronouncer):

    used_for = "ar", "en", "fr"
    popup_menu_text = "Insert Google text-to-speech..."

    # https://cloud.google.com/speech-to-text/docs/languages

    def download_tmp_audio_file(self, card_type, foreign_text):

        """Returns a temporary filename with the audio."""

        language_id = self.config().card_type_property(\
            "language_id", card_type)
        try:
            tts = gTTS(foreign_text, language_id)
        except Exception as e:
            1/0
        filename = expand_path("__GTTS__TMP__.mp3", self.database().media_dir())
        tts.save(filename)
        return filename
