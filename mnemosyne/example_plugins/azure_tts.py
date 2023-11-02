#
# azure_tts.py <Peter.Bienstman@UGent.be>
#

# Set up your account according to
# https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/get-started-text-to-speech?tabs=windows%2Cterminal&pivots=programming-language-python

import os

from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.pronouncer import Pronouncer



class AzurePronouncer(Pronouncer):

    used_for = "ar", "zh", "ja"

    popup_menu_text = "Insert Azure text-to-speech..."

    def download_tmp_audio_file(self, card_type, foreign_text):

        """Returns a temporary filename with the audio."""
        
        from pydub import AudioSegment
        
        import azure.cognitiveservices.speech as speechsdk
        speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('COGNITIVE_SERVICE_KEY'), region=os.environ.get('COGNITIVE_SERVICE_REGION'))
        speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm)


        language_id = self.config().card_type_property(\
            "sublanguage_id", card_type)
        if not language_id:
            language_id = self.config().card_type_property(\
                "language_id", card_type)

        # https://azure.microsoft.com/en-gb/products/cognitive-services/text-to-speech/#features

        if 'zh' in language_id.lower():
            speech_config.speech_synthesis_voice_name = "zh-CN-YunzeNeural"
        if 'ar' in language_id.lower():
            speech_config.speech_synthesis_voice_name = "ar-JO-TaimNeural"
        if 'ja' in language_id.lower():
            speech_config.speech_synthesis_voice_name = "ja-JP-KeitaNeural"

        speech_config.set_speech_synthesis_output_format(\
            speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm)

        speech_synthesizer = speechsdk.SpeechSynthesizer(\
            speech_config=speech_config, audio_config=None)

        result = speech_synthesizer.speak_text_async(foreign_text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(foreign_text))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: {}".format(cancellation_details.error_details))
                    print("Did you set the speech resource key and region values?")
            return
        
        filename_wav = expand_path("__AZURE_TTS__TMP__.wav", 
            self.database().media_dir())
        filename_mp3 = expand_path("__AZURE_TTS__TMP__.mp3", 
            self.database().media_dir())
        stream = speechsdk.AudioDataStream(result)
        stream.save_to_wav_file(filename_wav)
        audio = AudioSegment.from_wav(filename_wav)
        audio.export(filename_mp3, format="mp3")  
        return filename_mp3


class AzureTTSPlugin(Plugin):

    name = "Azure TTS"
    description = "Add Azure text-to-speech."
    components = [AzurePronouncer]
    gui_for_component = {"AzurePronouncer" :
        [("mnemosyne.pyqt_ui.pronouncer_dlg", "PronouncerDlg")]}
    supported_API_level = 3


# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(AzureTTSPlugin)
