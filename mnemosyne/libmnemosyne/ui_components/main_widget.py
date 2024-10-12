#
# main_widget.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.ui_component import UiComponent


class MainWidget(UiComponent):

    """Describes the interface that the main widget needs to implement
    in order to be used by the main controller.

    """

    component_type = "main_widget"

    instantiate = UiComponent.IMMEDIATELY

    def activate(self):
        pass

    def set_window_title(self, text):
        pass

    def show_information(self, text):
        print(text)

    def show_question(self, text, option0, option1, option2=""):

        """Returns 0, 1 or 2."""

        raise NotImplementedError

    def show_error(self, text):
        print(text)

    def handle_keyboard_interrupt(self, text):
        self.show_error(text)

    def default_font_size(self):
        return 12

    def get_filename_to_open(self, path, filter, caption=""):
        raise NotImplementedError

    def get_filename_to_save(self, path, filter, caption=""):

        """Should ask for confirmation on overwrite."""

        raise NotImplementedError

    def set_status_bar_message(self, text):
        pass

    def set_progress_text(self, text):

        """Resets all the attributes of the progress bar if one is still open,
        and displays 'text'.

        """

        print(text)

    def set_progress_range(self, maximum):

        """Progress bar runs from 0 to 'maximum. If 'maximum' is zero, this is
        just a busy dialog. Should be the default for set_progress_text.

        """

        pass

    def set_progress_update_interval(self, update_interval):

        """Sometimes updating the progress bar for a single step takes longer
        than doing the actual processing. In this case, it is useful to set
        'update_interval' and the progress bar will only be updated every
        'update_interval' steps.

        """

        pass

    def increase_progress(self, value):

        """Increase the progress by 'value'."""

        pass

    def set_progress_value(self, value):

        """If 'value' is maximum or beyond, the dialog closes."""

        pass

    def close_progress(self):

        """Convenience function for closing a busy dialog."""

        pass

    def enable_edit_current_card(self, is_enabled):
        pass

    def enable_delete_current_card(self, is_enabled):
        pass

    def enable_reset_current_card(self, is_enabled):
        pass

    def enable_browse_cards(self, is_enabled):
        pass

    # Moved here from default_controller.py to simplify the multithreaded
    # implementation.
    def show_export_metadata_dialog(self, metadata=None, read_only=False):
        self.stopwatch().pause()
        self.flush_sync_server()
        dialog = self.component_manager.current("export_metadata_dialog")\
            (component_manager=self.component_manager)
        if metadata:
            dialog.set_values(metadata)
        if read_only:
            dialog.set_read_only()
        dialog.activate()
        self.stopwatch().unpause()
        return dialog.values()

