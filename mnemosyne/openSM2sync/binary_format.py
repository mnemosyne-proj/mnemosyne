#
# binary_format.py <Peter.Bienstman@UGent.be>
#

class BinaryFormat(object):

    """Used when doing the initial sync and downloading the entire database
    as a binary file in order to speed up the sync.

    """
    
    def __init__(self, database):
        raise NotImplementedError
    
    def supports(self, program_name, program_version, database_version):
        raise NotImplementedError

    def binary_file_and_size(self, store_pregenerated_data,
            interested_in_old_reps):

        """Returns a file object and its size. Set size=0 for unknown."""
        
        raise NotImplementedError

    def clean_up(self):
        pass
