#
# binary_format.py <Peter.Bienstman@gmail.com>
#

class BinaryFormat(object):

    """Used when doing the initial sync and downloading the entire database
    as a binary file in order to speed up the sync.

    """

    def __init__(self, database):
        raise NotImplementedError

    def supports(self, program_name, program_version, database_version):
        raise NotImplementedError

    def binary_filename(self, store_pregenerated_data,
            interested_in_old_reps):
        raise NotImplementedError

    def clean_up(self):
        pass
