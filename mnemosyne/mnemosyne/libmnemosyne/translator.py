#
# translator.py <Peter.Bienstman@UGent.be>
#               <Johannes.Baiter@gmail.com>
#

import os
import sys
    
from mnemosyne.libmnemosyne.component import Component

# Dummy translator for cases where no translator is activated
_ = lambda s: s


# http://en.wikipedia.org/wiki/List_of_ISO_639-2_codes

language_name_for_iso6931_code = {
    "aa": "Afar",
    "ab": "Abkhazian",
    "ae": "Avestan",
    "af": "Afrikaans",
    "ak": "Akan",
    "am": "Amharic",
    "an": "Aragonese",
    "ar": "Arabic",
    "as": "Assamese",
    "av": "Avaric",
    "ay": "Aymara",
    "az": "Azerbaijani",
    "ba": "Bashkir",
    "be": "Belarusian",
    "bg": "Bulgarian",
    "bh": "Bihari languages",
    "bi": "Bislama",
    "bm": "Bambara",
    "bn": "Bengali",
    "bo": "Tibetan",
    "br": "Breton",
    "bs": "Bosnian",
    "ca": "Catalan, Valencian",
    "ce": "Chechen",
    "ch": "Chamorro",
    "co": "Corsican",
    "cr": "Cree",
    "cs": "Czech",
    "cu": "Church Slavonic, Church Slavic, Old Church Slavonic, Old Slavonic, Old Bulgarian",
    "cv": "Chuvash",
    "cy": "Welsh",
    "da": "Danish",
    "de": "German",
    "dv": "Divehi, Dhivehi, Maldivian",
    "dz": "Dzongkha",
    "ee": "Ewe",
    "el": "Modern Greek (1453\xe2\x80\x93)",
    "en": "English",
    "eo": "Esperanto",
    "es": "Spanish, Castilian",
    "et": "Estonian",
    "eu": "Basque",
    "fa": "Persian",
    "ff": "Fulah",
    "fi": "Finnish",
    "fj": "Fijian",
    "fo": "Faroese",
    "fr": "French",
    "fy": "Western Frisian",
    "ga": "Irish",
    "gd": "Scottish Gaelic, Gaelic",
    "gl": "Galician",
    "gn": "Guarani",
    "gu": "Gujarati",
    "gv": "Manx",
    "ha": "Hausa",
    "he": "Hebrew",
    "hi": "Hindi",
    "ho": "Hiri Motu",
    "hr": "Croatian",
    "ht": "Haitian Creole, Haitian",
    "hu": "Hungarian",
    "hy": "Armenian",
    "hz": "Herero",
    "ia": "Interlingua (International Auxiliary Language Association)",
    "id": "Indonesian",
    "ie": "Interlingue, Occidental",
    "ig": "Igbo",
    "ii": "Sichuan Yi, Nuosu",
    "ik": "Inupiaq",
    "io": "Ido",
    "is": "Icelandic",
    "it": "Italian",
    "iu": "Inuktitut",
    "ja": "Japanese",
    "jv": "Javanese",
    "ka": "Georgian",
    "kg": "Kongo",
    "ki": "Kikuyu, Gikuyu",
    "kj": "Kuanyama, Kwanyama",
    "kk": "Kazakh",
    "kl": "Greenlandic, Kalaallisut",
    "km": "Central Khmer",
    "kn": "Kannada",
    "ko": "Korean",
    "kr": "Kanuri",
    "ks": "Kashmiri",
    "ku": "Kurdish",
    "kv": "Komi",
    "kw": "Cornish",
    "ky": "Kirghiz, Kyrgyz",
    "la": "Latin",
    "lb": "Luxembourgish, Letzeburgesch",
    "lg": "Luganda",
    "li": "Limburgish, Limburger, Limburgan",
    "ln": "Lingala",
    "lo": "Lao",
    "lt": "Lithuanian",
    "lu": "Luba-Katanga",
    "lv": "Latvian",
    "mg": "Malagasy",
    "mh": "Marshallese",
    "mi": "M\xc4\x81ori",
    "mk": "Macedonian",
    "ml": "Malayalam",
    "mn": "Mongolian",
    "mr": "Marathi",
    "ms": "Malay",
    "mt": "Maltese",
    "my": "Burmese",
    "na": "Nauruan",
    "nb": "Norwegian Bokm\xc3\xa5l",
    "nd": "Northern Ndebele",
    "ne": "Nepali",
    "ng": "Ndonga",
    "nl": "Dutch, Flemish",
    "nn": "Norwegian Nynorsk",
    "no": "Norwegian",
    "nr": "Southern Ndebele",
    "nv": "Navajo, Navaho",
    "ny": "Chichewa, Chewa, Nyanja",
    "oc": "Occitan (1500\xe2\x80\x93)",
    "oj": "Ojibwa",
    "om": "Oromo",
    "or": "Oriya",
    "os": "Ossetian, Ossetic",
    "pa": "Punjabi, Panjabi",
    "pi": "Pali",
    "pl": "Polish",
    "ps": "Pashto language, Pashto",
    "pt": "Portuguese",
    "qu": "Quechua",
    "rm": "Romansh",
    "rn": "Rundi",
    "ro": "Romanian",
    "ru": "Russian",
    "rw": "Kinyarwanda",
    "sa": "Sanskrit",
    "sc": "Sardinian",
    "sd": "Sindhi",
    "se": "Northern Sami",
    "sg": "Sango",
    "si": "Sinhalese, Sinhala",
    "sk": "Slovak",
    "sl": "Slovenian",
    "sm": "Samoan",
    "sn": "Shona",
    "so": "Somali",
    "sq": "Albanian",
    "sr": "Serbian",
    "ss": "Swati",
    "st": "Southern Sotho",
    "su": "Sundanese",
    "sv": "Swedish",
    "sw": "Swahili",
    "ta": "Tamil",
    "te": "Telugu",
    "tg": "Tajik",
    "th": "Thai",
    "ti": "Tigrinya",
    "tk": "Turkmen",
    "tl": "Tagalog",
    "tn": "Tswana",
    "to": "Tonga (Tonga Islands)",
    "tr": "Turkish",
    "ts": "Tsonga",
    "tt": "Tatar",
    "tw": "Twi",
    "ty": "Tahitian",
    "ug": "Uighur, Uyghur",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "uz": "Uzbek",
    "ve": "Venda",
    "vi": "Vietnamese",
    "vo": "Volap\xc3\xbck",
    "wa": "Walloon",
    "wo": "Wolof",
    "xh": "Xhosa",
    "yi": "Yiddish",
    "yo": "Yoruba",
    "za": "Zhuang, Chuang",
    "zh": "Chinese",
    "zu": "Zulu" 
}


def iso6931_code_for_language_name(language):
    return dict((v,k) for k, v in \
        language_name_for_iso6931_code.iteritems())[language]


class Translator(Component):

    component_type = "translator"

    def __init__(self, component_manager):
        Component.__init__(self, component_manager)
        global _
        _ = self

    def __call__(self, text):
        raise NotImplementedError
    

class NoTranslation(Translator):

    def __call__(self, text):
        return text


class GetTextTranslator(Translator):

    def activate(self):
        # We cannot perform this in __init__, as we need the config to be
        # activated.
        self.change_language(self.config()["ui_language"])
        global _
        _ = self

    def change_language(self, language):
        if not language:
            language = ""
        # Check if we're running in a development environment.
        if os.path.exists("mo"):
            localedir = "mo"
        else:
            localedir = os.path.join(sys.exec_prefix, "share", "locale")
        import gettext
        self._gettext = gettext.translation("mnemosyne", localedir=localedir,
            languages=[language], fallback=True)

    def supported_languages(self):
        import glob
        # Check if we're running in a development environment.
        if os.path.exists("mo"):
            langs = [os.path.split(x)[1] for x in glob.glob(\
                os.path.join("mo", "*")) if os.path.isdir(x) \
                and len(os.path.split(x)[1]) == 2]
        else:
            if sys.platform == "win32":
                path_separator = "\\"
            else:
                path_separator = "/"
            langs = [x.split(path_separator)[-3] for x in glob.glob(
                os.path.join(sys.exec_prefix, "share", "locale", "*",
                "LC_MESSAGES", "mnemosyne.mo"))]
        return langs

    def __call__(self, text):
        if hasattr(self, "_gettext"):
            return self._gettext.ugettext(text)
        else:  # Translator was not yet activated.
            return text
