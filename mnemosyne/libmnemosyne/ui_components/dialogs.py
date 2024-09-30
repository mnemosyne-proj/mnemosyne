#
# dialogs.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.ui_component import UiComponent


class Dialog(UiComponent):

    component_type = "dialog"
    instantiate = UiComponent.LATER


class AddCardsDialog(Dialog):

    component_type = "add_cards_dialog"


class EditCardDialog(Dialog):

    """Note: even though this is in essence an EditFactDialog, we don't use
    'fact' as argument, as 'fact' does not know anything about card types.

    """

    component_type = "edit_card_dialog"

    def __init__(self, card, component_manager, allow_cancel=True):
        Dialog.__init__(self, component_manager)


class ActivateCardsDialog(Dialog):

    component_type = "activate_cards_dialog"


class BrowseCardsDialog(Dialog):

    component_type = "browse_cards_dialog"


class ManagePluginsDialog(Dialog):

    component_type = "manage_plugins_dialog"


class ManageCardTypesDialog(Dialog):

    component_type = "manage_card_types_dialog"


class StatisticsDialog(Dialog):

    component_type = "statistics_dialog"


class ConfigurationDialog(Dialog):

    component_type = "configuration_dialog"


class SyncDialog(Dialog):

    component_type = "sync_dialog"


class GettingStartedDialog(Dialog):

    component_type = "getting_started_dialog"


class TipDialog(Dialog):

    component_type = "tip_dialog"


class AboutDialog(Dialog):

    component_type = "about_dialog"


class ImportDialog(Dialog):

    component_type = "import_dialog"


class ExportDialog(Dialog):

    component_type = "export_dialog"


class ExportMetadataDialog(Dialog):

    component_type = "export_metadata_dialog"

    def values(self):
        raise NotImplementedError


class CompactDatabaseDialog(Dialog):

    component_type = "compact_database_dialog"


class EditMSidedCardTypeDialog(Dialog):

    component_type = "edit_M_sided_card_type_dialog"


class EditMSidedCardTemplateWidget(Dialog):

    component_type = "edit_M_sided_card_template_widget"


class PronouncerDialog(Dialog):

    component_type = "pronouncer_dialog"


class TranslatorDialog(Dialog):

    component_type = "translator_dialog"

