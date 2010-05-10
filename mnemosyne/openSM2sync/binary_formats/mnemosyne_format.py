#
# mnemosyne_format.py <Peter.Bienstman@UGent.be>
#

import os
import shutil
import sqlite3
import tempfile

from openSM2sync.log_entry import EventTypes


class MnemosyneFormat(object):
    
    @staticmethod
    def supports(program_name, program_version):
        return program_name.lower() == "mnemosyne"

    def __init__(self, database):
        self.database = database

    def binary_file_and_size(self, interested_in_old_reps=True):
        self.database.save()
        self.to_delete = None
        if interested_in_old_reps:
            filename = self.database._path
        else:
            tmp_file = tempfile.NamedTemporaryFile(delete=False)
            filename = tmp_file.name
            tmp_file.close()
            shutil.copy(self.database._path, filename)
            con = sqlite3.connect(filename, timeout=0.1,
                isolation_level="EXCLUSIVE")
            con.execute("delete from log where event_type=?",
                (EventTypes.REPETITION, ))
            con.execute("vacuum")
            con.commit()
            con.close()
            self.to_delete = filename
        return file(filename), os.path.getsize(filename)       

    def clean_up(self):
        if self.to_delete:
            os.remove(self.to_delete)
