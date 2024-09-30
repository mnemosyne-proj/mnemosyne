#
# _sqlite3.py <Peter.Bienstman@gmail.com>
#

#
# Wrapper around sqlite3, to make it possible to easily swap an sqlite3
# backend with an APSW backend.
#

import os
import sys
import time
import sqlite3

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import traceback_string, MnemosyneError


class _Sqlite3Cursor(object):

    def __init__(self, cursor):
        self.cursor = cursor

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.cursor)


class _Sqlite3(Component):

    DEBUG = False

    def __init__(self, component_manager, path):
        Component.__init__(self, component_manager)
        self._cursor = None
        # Make sure we don't put a database on a network drive under Windows:
        # http://www.sqlite.org/lockingv3.html
        if sys.platform == "win32":  # pragma: no cover
            drive = os.path.splitdrive(path)[0]
            import ctypes
            if ctypes.windll.kernel32.GetDriveTypeW("%s\\" % drive) == 4:
                self.main_widget().show_error(_\
("Putting a database on a network drive is forbidden under Windows to avoid data corruption. Mnemosyne will now close."))
                sys.exit(-1)
        self.connection = sqlite3.connect(path)
        # http://www.mail-archive.com/sqlite-users@sqlite.org/msg34453.html
        self.connection.execute("pragma journal_mode = persist;")
        # Should only be used to speed up the test suite.
        if self.config()["asynchronous_database"] == True:
            self.connection.execute("pragma synchronous = off;")

    def executescript(self, script):
        if self.DEBUG:
            print(script)
            t = time.time()
        self.connection.executescript(script)
        if self.DEBUG:
            print(("took %.3f secs" % (time.time() - t)))

    def execute(self, sql, *args):
        if self.DEBUG:
            print((sql, args))
            t = time.time()
        try:
            self._cursor = self.connection.execute(sql, *args)
        except:
            raise MnemosyneError("SQL error: " + sql + " " + str(*args)
                + "\n" + traceback_string())
        if self.DEBUG:
            print(("took %.3f secs" % (time.time() - t)))
        return _Sqlite3Cursor(self._cursor)

    def executemany(self, sql, *args):
        if self.DEBUG:
            print((sql, args))
            t = time.time()
        self._cursor = self.connection.executemany(sql, *args)
        if self.DEBUG:
            print(("took %.3f secs" % (time.time() - t)))
        return _Sqlite3Cursor(self._cursor)

    def last_insert_rowid(self):
        return self._cursor.lastrowid

    def commit(self):
        return self.connection.commit()

    def close(self):
        del self._cursor
        return self.connection.close()
