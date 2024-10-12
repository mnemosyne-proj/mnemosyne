#
# ui.py <Peter.Bienstman@gmail.com>
#

class UI(object):

    """Interface that needs to be implemented by the Ui object used in the
    Client and the Server.

    """

    def show_information(self, message):
        print(message)

    def show_error(self, message):
        print(message)

    def show_question(self, question, option0, option1, option2):

        """Returns 0, 1 or 2."""

        raise NotImplementedError

    def set_progress_text(self, text):

        """Resets all the attributes of the progress bar if one is still open,
        and displays 'text'.

        """

        pass

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
