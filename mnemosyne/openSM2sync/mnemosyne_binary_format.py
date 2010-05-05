#
# mnemosyne_binary_format.py <Peter.Bienstman@UGent.be>
#

class MnemosyneBinaryFormat(object):

    def supports(self, program_name, program_version):
        return program_name.lower() == "mnemosyne"

    def __init__(self, database):
        self.database = database

    def binary_filename(self):
        return self.database._path

    def clean_up(self):
        pass
