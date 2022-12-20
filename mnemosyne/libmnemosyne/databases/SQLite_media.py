#
# SQLite_media.py <Peter.Bienstman@gmail.com>
#

import os
import re
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

if "ANDROID" in os.environ:
    from mnemosyne.android_python.utf8_filenames import *

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.utils import normalise_path
from mnemosyne.libmnemosyne.utils import expand_path, contract_path
from mnemosyne.libmnemosyne.utils import is_filesystem_case_insensitive
from mnemosyne.libmnemosyne.utils import copy_file_to_dir, remove_empty_dirs_in

re_src = re.compile(r"""(src|data)=\"(.+?)\"""", re.DOTALL | re.IGNORECASE)


class SQLiteMedia(object):

    """Code to be injected into the SQLite database class through inheritance,
    so that SQLite.py does not becomes too large.


    """

    def media_dir(self):
        if self.config()["last_database"] == \
            os.path.basename(self.config()["last_database"]):
            return os.path.join(self.config().data_dir,
                os.path.basename(self.config()["last_database"]) + "_media")
        else:
            return self.config()["last_database"] + "_media"

    def create_media_dir_if_needed(self):
        media_dir = self.media_dir()
        if not os.path.exists(media_dir):
            try:
                os.makedirs(media_dir)
            except OSError:
                self.main_widget().show_error(_("Could not create" ) + " " + \
media_dir + ".\n" + _("Check your file permissions and make sure the directory is not open in a file browser."))

    def fact_contains_static_media_files(self, fact):
        # Could be part of fact.py, but is put here to have all media related
        # functions in one place.
        return re_src.search("".join(fact.data.values())) != None

    def _media_hash(self, filename):

        """A hash function that will be used to determine whether or not a
        media file has been modified outside of Mnemosyne.

        'filename' is a relative path inside the media dir.

        In principle, you could have different hash implementations on
        different systems, as the hash is considered something internal and is
        not sent across during sync e.g..

        """

        filename = normalise_path(os.path.join(self.media_dir(), filename))
        if not os.path.exists(filename):
            return "0"
        media_file = open(filename, "rb")
        hasher = md5()
        while True:
            buffer = media_file.read(8096)
            if not buffer:
                break
            hasher.update(buffer)
        return hasher.hexdigest()

        # The following implementation uses the modification date. Less
        # robust, but could be useful on a mobile device.

        #return os.path.getmtime(media_file)

    def check_for_edited_media_files(self):
        # Regular media files.
        new_hashes = {}
        for sql_res in self.con.execute("select filename, _hash from media"):
            filename, hash = normalise_path(sql_res[0]), sql_res[1]
            if not os.path.exists(expand_path(filename, self.media_dir())):
                continue
            new_hash = self._media_hash(filename)
            if hash != new_hash:
                new_hashes[filename] = new_hash
        for filename, new_hash in new_hashes.items():
            self.con.execute("update media set _hash=? where filename=?",
                (new_hash, filename))
            self.log().edited_media_file(filename)

    def dynamically_create_media_files(self):
        # First check which components are actually working. E.g., on a
        # headless server, it's possible that latex is not installed, so
        # we don't need to go through all the effort.
        creators = [f for f in self.component_manager.all("hook",
            "dynamically_create_media_files") if f.is_working() == True]
        if len(creators) == 0:
            return
        for cursor in self.con.execute("select value from data_for_fact"):
            for creator in creators:
                creator.run(cursor[0])

    def active_dynamic_media_files(self):
        # Other media files, e.g. latex.
        filenames = set()
        for hook in self.component_manager.all\
            ("hook", "active_dynamic_media_files"):
            # Prefilter data we need to screen.
            sql_command = """select value from data_for_fact where _fact_id in
                (select _fact_id from cards where active=1) and ("""
            for tag in hook.tags:
                sql_command += """value like '%""" + tag + """%' or """
            sql_command = sql_command[:-3] + ")"
            for cursor in self.con.execute(sql_command):
                filenames = filenames.union(hook.run(cursor[0]))
        return filenames

    def _process_media(self, fact):

        """Copy the media files to the media directory and edit the media
        table. We don't keep track of which facts use which media and delete
        a media file if it's no longer in use. The reason for this is that some
        people use the media directory as their only location to store their
        media files, and also use these files for other purposes.

        Note that not all 'added_media_file' events originated here, they are
        also generated by the latex subsystem, or by checking for files which
        were modified outside of Mnemosyne.

        """

        for match in re_src.finditer("".join(fact.data.values())):
            filename = match.group(2)
            if filename.startswith("http:"):
                continue
            if len(filename) > 200:
                self.main_widget().show_information(\
_("Media filename rather long. This could cause problems using this file on a different OS."))
            if "#" in filename:
                self.main_widget().show_information(\
_("Filename contains '#', which could cause problems on some operating systems."))
            if not os.path.exists(filename) and \
                not os.path.exists(expand_path(filename, self.media_dir())):
                self.main_widget().show_error(\
                    _("Missing media file!") + "\n\n" + filename)
                for fact_key, value in fact.data.items():
                    fact.data[fact_key] = \
                        fact.data[fact_key].replace(match.group(),
                        "src_missing=\"%s\"" % match.group(2))
                continue
            # If needed, copy file to the media dir. Normally this happens when
            # the user clicks 'Add image' e.g., but he could have typed in the
            # full path directly.
            if os.path.isabs(filename):
                filename = copy_file_to_dir(filename, self.media_dir())
            else:  # We always store Unix paths internally.
                filename = filename.replace("\\", "/")
            for fact_key, value in fact.data.items():
                fact.data[fact_key] = value.replace(match.group(2), filename)
                self.con.execute("""update data_for_fact set value=? where
                    _fact_id=? and key=?""",
                    (fact.data[fact_key], fact._id, fact_key))
            if self.con.execute("select 1 from media where filename=? limit 1",
                                (filename, )).fetchone() is None:
                self.con.execute("""insert into media(filename, _hash)
                    values(?,?)""", (filename, self._media_hash(filename)))
                # When we are applying log entries during sync or import, the
                # side effects of e.g. ADDED_FACT events should not generate
                # additional ADDED_MEDIA_FILE events at the remote partner, so
                # we disable the logging of these side effects in that case.
                if not self.syncing and not self.importing:
                    self.log().added_media_file(filename)

    def unused_media_files(self):

        """Returns a set of media files which are in the media directory but
        which are not referenced in the cards.

        """

        case_insensitive = is_filesystem_case_insensitive()
        # Files referenced in the database.
        files_in_db = set()
        for result in self.con.execute(\
            "select value from data_for_fact where value like '%src=%'"):
            for match in re_src.finditer(result[0]):
                filename = match.group(2)
                if case_insensitive:
                    filename = filename.lower()
                files_in_db.add(filename)
        # Files in the media dir.
        files_in_media_dir = set()
        for root, dirnames, filenames in os.walk(self.media_dir()):
            root = contract_path(root, self.media_dir())
            if root.startswith("_"):
                continue
            for filename in filenames:
                # Paths are stored using unix convention.
                if root:
                    filename = root + "/" + filename
                if case_insensitive:
                    filename = filename.lower()
                files_in_media_dir.add(filename)
        return files_in_media_dir - files_in_db

    def delete_unused_media_files(self, unused_files):

        """Delete media files which are no longer in use. 'unused_files'
        should be a subset of 'self.unused_media_files', because here we no
        longer check if these media files are used or not.

        """
        for filename in unused_files:
            os.remove(expand_path(filename, self.media_dir()))
            self.log().deleted_media_file(filename)
        # Purge empty dirs.
        for root, dirnames, filenames in \
            os.walk(self.media_dir(), topdown=False):
            contracted_root = contract_path(root, self.media_dir())
            if not contracted_root or contracted_root.startswith("_"):
                continue
            if len(filenames) == 0 and len(dirnames) == 0:
                os.rmdir(root)
        # Other media files, e.g. latex.
        for f in self.component_manager.all("hook",
            "delete_unused_media_files"):
            f.run()
        remove_empty_dirs_in(self.media_dir())

