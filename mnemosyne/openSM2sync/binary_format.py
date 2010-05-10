#
# binary_format.py <Peter.Bienstman@UGent.be>
#

class BinaryFormat(object):

    """Used when doing the initial sync and downloading the entire database
    as a binary file in order to speed up the sync.

    """
    
    @staticmethod
    def supports(program_name, program_version):
        raise NotImplementedError

    def __init__(self, database):
        raise NotImplementedError

    def binary_file_and_size(self, interested_in_old_reps=True):

        """Returns a file object and its size. Set size=0 for unknown."""
        
        raise NotImplementedError

    def clean_up(self):
        pass
