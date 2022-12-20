#
# controller.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.component import Component


class Controller(Component):

    """A collection of logic used by the GUI.  The logic related to the
    review process is split out in a separated controller class, to
    allow that to be swapped out easily.

    There are two classes of functions here: 'show_XXX_dialog', which needs
    to be called by the GUI to set everything up to show a certain dialog,
    and then the other functions, which the implementation of the actual
    dialog can use to perform GUI-independent operations.

    See also 'How to write a new frontend' in the docs.

    """

    component_type = "controller"

    def heartbeat(self):

        """For code that needs to run periodically."""

        pass

    def update_title(self):
        raise NotImplementedError

    def show_add_cards_dialog(self):
        raise NotImplementedError

    def set_study_mode(self, study_mode):
        raise NotImplementedError

    def create_new_cards(self, fact_data, card_type, grade,
            tag_names, check_for_duplicates=True, save=True):
        raise NotImplementedError

    def show_edit_card_dialog(self):
        raise NotImplementedError

    def edit_card_and_sisters(self, card, new_fact_data, new_card_type,
            new_tag_names, correspondence):
        raise NotImplementedError

    def change_card_type(self, facts, old_card_type, new_card_type,
                         correspondence):

        """Note: all facts should have the same card type."""

        raise NotImplementedError

    def star_current_card(self):
        raise NotImplementedError

    def delete_current_card(self):
        raise NotImplementedError

    def delete_facts_and_their_cards(self, facts):
        raise NotImplementedError

    def reset_current_card(self):
        raise NotImplementedError

    def reset_facts_and_their_cards(self, facts):
        raise NotImplementedError

    def clone_card_type(self, card_type, clone_name):
        raise NotImplementedError

    def delete_card_type(self, card_type):
        raise NotImplementedError

    def show_new_file_dialog(self):
        raise NotImplementedError

    def show_open_file_dialog(self):
        raise NotImplementedError

    def save_file(self):
        raise NotImplementedError

    def show_save_file_as_dialog(self):
        raise NotImplementedError

    def show_insert_img_dialog(self, filter):

        """Filter contains the file dialog filter with the supported
        filetypes.

        """

        raise NotImplementedError

    def show_insert_sound_dialog(self, filter):

        """Filter contains the file dialog filter with the supported
        filetypes.

        """

        raise NotImplementedError

    def show_insert_video_dialog(self, filter):

        """Filter contains the file dialog filter with the supported
        filetypes.

        """

        raise NotImplementedError

    def show_browse_cards_dialog(self):
        raise NotImplementedError

    def show_manage_plugins_dialog(self):
        raise NotImplementedError

    def install_plugin(self):
        raise NotImplementedError

    def delete_plugin(self, plugin):
        raise NotImplementedError

    def show_manage_card_types_dialog(self):
        raise NotImplementedError

    def show_statistics_dialog(self):
        raise NotImplementedError

    def show_configuration_dialog(self):
        raise NotImplementedError

    def show_import_file_dialog(self):
        raise NotImplementedError

    def show_export_file_dialog(self):
        raise NotImplementedError

    def show_sync_dialog(self):
        raise NotImplementedError

    def show_tip_dialog(self):
        raise NotImplementedError

    def show_getting_started_dialog(self):
        raise NotImplementedError

    def sync(self, server, port, username, password, ui=None):
        raise NotImplementedError
