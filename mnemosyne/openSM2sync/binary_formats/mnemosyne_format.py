#
# mnemosyne_format.py <Peter.Bienstman@UGent.be>
#

import os


class MnemosyneFormat(object):
    
    @staticmethod
    def supports(program_name, program_version):
        return program_name.lower() == "mnemosyne"

    def __init__(self, database):
        self.database = database

    def binary_file_and_size(self):
        size = os.path.getsize(self.database._path)
        return file(self.database._path), size

    def clean_up(self):
        pass
