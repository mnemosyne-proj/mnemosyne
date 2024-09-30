#
# google_pronouncer.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.pronouncer import Pronouncer

class GooglePronouncer(Pronouncer):

    used_for = "bn", "bn-BD", "bn-ID", "zh", "zh-CN", "zh-TW", "cs", "da", \
        "nl", "en", "en-GB", "en-US", "en-IN", "en-AU", "et", "fi", "fr", \
        "fr-FR", "fr-CA", "de", "el", "hi", "hu", "id", "it", "ja", "jw", \
        "km", "ko", "ne", "no", "pl", "pt", "pt-PT", "pt-BR", "ro", "ru", \
        "si", "sk", "es", "es-ES", "es-US", "su", "sv", "th", "tr", "uk", \
        "vi", "ar", "is"

    popup_menu_text = "Insert Google text-to-speech..."

    # https://en.wikipedia.org/wiki/Google_Text-to-Speech

    def download_tmp_audio_file(self, card_type, foreign_text):

        """Returns a temporary filename with the audio."""

        # Lazy import to speed things up.
        from gtts import gTTS

        language_id = self.config().card_type_property(\
            "sublanguage_id", card_type)
        if not language_id:
            language_id = self.config().card_type_property(\
                "language_id", card_type)
        tts = gTTS(foreign_text, lang=language_id)
        filename = expand_path("__GTTS__TMP__.mp3", self.database().media_dir())
        tts.save(filename)
        return filename
