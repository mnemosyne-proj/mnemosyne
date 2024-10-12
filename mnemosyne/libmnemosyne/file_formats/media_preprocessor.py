#
# media_preprocessor.py <Peter.Bienstman@gmail.com>
#

import os
import re

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import MnemosyneError, expand_path, copy

re_src = re.compile(r"""src=\"(.+?)\"""", re.DOTALL | re.IGNORECASE)
re_sound = re.compile(r"""<sound src=\".+?\">""", re.DOTALL | re.IGNORECASE)


class MediaPreprocessor(Component):

    def __init__(self, component_manager):
        Component.__init__(self, component_manager)
        self.warned_about_missing_media = False

    def preprocess_media(self, fact_data, tag_names):
        missing_media = False
        media_dir = self.database().media_dir()
        # os.path.normpath does not convert Windows separators to Unix
        # separators, so we need to make sure we internally store Unix paths.
        for fact_key in fact_data:
            for match in re_src.finditer(fact_data[fact_key]):
                fact_data[fact_key] = \
                    fact_data[fact_key].replace(match.group(),
                    match.group().replace("\\", "/"))
        # Convert sound tags to audio tags.
        for fact_key in fact_data:
            for match in re_sound.finditer(fact_data[fact_key]):
                fact_data[fact_key] = fact_data[fact_key].replace(match.group(),
                    match.group().replace("<sound src", "<audio src"))
        # Copy files to media directory, creating subdirectories as we go.
        # For missing media, we change the tag to scr_missing, which makes it
        # easier for the user to identify the problem if there is more than 1
        # media file missing for a card.
        for fact_key in fact_data:
            for match in re_src.finditer(fact_data[fact_key]):
                filename = match.group(1)
                if not os.path.exists(filename) \
                    and not os.path.exists(\
                        expand_path(filename, self.import_dir)) \
                    and not os.path.exists(\
                        expand_path(filename, self.database().media_dir())):
                    fact_data[fact_key] = \
                        fact_data[fact_key].replace(match.group(),
                        "src_missing=\"%s\"" % filename)
                    missing_media = True
                    continue
                if not os.path.isabs(filename) and not os.path.exists(\
                        expand_path(filename, self.database().media_dir())):
                    source = expand_path(filename, self.import_dir)
                    dest = expand_path(filename, media_dir)
                    directory = os.path.dirname(dest)
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    copy(source, dest)
        if missing_media:
            tag_names.append(_("MISSING_MEDIA"))
            if not self.warned_about_missing_media:
                self.main_widget().show_information(\
 _("Warning: media files were missing. These cards have been tagged as MISSING_MEDIA. You must also change 'src_missing' to 'src' in the text of these cards."))
                self.warned_about_missing_media = True
