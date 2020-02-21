#
# responsive_voice_tts.py <Peter.Bienstman@UGent.be>
#

# Set up your account according to
# https://cloud.google.com/text-to-speech/docs/quickstart-client-libraries#client-libraries-install-python

import os
import importlib
from google.cloud import texttospeech
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] \
        = 'D:\cygwin64\home\Peter\My Project-d2fe488ee997.json'

from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.pronouncer import Pronouncer


class GoogleCloudPronouncer(Pronouncer):

    used_for = "en", "en-GB", "en-US", "fr", "fr-FR", "ar"

    popup_menu_text = "Insert Google Cloud text-to-speech..."

    def download_tmp_audio_file(self, card_type, foreign_text):

        """Returns a temporary filename with the audio."""

        language_id = self.config().card_type_property(\
            "sublanguage_id", card_type)
        if not language_id:
            language_id = self.config().card_type_property(\
                "language_id", card_type)

        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.types.SynthesisInput(text=foreign_text)
        voice = texttospeech.types.VoiceSelectionParams(
            language_code=language_id,
            ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)
        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)
        response = client.synthesize_speech(synthesis_input, voice, audio_config)

        filename = expand_path("__GTTS__TMP__.mp3", self.database().media_dir())
        with open(filename, 'wb') as mp3_file:
            mp3_file.write(response.audio_content)
        return filename


class GoogleCloudTTSPlugin(Plugin):

    name = "Google Cloud TTS"
    description = "Add Google Cloud text-to-speech."
    supported_API_level = 2

    def activate(self):
        Plugin.activate(self)
        self.component = GoogleCloudPronouncer(\
            component_manager=self.component_manager)
        self.component_manager.register(self.component)
        # TODO: refactor this to plugin.py
        gui_module_name = "mnemosyne.pyqt_ui.pronouncer_dlg"
        gui_class_name = "PronouncerDlg"
        gui_class = getattr(\
            importlib.import_module(gui_module_name), gui_class_name)
        self.component_manager.add_gui_to_component(\
            "GoogleCloudPronouncer", gui_class)

    def deactivate(self):
        Plugin.deactivate(self)
        self.component_manager.unregister(self.component)



# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(GoogleCloudTTSPlugin)
