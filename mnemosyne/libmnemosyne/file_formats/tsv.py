#
# tsv.py <Peter.Bienstman@gmail.com>
#

import os
import re

from mnemosyne.libmnemosyne.gui_translator import _
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
    extension = ".txt"
    filename_filter = _("Tab-separated text files (*.txt *.tsv *.tab)")
    import_possible = True
    export_possible = True

    def __init__(self, component_manager):
        FileFormat.__init__(self, component_manager)
        MediaPreprocessor.__init__(self, component_manager)

    def do_import(self, filename, extra_tag_names=""):
        FileFormat.do_import(self, filename, extra_tag_names)
        try:
            f = open(filename, encoding="utf-8")
        except:
            self.main_widget().show_error(_("Could not load file."))
            return
        facts_data = []
        line_number = 0
        for line in f:
            line_number += 1
            line = line.rstrip()
            # Parse html style escaped unicode (e.g. &#33267;).
            for match in re0.finditer(line):
                # Integer part.
                escaped = match.group(1)
                if escaped[0] == "x":
                    escaped = "0" + escaped
                if "x" in escaped:
                    u = chr(int(escaped, 16))
                else:
                    u = chr(int(escaped))
                # Integer part with &# and ;.
                line = line.replace(match.group(), u)
            if len(line) == 0:
                continue
            if line[0] == "\\ufeff": # Remove byte-order mark.
                line = line[1:]
            fields = line.split("\t")
            if len(fields) >= 3:  # Vocabulary card.
                if len(fields) >= 4:
                    if not fields[0] or not fields[2]:
                        self.main_widget().show_error(\
                            _("Required field missing on line") \
                            + " " + str(line_number) + ":\n" + line)
                        return
                    facts_data.append({"f": fields[0], "p_1": fields[1],
                        "m_1": fields[2], "n": fields[3]})
                else:
                    facts_data.append({"f": fields[0], "p_1": fields[1],
                        "m_1": fields[2]})
            elif len(fields) == 2:  # Front-to-back only.
                if not fields[0] :
                    self.main_widget().show_error(\
                        _("Required field missing on line") \
                        + " " + str(line_number) + ":\n" + line)
                    return
                facts_data.append({"f": fields[0], "b": fields[1]})
            else:  # Malformed line.
                self.main_widget().show_error(_("Badly formed input on line") \
                    + " " + str(line_number) + ":\n" + line)
                return
        # Now that we know all the data is well-formed, create the cards.
        tag_names = [tag_name.strip() for \
            tag_name in extra_tag_names.split(",") if tag_name.strip()]
        for fact_data in facts_data:
            if len(list(fact_data.keys())) == 2:
                card_type = self.card_type_with_id("1")
            else:
                card_type = self.card_type_with_id("3")
            self.preprocess_media(fact_data, tag_names)
            self.controller().create_new_cards(fact_data, card_type, grade=-1,
                tag_names=tag_names, check_for_duplicates=False, save=False)
            if _("MISSING_MEDIA") in tag_names:
                tag_names.remove(_("MISSING_MEDIA"))
        self.warned_about_missing_media = False

    def process_string_for_text_export(self, text):
        text = text.replace("\n", "<br>").replace("\t", " ")
        if text == "":
            text = "<br>"
        return text

    def do_export(self, filename):
        if not os.path.isabs(filename):
            filename = os.path.join(self.config()["export_dir"], filename)
        db = self.database()
        w = self.main_widget()
        w.set_progress_text(_("Exporting cards..."))
        number_of_cards = db.active_count()
        w.set_progress_range(number_of_cards)
        w.set_progress_update_interval(number_of_cards/50)
        outfile = open(filename, "w", encoding="utf-8")
        for _card_id, _fact_id in db.active_cards():
            card = db.card(_card_id, is_id_internal=True)
            q = self.process_string_for_text_export(\
                card.question(render_chain="plain_text"))
            a = self.process_string_for_text_export(\
                card.answer(render_chain="plain_text"))
            outfile.write("%s\t%s\n" % (q, a))
            w.increase_progress(1)
        w.close_progress()

