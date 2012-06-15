#
# tsv.py <Peter.Bienstman@UGent.be>
#

import re

from mnemosyne.libmnemosyne.translator import _
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
        FileFormat.do_import(self, filename, extra_tag_name)
        # Open txt file. Use Universal line ending detection.
        f = None
        try:
            f = file(filename, "rU")
        except:
            try:
                f = file(filename.encode("latin", "rU"))
            except:
                self.main_widget().show_error(_("Could not load file."))
                return
        # Parse txt file.
        facts_data = []
        for line in f:
            try:
                line = unicode(line, "utf-8")
            except:
                try:
                    line = unicode(line, "latin")
                except:
                    self.main_widget().show_error(\
                        _("Could not determine encoding."))
                    return
            line = line.rstrip()
            # Parse html style escaped unicode (e.g. &#33267;).
            for match in re0.finditer(line):
                # Integer part.
                u = unichr(int(match.group(1)))
                # Integer part with &# and ;.
                line = line.replace(match.group(), u)
            if len(line) == 0:
                continue
            if line[0] == u"\ufeff": # Remove byte-order mark.
                line = line[1:]
            fields = line.split("\t")
            if len(fields) >= 3:  # Vocabulary card.
                facts_data.append({"f": fields[0], "p_1": fields[1],
                    "m_1": fields[2]})
            elif len(fields) == 2:  # Front-to-back only.
                facts_data.append({"f": fields[0], "b": fields[1]})
            else:  # Malformed line.
                self.main_widget().show_error(\
                    _("Missing answer on line:\n") + line)
                return
        # Now that we know all the data is well-formed, create the cards.
        tag_names = []
        if extra_tag_name:
            tag_names.append(extra_tag_name)
        for fact_data in facts_data:
            if len(fact_data.keys()) == 2:
                card_type = self.card_type_with_id("1")
            else:
                card_type = self.card_type_with_id("3")
            self.preprocess_media(fact_data, [extra_tag_name])
            self.controller().create_new_cards(fact_data, card_type, grade=-1,
                tag_names=tag_names, check_for_duplicates=False, save=False)

