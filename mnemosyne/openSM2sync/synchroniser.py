#
# synchroniser.py - Max Usachev <maxusachev@gmail.com>
#                   Ed Bartosh <bartosh@gmail.com>
#                   Peter Bienstman <Peter.Bienstman@UGent.be>

from xml.sax import saxutils
from xml.etree import cElementTree
from openSM2sync.log_entry import LogEntry, EventTypes

PROTOCOL_VERSION = 1.0

QA_CARD_TYPE = 1
VICE_VERSA_CARD_TYPE = 2
N_SIDED_CARD_TYPE = 3

class SyncError(Exception):
    pass

            
class Synchroniser:
    
    """Class handling the conversion from LogEntry objects to XML streams and
    vice versa.

    """

    # The list of keys to be passed on as attributes.
    keys_in_attribs = ["type", "time", "o_id", "sch", "n_mem", "act"]
    int_keys = ["type", "time", "sch", "n_mem", "act"]
    
    def __init__(self):
        self.partner = {"id": None, "program_name": None,
            "program_version": None, "protocol_version": None,
            "capabilities": None, "database_name": None,
            "server_deck_read_only": None, "server_allows_media_upload": None}

    def set_partner_params(self, partner_params):
        params = cElementTree.fromstring(partner_params) 
        for key in params.keys():
            value = params.get(key)
            if value == "true":
                value = True
            if value == "false":
                value = False
            self.partner[key] = value

    def log_entry_to_XML(self, log_entry):

        """Note that this function should return a regular string, not a
        unicode object, as unicode is not supported by the html standard.

        """
        
        attribs, tags = "", ""
        for key, value in log_entry.iteritems():
            if key in self.keys_in_attribs:
                attribs += " %s='%s'" % (key, value)
            else:
                tags += "<%s>%s</%s>" % (key, saxutils.escape(value), key)
        xml = "<log%s>%s</log>" % (attribs, tags)
    
        import sys
        sys.stderr.write(xml.encode("utf-8") + "\n")
        
        return xml.encode("utf-8")

    def XML_to_log_entry(self, chunk):
        xml = cElementTree.XML(chunk)
        log_entry = LogEntry()
        for key, value in xml.attrib.iteritems():
            if key in self.int_keys:
                value = int(value)
            log_entry[key] = value
        for child in xml:
            log_entry[child.tag] = child.text
        return log_entry
        
    def create_media_xml_element(self, log_entry):
        import os
        fname = log_entry["id"].split("__for__")[0]
        if os.path.exists(os.path.join(self.mediadir, fname)):
            return "<i><t>media</t><ev>%s</ev><id>%s</id></i>" % \
                (log_entry["log_entry"], log_entry["id"])
        else:
            return ""

    def apply_media(self, history, media_count):
        count = 0
        hsize = float(media_count)
        self.ui.show_progressbar()
        for child in cElementTree.fromstring(history):
            self.get_media(child.find("id").text.split("__for__")[0])
            count += 1
            self.ui.update_progressbar(count / hsize)
        self.ui.hide_progressbar()



