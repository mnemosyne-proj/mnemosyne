#
# expand_paths.py <Peter.Bienstman@gmail.com>
#

import sys

from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.utils import expand_path


class ExpandPaths(Filter):

    """Fill out relative paths for src tags (e.g. img src or sound src)."""

    def run(self, text, card, fact_key, **render_args):
        text = self.expand_tag("src", text)
        text = self.expand_tag("data", text) # For Flash.
        return text

    def expand_tag(self, tag, text):
        # Add "=" to make sure we don't match "Application Data".
        i = text.lower().find(tag + "=")
        while i != -1:
            start = text.find("\"", i)
            end = text.find("\"", start + 1)
            if start == -1 or end == -1:
                break
            if len(text[i:start].replace(" ", "")) > len(tag) + 1:
                break
            old_path = text[start+1:end]
            if not old_path.startswith("http:"):
                new_path = expand_path(old_path, self.database().media_dir())
                if sys.platform == "win32":
                    new_path = "/" + new_path.replace("\\", "/")
                new_path = new_path.replace("#", "%23")
                if sys.platform != "win32" or tag != "data":
                    new_path = "file://" + new_path
                text = text[:start+1] + new_path + text[end:]
                end = start + len(new_path)
            # Since text is always longer now, we can start searching
            # from the previous end tag.
            i = text.lower().find(tag, end + 1)
        # Replace code word 'db_media:///' by the absolute path for use e.g.
        # in javascript.
        if "db_media:///" in text:
            text = text.replace("db_media:///", 
                self.database().media_dir().replace("\\", "/") + "/")
        return text
