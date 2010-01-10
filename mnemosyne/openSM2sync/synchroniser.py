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

            
class Synchroniser(object):
    
    """Class handling the conversion from LogEntry objects to XML streams and
    vice versa.

    """

    # The list of keys to be passed on as attributes.
    keys_in_attribs = ["type", "time", "o_id", "sch", "n_mem", "act", "c_time",
        "m_time", "card_t", "fact", "fact_v", "tags", "act", "gr", "e", "l_rp",
        "n_rp", "ac_rp", "rt_rp", "lps", "ac_rp_l", "rt_rp_l", "sch_data",
        "sch_i", "act_i", "new_i", "th_t"]
    int_keys = ["type", "time", "sch", "n_mem", "act", "c_time", "m_time",
        "act", "gr", "l_rp", "n_rp", "ac_rp", "rt_rp", "lps", "ac_rp_l",
        "rt_rp_l", "sch_data", "sch_i", "act_i", "new_i", "th_t"]
    float_keys = ["e"]

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
            elif key in self.float_keys:
                values = float(value)
            log_entry[key] = value
        for child in xml:
            log_entry[child.tag] = child.text
        return log_entry
