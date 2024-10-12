#
# responsive_voice_tts.py <Peter.Bienstman@gmail.com>
#

# (no longer works)

import urllib
import importlib

from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.pronouncer import Pronouncer


class ResponsiveVoicePronouncer(Pronouncer):

    used_for = "en", "en-GB", "en-US", "fr", "fr-FR", "ar"

    popup_menu_text = "Insert ResponsiveVoice text-to-speech..."

    def download_tmp_audio_file(self, card_type, foreign_text):

        """Returns a temporary filename with the audio."""

        language_id = self.config().card_type_property(\
            "sublanguage_id", card_type)
        if not language_id:
            language_id = self.config().card_type_property(\
                "language_id", card_type)

        foreign_text = urllib.parse.quote(foreign_text.encode("utf-8"))
        headers = {'User-Agent':'Mozilla/5.0'}
        url = "https://code.responsivevoice.org/getvoice.php?t=%s&tl=%s" \
            % (foreign_text, language_id)
        req = urllib.request.Request(url=url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = response.read()

        filename = expand_path("__GTTS__TMP__.mp3", self.database().media_dir())
        with open(filename, 'wb') as mp3_file:
            mp3_file.write(data)
        return filename


class ResponsiveVoiceTTSPlugin(Plugin):

    name = "Responsive Voice TTS"
    description = "Add ResponsiveVoice text-to-speech."
    components = [ResponsiveVoicePronouncer]
    gui_for_component = {"ResponsiveVoicePronouncer" :
        [("mnemosyne.pyqt_ui.pronouncer_dlg", "PronouncerDlg")]}
    supported_API_level = 3


# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(ResponsiveVoiceTTSPlugin)
