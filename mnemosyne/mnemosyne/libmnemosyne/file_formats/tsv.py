#
# tsv.py <Peter.Bienstman@UGent.be>
#

import re

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import MnemosyneError
from mnemosyne.libmnemosyne.file_format import FileFormat
from mnemosyne.libmnemosyne.file_formats.media_preprocessor \
    import MediaPreprocessor

re0 = re.compile(r"&#(.+?);", re.DOTALL | re.IGNORECASE)


class Tsv(FileFormat, MediaPreprocessor):

    """Question and answers on a single line, separated by tabs.
    Or, for three-sided cards: foreign word, pronunciation, meaning,
    separated by tabs.

    """

    description = _("Tab-separated text files")
    filename_filter = _("Tab-separated text files (*.txt)")
    import_possible = True
    export_possible = False

    def __init__(self, component_manager):
        FileFormat.__init__(self, component_manager)
        MediaPreprocessor.__init__(self, component_manager)

    def do_import(self, filename, extra_tag_name=None):
        card_type_1 = self.card_type_with_id("1")
        card_type_3 = self.card_type_with_id("3")
        # Open txt file.
        f = None
        try:
            f = file(filename)
        except:
            try:
                f = file(filename.encode("latin"))
            except:
                self.main_widget().show_error(_("Could not load file."))
                raise MnemosyneError
        # Parse txt file.
        self.database().add_savepoint("import")
        for line in f:
            try:
                line = unicode(line, "utf-8")
            except:
                try:
                    line = unicode(line, "latin")
                except:
                    self.main_widget().show_error(\
                        _("Could not determine encoding."))
                    raise MnemosyneError
            line = line.rstrip()
            # Parse html style escaped unicode (e.g. &#33267;).
            for match in re0.finditer(s):
                # Integer part.
                u = unichr(int(match.group(1)))
                # Integer part with &# and ;.
                line = line.replace(match.group(), u)
            if len(line) == 0:
                continue
            if line[0] == u"\ufeff": # Remove byte-order mark.
                line = line[1:]
            fields = line.split("\t")
            # Vocabulary card.
            if len(fields) >= 3:
                fact_data = {"f": fields[0], "p_1": fields[1],
                    "m_1": fields[2]}
                self.preprocess_media(fact_data, [extra_tag_name])
                self.controller().create_new_cards(fact_data,
                    card_type_3, grade=-1, tag_names=[extra_tag_name],
                    check_for_duplicates=False, save=False)
            # Front-to-back only.
            elif len(fields) == 2:
                fact_data = {"f": fields[0], "b": fields[1]}
                self.preprocess_media(fact_data, [extra_tag_name])
                self.controller().create_new_cards(fact_data,
                    card_type_1, grade=-1, tag_names=[extra_tag_name],
                    check_for_duplicates=False, save=False)
            # Malformed line.
            else:
                self.main_widget().show_error(\
                    _("Missing answer on line:\n") + line)
                self.database().rollback_to_savepoint("import")
                raise MnemosyneError


