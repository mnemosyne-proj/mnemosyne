#
# language.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.component import Component


class Language(Component):

    """Interface class describing the functions to be implemented by the
    actual language classes.

    Contains all language-specific calls related to parsing, stemming,
    dictionary lookup, text-to-speech, ... .

    The link between languages and card types is stored in config.db, so that
    it easily fits with the syncing logic and also works for built-in uncloned
    card types.

    """

    component_type = "language"
    name = None
    used_for = None  # ISO 639-1 code
    sublanguages = {} # {"en_GB": "English (UK)", "en_US": "English (US")}.
    feature_description = None
