#
# gui_translator.py <Peter.Bienstman@gmail.com>
#                   <Johannes.Baiter@gmail.com>
#

from mnemosyne.libmnemosyne.component import Component

_ = None

class GuiTranslator(Component):

    """Note: static text will be marked as translatable by
    `static_variable = _("...")`, e.g. in CardType. However, if want to have
    this text show up translated in the GUI, we need to use
    `_(static_variable)` there as opposed to just `static_variable`.

    This is the most straightforward design to allow switching back and forth
    between different languages in the GUI on the fly, i.e. without restarting
    the program.

    """

    component_type = "gui_translator"

    def __init__(self, component_manager):
        Component.__init__(self, component_manager)
        global _
        _ = self
        # We install a dummy translator so that translatable stings can be
        # marked even if 'activate' has not yet been called.
        self._translator = lambda x : x

    def activate(self):
        Component.activate(self)
        self.set_language(self.config()["ui_language"])
        # We cannot perform this in __init__, as we need to wait until
        # 'config' has been activated.

    def supported_languages(self):
        return []

    def set_language(self, language):

        """'language' should be an iso 693-1 code."""

        self.set_translator(language)
        self.translate_ui(language)

    def set_translator(self, language):
        raise NotImplementedError

    def translate_ui(self, language):

        """To be overridden by a GUI to do GUI-specific translation."""

        pass

    def __call__(self, text):

        """Used to do translations / mark translatable strings by _("...")."""

        return self._translator(text)


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
    "ca": "Catalan",
    "ca@valencia": "Catalan (Valencian)",
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
    "el": "Modern Greek (1453-)",
    "en": "English",
    "eo": "Esperanto",
    "es": "Spanish (Castilian)",
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
    "mi": "M\u0100ori",
    "mk": "Macedonian",
    "ml": "Malayalam",
    "mn": "Mongolian",
    "mr": "Marathi",
    "ms": "Malay",
    "mt": "Maltese",
    "my": "Burmese",
    "na": "Nauruan",
    "nb": u"Norwegian",
    "nb_NO": "Norwegian Bokm\u00e5l",
    "nd": "Northern Ndebele",
    "ne": "Nepali",
    "ng": "Ndonga",
    "nl": "Dutch",
    "nn": "Norwegian Nynorsk",
    "no": "Norwegian",
    "nr": "Southern Ndebele",
    "nv": "Navajo, Navaho",
    "ny": "Chichewa, Chewa, Nyanja",
    "oc": "Occitan (1500-)",
    "oj": "Ojibwa",
    "om": "Oromo",
    "or": "Oriya",
    "os": "Ossetian, Ossetic",
    "pa": "Punjabi, Panjabi",
    "pi": "Pali",
    "pl": "Polish",
    "ps": "Pashto language, Pashto",
    "pt": "Portuguese",
    "pt_BR": "Portuguese (Brazil)",
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
    "vo": "Volap\u00FCck",
    "wa": "Walloon",
    "wo": "Wolof",
    "xh": "Xhosa",
    "yi": "Yiddish",
    "yo": "Yoruba",
    "za": "Zhuang, Chuang",
    "zh": "Chinese",
    "zh_CN": "Chinese (Simplified)",
    "zh_HK": "Chinese (Hong Kong)",
    "zh_SG": "Chinese (Singapore)",
    "zh_TW": "Chinese (Taiwan)",
    "zu": "Zulu"
}


def iso6931_code_for_language_name(language):
    return dict((v,k) for k, v in \
        language_name_for_iso6931_code.items())[language]
