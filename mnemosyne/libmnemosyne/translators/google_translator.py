#
# google_translator.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.translator import Translator

translator = None

class GoogleTranslator(Translator):

    # https://cloud.google.com/translate/docs/languages

    used_for = "af", "sq", "am", "ar", "hy", "az", "eu", "be", "bn", "bs", \
        "bg", "ca", "ceb", "zh", "zh-CN", "zh-TW", "co", "hr", "cs", "da", \
        "nl", "en", "eo", "et", "fi", "fr", "fy", "gl", "ka", "de", "el", \
        "gu", "ht", "ha", "haw", "he", "hi", "hmn", "hu", "is", "ig", "id", \
        "ga", "it", "ja", "jw", "kn", "kk", "km", "ko", "ku", "ky", "lo", \
        "la", "lv", "lt", "lb", "mk", "mg", "ms", "ml", "mt", "mi", "mr", \
        "mn", "my", "ne", "no", "ny", "ps", "fa", "pl", "pt", "pa", "ro", \
        "ru", "sm", "gd", "sr", "st", "sn", "sd", "si", "sk", "sl", "so", \
        "es", "su", "sw", "sv", "tl", "tg", "ta", "te", "th", "tr", "uk", \
        "ur", "uz", "vi", "cy", "xh", "yi", "yo", "zu"

    popup_menu_text = "Insert Google translation..."

    def translate(self, card_type, foreign_text, target_language_id,
                  retries=0):
        # Lazy import to speed things up.
                  
        from google_trans_new import google_translator
        #from googletrans import Translator as google_translator
        # Note: also update libmnemosyne/__init__.py if you change this.

        global translator
        if not translator:
            translator = google_translator()
        source_language_id = self.config().card_type_property(\
            "language_id", card_type)
        try:
            result = translator.translate(foreign_text,
                lang_tgt=target_language_id, lang_src=source_language_id).strip()
            #result = translator.translate(foreign_text,
            #    dest=target_language_id, src=source_language_id).text.strip()
        except Exception as e:
            if retries < 5:
                import time; time.sleep(2)
                translator = google_translator()
                return self.translate(card_type, foreign_text,
                    target_language_id, retries=retries+1)
            else:
                return None
        return result
