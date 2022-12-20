#
# _aspw.py <Peter.Bienstman@gmail.com>
#

#
# Wrapper around APSW, to make it possible to easily swap an sqlite3
# backend with an APSW backend.
#

import os
import sys
import time
import apsw

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.component import Component


class _APSWCursor(object):

    def __init__(self, cursor):
        self.cursor = cursor

    def fetchone(self):
        try:
            return next(self.cursor)
        except StopIteration:
            return None

    def fetchall(self):
        return self.cursor.fetchall()

    def __iter__(self):
        return self.cursor

    def __next__(self):
        return next(self.cursor)


class _APSW(Component):

    # We don't need debug and tracing statements, since APSW provides tools
    # like apswtrace.

    def __init__(self, component_manager, path):
        Component.__init__(self, component_manager)
        # Make sure we don't put a database on a network drive under Windows:
        # http://www.sqlite.org/lockingv3.html
        if sys.platform == "win32":  # pragma: no cover
            drive = os.path.splitdrive(path)[0]
            import ctypes
            if ctypes.windll.kernel32.GetDriveTypeW("%s\\" % drive) == 4:
                self.main_widget().show_error(_\
("Putting a database on a network drive is forbidden under Windows to avoid data corruption. Mnemosyne will now close."))
                sys.exit(-1)
        self.connection = apsw.Connection(path)
        self.connection.setbusytimeout(250)
        cursor = self.connection.cursor()
        # http://www.mail-archive.com/sqlite-users@sqlite.org/msg34453.html
        cursor.execute("pragma journal_mode = persist;")
        # Should only be used to speed up the test suite.
        if self.config()["asynchronous_database"] == True:
            cursor.execute("pragma synchronous = off;")
        # Always start a transaction and only commit when 'commit' is called
        # explicitly.
        cursor.execute("begin;")

    def executescript(self, script):
        self.connection.cursor().execute(script)

    def execute(self, sql, *args):
        return _APSWCursor(self.connection.cursor().execute(sql, *args))

    def executemany(self, sql, *args):
        return _APSWCursor(self.connection.cursor().executemany(sql, *args))

    def last_insert_rowid(self):
        return self.connection.last_insert_rowid()

    def commit(self):
        try:
            return self.connection.cursor().execute("commit;")
        except apsw.SQLError as e:
            if "cannot commit - no transaction is active" in str(e):
                pass
            else:
                raise e
        self.connection.cursor().execute("begin;")

    def close(self):
        self.connection.close()