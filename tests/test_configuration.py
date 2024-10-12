import os
import sys

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne_test import MnemosyneTest
from unittest.mock import patch


class TestConfiguration(MnemosyneTest):

    def setup_method(self):
        self.initialise_data_dir()
        path = os.path.join(os.getcwd(), "..", "mnemosyne", "libmnemosyne",
                            "renderers")
        if path not in sys.path:
            sys.path.append(path)
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True,
            asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.components.append(\
            ("test_add_cards", "Widget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "EditCardDialog"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"),  automatic_upgrades=False)
        self.review_controller().reset()

    def test_default_language_default(self):
        # the default language should be the en
        assert self.config().default_language() == 'en'

    def test_supported_language_as_default(self):

        locale_map_to_test = {
                              "ca_ES@valencia.UTF-8": "ca@valencia",
                              "de_DE.UTF-8": "de",
                              "en_US.UTF-8": "en",
                              "hu_HU.UTF-8": "hu",
                              "ja_JP.UTF-8": "ja",
                              "pt_BR.UTF-8": "pt_BR",
                              "pt_PT.UTF-8": "pt",
                              "sv_SE.UTF-8": "sv",
                              "zh_CN.UTF-8": "zh_CN",
                              "zh_HK.UTF-8": "zh_HK",
                              "zh_TW.UTF-8": "zh_TW",
                              }

        with patch('mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator.GetTextGuiTranslator.supported_languages') as mock_supported:
            # in development mode, we need to mock the supported_languages
            mock_supported.return_value = ['ca', 'gl', 'ja', 'pt', 'pl',
                                           'nb', 'tr', 'id', 'ca@valencia',
                                           'zh_TW', 'cs', 'zh_CN', 'nl', 'fr',
                                           'he', 'it', 'da', 'sr', 'de',
                                           'pt_BR', 'ru', 'eo', 'hr', 'sv',
                                           'uk', 'fa', 'hu', 'zh_HK', 'es']
            for lang_locale in locale_map_to_test:
                lang_code, encoding = lang_locale.split(".")
                with patch('mnemosyne.libmnemosyne.configuration.getdefaultlocale') as mock_locale:
                    mock_locale.return_value = (lang_code, encoding)
                    lang = self.config().default_language()
                    assert lang == locale_map_to_test[lang_locale]
                    mock_locale.assert_called_once()
