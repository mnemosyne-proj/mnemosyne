#
# SQLite_no_pregenerated_data.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.databases.SQLite import SQLite


class SQLite_NoPregeneratedData(SQLite):

    store_pregenerated_data = False
