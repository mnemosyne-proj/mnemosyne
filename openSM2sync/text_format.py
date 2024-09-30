#
# text_format.py <Peter.Bienstman@gmail.com>
#

              
class TextFormat(object):
    
    """Class handling the conversion from log entries and other data to
    text streams and vice versa.

    """

    mime_type = None

    def repr_partner_info(self, info):
        raise NotImplementedError

    def parse_partner_info(self, text):
        raise NotImplementedError

    def log_entries_header(self, number_of_entries):
        raise NotImplementedError

    def log_entries_footer(self):
        raise NotImplementedError

    def repr_log_entry(self, log_entry):
        raise NotImplementedError

    def parse_log_entries(self, txt):
        raise NotImplementedError

    def repr_message(self, message, traceback=None):
        raise NotImplementedError

    def parse_message(self, text):
        raise NotImplementedError
