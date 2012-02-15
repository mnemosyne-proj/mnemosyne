#
# expand_paths.py <Peter.Bienstman@UGent.be>
#

import sys

from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.utils import expand_path


class ExpandPaths(Filter):

    """Fill out relative paths for src tags (e.g. img src or sound src)."""

    def run(self, text, card, fact_key, **render_args):
        i = text.lower().find("src")
        while i != -1:
            start = text.find("\"", i)
            end = text.find("\"", start + 1)
            if start == -1 or end == -1:
                break
            old_path = text[start+1:end]
            new_path = expand_path(old_path, self.database().media_dir())
            if sys.platform == "win32":
                new_path = "/" + new_path.replace("\\", "/")
            text = text[:start+1] + "file://" + new_path + text[end:]
            # Since text is always longer now, we can start searching
            # from the previous end tag.
            i = text.lower().find("src", end + 1)
        return text
