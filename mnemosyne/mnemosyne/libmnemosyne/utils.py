#
# utils.py <Peter.Bienstman@UGent.be>
#          <Johannes.Baiter@gmail.com>
#

import os
import re
import cgi
import sys
import random
import shutil
import traceback

iso6931_dict = {
    'aa': 'Afar',
    'ab': 'Abkhazian',
    'ae': 'Avestan',
    'af': 'Afrikaans',
    'ak': 'Akan',
    'am': 'Amharic',
    'an': 'Aragonese',
    'ar': 'Arabic',
    'as': 'Assamese',
    'av': 'Avaric',
    'ay': 'Aymara',
    'az': 'Azerbaijani',
    'ba': 'Bashkir',
    'be': 'Belarusian',
    'bg': 'Bulgarian',
    'bh': 'Bihari languages',
    'bi': 'Bislama',
    'bm': 'Bambara',
    'bn': 'Bengali',
    'bo': 'Tibetan',
    'br': 'Breton',
    'bs': 'Bosnian',
    'ca': 'Catalan, Valencian',
    'ce': 'Chechen',
    'ch': 'Chamorro',
    'co': 'Corsican',
    'cr': 'Cree',
    'cs': 'Czech',
    'cu': 'Church Slavonic, Church Slavic, Old Church Slavonic, Old Slavonic, Old Bulgarian',
    'cv': 'Chuvash',
    'cy': 'Welsh',
    'da': 'Danish',
    'de': 'German',
    'dv': 'Divehi, Dhivehi, Maldivian',
    'dz': 'Dzongkha',
    'ee': 'Ewe',
    'el': 'Modern Greek (1453\xe2\x80\x93)',
    'en': 'English',
    'eo': 'Esperanto',
    'es': 'Spanish, Castilian',
    'et': 'Estonian',
    'eu': 'Basque',
    'fa': 'Persian',
    'ff': 'Fulah',
    'fi': 'Finnish',
    'fj': 'Fijian',
    'fo': 'Faroese',
    'fr': 'French',
    'fy': 'Western Frisian',
    'ga': 'Irish',
    'gd': 'Scottish Gaelic, Gaelic',
    'gl': 'Galician',
    'gn': 'Guarani',
    'gu': 'Gujarati',
    'gv': 'Manx',
    'ha': 'Hausa',
    'he': 'Hebrew',
    'hi': 'Hindi',
    'ho': 'Hiri Motu',
    'hr': 'Croatian',
    'ht': 'Haitian Creole, Haitian',
    'hu': 'Hungarian',
    'hy': 'Armenian',
    'hz': 'Herero',
    'ia': 'Interlingua (International Auxiliary Language Association)',
    'id': 'Indonesian',
    'ie': 'Interlingue, Occidental',
    'ig': 'Igbo',
    'ii': 'Sichuan Yi, Nuosu',
    'ik': 'Inupiaq',
    'io': 'Ido',
    'is': 'Icelandic',
    'it': 'Italian',
    'iu': 'Inuktitut',
    'ja': 'Japanese',
    'jv': 'Javanese',
    'ka': 'Georgian',
    'kg': 'Kongo',
    'ki': 'Kikuyu, Gikuyu',
    'kj': 'Kuanyama, Kwanyama',
    'kk': 'Kazakh',
    'kl': 'Greenlandic, Kalaallisut',
    'km': 'Central Khmer',
    'kn': 'Kannada',
    'ko': 'Korean',
    'kr': 'Kanuri',
    'ks': 'Kashmiri',
    'ku': 'Kurdish',
    'kv': 'Komi',
    'kw': 'Cornish',
    'ky': 'Kirghiz, Kyrgyz',
    'la': 'Latin',
    'lb': 'Luxembourgish, Letzeburgesch',
    'lg': 'Luganda',
    'li': 'Limburgish, Limburger, Limburgan',
    'ln': 'Lingala',
    'lo': 'Lao',
    'lt': 'Lithuanian',
    'lu': 'Luba-Katanga',
    'lv': 'Latvian',
    'mg': 'Malagasy',
    'mh': 'Marshallese',
    'mi': 'M\xc4\x81ori',
    'mk': 'Macedonian',
    'ml': 'Malayalam',
    'mn': 'Mongolian',
    'mr': 'Marathi',
    'ms': 'Malay',
    'mt': 'Maltese',
    'my': 'Burmese',
    'na': 'Nauruan',
    'nb': 'Norwegian Bokm\xc3\xa5l',
    'nd': 'Northern Ndebele',
    'ne': 'Nepali',
    'ng': 'Ndonga',
    'nl': 'Dutch, Flemish',
    'nn': 'Norwegian Nynorsk',
    'no': 'Norwegian',
    'nr': 'Southern Ndebele',
    'nv': 'Navajo, Navaho',
    'ny': 'Chichewa, Chewa, Nyanja',
    'oc': 'Occitan (1500\xe2\x80\x93)',
    'oj': 'Ojibwa',
    'om': 'Oromo',
    'or': 'Oriya',
    'os': 'Ossetian, Ossetic',
    'pa': 'Punjabi, Panjabi',
    'pi': 'Pali',
    'pl': 'Polish',
    'ps': 'Pashto language, Pashto',
    'pt': 'Portuguese',
    'qu': 'Quechua',
    'rm': 'Romansh',
    'rn': 'Rundi',
    'ro': 'Romanian',
    'ru': 'Russian',
    'rw': 'Kinyarwanda',
    'sa': 'Sanskrit',
    'sc': 'Sardinian',
    'sd': 'Sindhi',
    'se': 'Northern Sami',
    'sg': 'Sango',
    'si': 'Sinhalese, Sinhala',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'sm': 'Samoan',
    'sn': 'Shona',
    'so': 'Somali',
    'sq': 'Albanian',
    'sr': 'Serbian',
    'ss': 'Swati',
    'st': 'Southern Sotho',
    'su': 'Sundanese',
    'sv': 'Swedish',
    'sw': 'Swahili',
    'ta': 'Tamil',
    'te': 'Telugu',
    'tg': 'Tajik',
    'th': 'Thai',
    'ti': 'Tigrinya',
    'tk': 'Turkmen',
    'tl': 'Tagalog',
    'tn': 'Tswana',
    'to': 'Tonga (Tonga Islands)',
    'tr': 'Turkish',
    'ts': 'Tsonga',
    'tt': 'Tatar',
    'tw': 'Twi',
    'ty': 'Tahitian',
    'ug': 'Uighur, Uyghur',
    'uk': 'Ukrainian',
    'ur': 'Urdu',
    'uz': 'Uzbek',
    've': 'Venda',
    'vi': 'Vietnamese',
    'vo': 'Volap\xc3\xbck',
    'wa': 'Walloon',
    'wo': 'Wolof',
    'xh': 'Xhosa',
    'yi': 'Yiddish',
    'yo': 'Yoruba',
    'za': 'Zhuang, Chuang',
    'zh': 'Chinese',
    'zu': 'Zulu' 
}

def _abs_path(path):

    """Our own version of os.path.abspath, which does not check for platform.
    In this way, we can test Windows paths even when running the testsuite
    under Linux.
    
    """

    return    ((len(path) > 1) and path[0] == "/") \
           or ((len(path) > 2) and path[1] == ":")


def contract_path(path, start):

    """Return relative path to 'path' from the directory 'start'.
    
    All paths in Mnemosyne are internally stored with Unix separators /.

    """

    # Normalise paths and convert everything to lowercase on Windows.
    # We avoid os.path.normcase here, so that we can test Windows paths
    # even when running the testsuite under Linux.
    path = os.path.normpath(path)
    start = os.path.normpath(start)
    if ( (len(path) > 2) and path[1] == ":"):
        path = path.lower()
        start = start.lower()
    # Do the actual detection.
    if _abs_path(path):
        try:
            rel_path = path.split(start)[1][1:]
        except:
            rel_path = path   
    else:
        rel_path = path
    return rel_path.replace("\\", "/")


def expand_path(path, start):

    """Make 'path' absolute starting from 'start'.

    Also convert Unix separators to Windows separators on that platform.

    """

    if _abs_path(path):
        return os.path.normcase(path)
    else:  
        return os.path.normcase(os.path.join(start, path))


def copy_file_to_dir(filename, dirname):

    """If the file is not in the directory, copy it there. Return the relative
    path to that file inside the directory.

    """

    filename = os.path.abspath(os.path.normcase(filename))
    dirname = os.path.abspath(os.path.normcase(dirname))
    if filename.startswith(dirname):
        return contract_path(filename, dirname)
    dest_path = os.path.join(dirname, os.path.basename(filename))
    if os.path.exists(dest_path):  # Rename it to something unique.
        prefix, suffix = dest_path.rsplit(".", 1)
        count = 0
        while True:
            count += 1
            dest_path = "%s_%d_.%s" % (prefix, count, suffix)
            if not os.path.exists(dest_path):
                break
    shutil.copy(filename, dest_path)
    return contract_path(dest_path, dirname)


def numeric_string_cmp(s1, s2):
    
    """Compare two strings using numeric ordering
    
    Compare the two strings s1 and s2 and return an integer according to the 
    outcome. The return value is negative if s1 < s2, zero if s1 == s2 and 
    strictly positive if s1 > s2. Unlike the standard python cmp() function
    numeric_string_cmp() compares strings using a natural numeric ordering,
    so that, e.g., "abc2" < "abc10".

    The strings are first split into tuples consisting of the alphabetic and
    numeric portions of the string. For example, "33_file1.txt" is converted
    to the tuple ('', 33, '_file', 1, '.txt'). The tuples are then compared
    using the standard python cmp().

    """
    
    atoi = lambda s: int(s) if s.isdigit() else s.lower()
    scan = lambda s: tuple(atoi(str) for str in re.split('(\d+)', s))
    return cmp(scan(s1), scan(s2))


def traceback_string():
    
    """Like traceback.print_exc(), but returns a string."""

    type, value, tb = sys.exc_info()
    body = "\nTraceback (innermost last):\n"
    list = traceback.format_tb(tb, limit=None) + \
           traceback.format_exception_only(type, value)
    body = body + "%-20s %s" % ("".join(list[:-1]), list[-1])
    del tb  # Prevent circular references.
    return body


def mangle(string):

    """Massage string such that it can be used as an identifier."""

    string = cgi.escape(string).encode("ascii", "xmlcharrefreplace")
    if string[0].isdigit():
        string = "_" + string
    new_string = ""
    for char in string:
        if char.isalnum() or char == "_":
            new_string += char    
    return new_string


def rand_uuid():

    """Importing Python's uuid module brings a huge overhead, so we use
    our own variant: a length 22 random string from a 62 letter alphabet,
    which in terms of randomness is about the same as the traditional hex
    string with length 32, but uses less space.

    """
    
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXZY0123456789"
    rand = random.random
    uuid = ""
    for c in range(22):
        uuid += chars[int(rand() * 62.0 - 1)]
    return uuid



class CompareOnId(object):

    """When pulling the same object twice from an SQL database, the resulting
    Python objects will be separate entities. That's why we need to compare
    them on id.

    """
  
    def __eq__(self, other):
        if isinstance(other, CompareOnId):
            return self.id == other.id
        return NotImplemented  # So Python can try other.__eq__(self)
    
    def __ne__(self, other):

        """Not automatically overridden by overriding __eq__!"""
        
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

def get_iso6931_code(language):
    """Returns ISO693-1 language code for every language name in English
       according to `iso6931_dict`.
       Needed for internationalization purposes.
       Data taken from Wikipedia:
            http://en.wikipedia.org/wiki/List_of_ISO_639-2_codes

    """
    return dict((v,k) for k, v in iso6931_dict.iteritems())[language]
