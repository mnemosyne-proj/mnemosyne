#
# mnemosyne2_cards.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import time
import codecs
import zipfile
import cPickle

from openSM2sync.log_entry import LogEntry
from openSM2sync.log_entry import EventTypes
from openSM2sync.text_formats.xml_format import XMLFormat

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import MnemosyneError
from mnemosyne.libmnemosyne.file_format import FileFormat


class Mnemosyne2Cards(FileFormat):

    description = _("Mnemosyne 2.x *.cards files")
    extension = ".cards"
    filename_filter = _("Mnemosyne 2.x cards for sharing (*.cards)")
    import_possible = True
    export_possible = True

    def do_export(self, filename, export_learning_data=False):
        # export_learning_data=True is only used internally when merging
        # databases.
        self.orig_dir = os.getcwd()
        if not os.path.isabs(filename):
            filename = os.path.join(self.config()["export_dir"], filename)
        os.chdir(os.path.dirname(filename))
        if export_learning_data is True:
            metadata = {}
        else:
            metadata = self.controller().show_export_metadata_dialog()
        if metadata is None:  # Cancelled.
            os.chdir(self.orig_dir)
            return -1
        metadata_file = file("METADATA", "w")
        for key, value in metadata.iteritems():
            print >> metadata_file, key + ":" + \
                value.strip().replace("\n", "<br>").encode("utf-8")
        metadata_file.close()
        db = self.database()
        w = self.main_widget()
        # Generate log entries.
        w.set_progress_text(_("Exporting cards..."))
        active_objects = db.active_objects_to_export()
        number_of_entries = len(active_objects["tags"]) + \
            len(active_objects["fact_view_ids"]) + \
            len(active_objects["card_type_ids"]) + \
            len(active_objects["media_filenames"]) + \
            len(active_objects["_card_ids"]) + \
            len(active_objects["_fact_ids"])
        xml_file = file("cards.xml", "w")
        xml_format = XMLFormat()
        xml_file.write(xml_format.log_entries_header(number_of_entries))
        w.set_progress_range(number_of_entries)
        w.set_progress_update_interval(number_of_entries/20)
        for tag in active_objects["tags"]:
            log_entry = LogEntry()
            log_entry["type"] = EventTypes.ADDED_TAG
            log_entry["o_id"] = tag.id
            log_entry["name"] = tag.name
            xml_file.write(xml_format.\
                repr_log_entry(log_entry).encode("utf-8"))
            w.increase_progress(1)
        for fact_view_id in active_objects["fact_view_ids"]:
            fact_view = db.fact_view(fact_view_id, is_id_internal=False)
            log_entry = LogEntry()
            log_entry["type"] = EventTypes.ADDED_FACT_VIEW
            log_entry["o_id"] = fact_view.id
            log_entry["name"] = fact_view.name
            log_entry["q_fact_keys"] = repr(fact_view.q_fact_keys)
            log_entry["a_fact_keys"] = repr(fact_view.a_fact_keys)
            log_entry["q_fact_key_decorators"] = \
                repr(fact_view.q_fact_key_decorators)
            log_entry["a_fact_key_decorators"] = \
                repr(fact_view.a_fact_key_decorators)
            log_entry["a_on_top_of_q"] = repr(fact_view.a_on_top_of_q)
            log_entry["type_answer"] = repr(fact_view.type_answer)
            if fact_view.extra_data:
                log_entry["extra"] = repr(fact_view.extra_data)
            xml_file.write(xml_format.\
                repr_log_entry(log_entry).encode("utf-8"))
            w.increase_progress(1)
        for card_type_id in active_objects["card_type_ids"]:
            card_type = db.card_type(card_type_id, is_id_internal=False)
            log_entry = LogEntry()
            log_entry["type"] = EventTypes.ADDED_CARD_TYPE
            log_entry["o_id"] = card_type.id
            log_entry["name"] = card_type.name
            log_entry["fact_keys_and_names"] = \
                repr(card_type.fact_keys_and_names)
            log_entry["fact_views"] = repr([fact_view.id for fact_view \
                in card_type.fact_views])
            log_entry["unique_fact_keys"] = \
                repr(card_type.unique_fact_keys)
            log_entry["required_fact_keys"] = \
                repr(card_type.required_fact_keys)
            log_entry["keyboard_shortcuts"] = \
                repr(card_type.keyboard_shortcuts)
            if card_type.extra_data:
                log_entry["extra"] = repr(card_type.extra_data)
            xml_file.write(xml_format.\
                repr_log_entry(log_entry).encode("utf-8"))
            w.increase_progress(1)
        for media_filename in active_objects["media_filenames"]:
            log_entry = LogEntry()
            log_entry["type"] = EventTypes.ADDED_MEDIA_FILE
            log_entry["fname"] = media_filename
            xml_file.write(xml_format.\
                repr_log_entry(log_entry).encode("utf-8"))
            w.increase_progress(1)
        for _fact_id in active_objects["_fact_ids"]:
            fact = db.fact(_fact_id, is_id_internal=True)
            log_entry = LogEntry()
            log_entry["type"] = EventTypes.ADDED_FACT
            log_entry["o_id"] = fact.id
            for fact_key, value in fact.data.iteritems():
                log_entry[fact_key] = value
            xml_file.write(xml_format.\
                repr_log_entry(log_entry).encode("utf-8"))
            w.increase_progress(1)
        for _card_id in active_objects["_card_ids"]:
            card = db.card(_card_id, is_id_internal=True)
            log_entry = LogEntry()
            log_entry["type"] = EventTypes.ADDED_CARD
            log_entry["o_id"] = card.id
            log_entry["card_t"] = card.card_type.id
            log_entry["fact"] = card.fact.id
            log_entry["fact_v"] = card.fact_view.id
            log_entry["tags"] = ",".join([tag.id for tag in card.tags])
            if export_learning_data:
                log_entry["gr"] = card.grade
                log_entry["e"] = card.easiness
                log_entry["ac_rp"] = card.acq_reps
                log_entry["rt_rp"] = card.ret_reps
                log_entry["lps"] = card.lapses
                log_entry["ac_rp_l"] = card.acq_reps_since_lapse
                log_entry["rt_rp_l"] = card.ret_reps_since_lapse
                log_entry["l_rp"] = card.last_rep
                log_entry["n_rp"] = card.next_rep                
            else:
                log_entry["gr"] = -1
                log_entry["e"] = 2.5
                log_entry["ac_rp"] = 0
                log_entry["rt_rp"] = 0
                log_entry["lps"] = 0
                log_entry["ac_rp_l"] = 0
                log_entry["rt_rp_l"] = 0
                log_entry["l_rp"] = -1
                log_entry["n_rp"] = -1
            if card.extra_data:
                log_entry["extra"] = repr(card.extra_data)
            xml_file.write(xml_format.\
                repr_log_entry(log_entry).encode("utf-8"))
            w.increase_progress(1)
        xml_file.write(xml_format.log_entries_footer())
        xml_file.close()
        # Make archive (Zipfile requires a .zip extension).
        zip_file = zipfile.ZipFile(filename + ".zip", "w",
            compression=zipfile.ZIP_DEFLATED)
        zip_file.write("cards.xml")
        zip_file.write("METADATA")
        w.close_progress()
        w.set_progress_text(_("Bundling media files..."))
        number_of_media_files = len(active_objects["media_filenames"])
        w.set_progress_range(number_of_media_files)
        w.set_progress_update_interval(number_of_media_files/100)
        for media_filename in active_objects["media_filenames"]:
            full_path = os.path.normpath(\
                os.path.join(self.database().media_dir(), media_filename))
            if not os.path.exists(full_path):
                self.main_widget().show_error(\
                _("Missing filename: " + full_path))
                continue
            zip_file.write(full_path, media_filename,
                compress_type=zipfile.ZIP_STORED)
            w.increase_progress(1)
        zip_file.close()
        if os.path.exists(filename):
            os.remove(filename)
        os.rename(filename + ".zip", filename)
        os.remove("cards.xml")
        os.remove("METADATA")
        os.chdir(self.orig_dir)
        w.close_progress()

    def do_import(self, filename, extra_tag_names=None, show_metadata=True):
        FileFormat.do_import(self, filename, extra_tag_names)
        if not extra_tag_names:
            extra_tags = []
        else:
            extra_tags = [self.database().get_or_create_tag_with_name(\
                tag_name.strip()) for tag_name in extra_tag_names.split(",")]
        self.database().set_extra_tags_on_import(extra_tags)
        w = self.main_widget()
        w.set_progress_text(_("Importing cards..."))
        # Extract zipfile.
        zip_file = zipfile.ZipFile(filename, "r")
        zip_file.extractall(self.database().media_dir())
        # Show metadata.            
        metadata_filename = os.path.join(\
                self.database().media_dir(), "METADATA")
        if show_metadata:
            metadata = {}
            for line in file(metadata_filename):
                key, value = line.split(":", 1)
                metadata[key] = value.replace("<br>", "\n")
            self.controller().show_export_metadata_dialog(metadata, read_only=True)
        # Parse XML.
        self.database().card_types_to_instantiate_later = set()
        xml_filename = os.path.join(self.database().media_dir(), "cards.xml")
        element_loop = XMLFormat().parse_log_entries(file(xml_filename, "r"))
        number_of_entries = int(element_loop.next())
        if number_of_entries == 0:
            return
        w.set_progress_range(number_of_entries)
        w.set_progress_update_interval(number_of_entries/20)
        for log_entry in element_loop:
            self.database().apply_log_entry(log_entry, importing=True)
            w.increase_progress(1)
        w.set_progress_value(number_of_entries)
        if len(self.database().card_types_to_instantiate_later) != 0:
            raise RuntimeError, _("Missing plugins for card types.")
        os.remove(xml_filename)
        os.remove(metadata_filename)
        w.close_progress()
