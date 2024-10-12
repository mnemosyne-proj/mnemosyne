#
# google_cloud_tts.py <Peter.Bienstman@gmail.com>
#

# Set up your account according to
# https://cloud.google.com/text-to-speech/docs/quickstart-client-libraries#client-libraries-install-python

import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] \
        = 'C:\cygwin64\home\Peter\My Project-d2fe488ee997.json'

from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.pronouncer import Pronouncer


class GoogleCloudPronouncer(Pronouncer):

    used_for = "en", "en-GB", "en-US", "fr", "fr-FR", "ar", "it"

    popup_menu_text = "Insert Google Cloud text-to-speech..."

    def download_tmp_audio_file(self, card_type, foreign_text):

        """Returns a temporary filename with the audio."""

        # Lazy import to speed things up.
        from google.cloud import texttospeech

        language_id = self.config().card_type_property(\
            "sublanguage_id", card_type)
        if not language_id:
            language_id = self.config().card_type_property(\
                "language_id", card_type)

        if " ج " in foreign_text:
            singular, plural = foreign_text.split(" ج ")
            foreign_text = \
                f"""<speak>{singular}<break time="0.3s"/>{plural}</speak>"""
        if "<br>" in foreign_text:
            foreign_text = "<speak>" + \
                foreign_text.replace("<br>", """<break time="0.3s"/>""") +\
                "</speak>"
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(ssml=foreign_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_id,
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3)
        response = client.synthesize_speech(request={
            "input": synthesis_input,
            "voice": voice,
            "audio_config": audio_config})

        filename = expand_path("__GTTS__TMP__.mp3", self.database().media_dir())
        with open(filename, 'wb') as mp3_file:
            mp3_file.write(response.audio_content)
        return filename


class GoogleCloudTTSPlugin(Plugin):

    name = "Google Cloud TTS"
    description = "Add Google Cloud text-to-speech."
    components = [GoogleCloudPronouncer]
    gui_for_component = {"GoogleCloudPronouncer" :
        [("mnemosyne.pyqt_ui.pronouncer_dlg", "PronouncerDlg")]}
    supported_API_level = 3


# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(GoogleCloudTTSPlugin)
