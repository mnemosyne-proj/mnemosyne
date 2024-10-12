#
# cuecard_wcu.py  Chris Aakre <caaakre@gmail.com>, <Peter.Bienstman@gmail.com>
#

from xml.etree import cElementTree

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.file_format import FileFormat
from mnemosyne.libmnemosyne.file_formats.media_preprocessor \
    import MediaPreprocessor


class CuecardWcu(FileFormat, MediaPreprocessor):

    description = _("Cuecard .wcu")
    extension = ".wcu"
    filename_filter = _("Cuecard files (*.wcu *.WCU)")
    import_possible = True
    export_possible = False

    def __init__(self, component_manager):
        FileFormat.__init__(self, component_manager)
        MediaPreprocessor.__init__(self, component_manager)

    def do_import(self, filename, extra_tag_names=""):
        FileFormat.do_import(self, filename, extra_tag_names)
        w = self.main_widget()
        try:
            tree = cElementTree.parse(filename)
        except cElementTree.ParseError as e:
            w.show_error(_("Unable to parse file:") + str(e))
            return
        card_type = self.card_type_with_id("1")
        tag_names = [tag_name.strip() for \
            tag_name in extra_tag_names.split(",") if tag_name.strip()]
        for element in tree.getroot().findall("Card"):
            fact_data = {"f": element.attrib["Question"],
                "b": element.attrib["Answer"]}
            self.preprocess_media(fact_data, tag_names)
            card = self.controller().create_new_cards(fact_data, card_type,
                grade=-1, tag_names=tag_names,
                check_for_duplicates=False, save=False)[0]
            if _("MISSING_MEDIA") in tag_names:
                tag_names.remove(_("MISSING_MEDIA"))
        self.warned_about_missing_media = False
