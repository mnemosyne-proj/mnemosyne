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
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            self.partner[key] = value

    def log_entry_to_XML(self, log_entry):

        """Converts LogEntry to XML.

        For efficiency reasons we require tag names and attribute values to be
        useable without escaping them with saxutils.quoteattr, so they should
        not contain <, >, &, ... .

        Note that the returned XML is a unicode object, and in order to send it
        across a socket e.g., we still need to encode it first.
        
        """
        
        attribs, tags = "", ""
        for key, value in log_entry.iteritems():
            if key in self.keys_in_attribs:
                attribs += " %s='%s'" % (key, value)
            else:    
                tags += "<%s>%s</%s>" % (key, saxutils.escape(value), key)
        xml = "<log%s>%s</log>" % (attribs, tags)
        import sys; sys.stderr.write(xml.encode("utf-8") + "\n")
        return xml

    def XML_to_log_entry(self, chunk):

        # TODO: remove
        
        #import sys; sys.stderr.write(chunk)
        xml = cElementTree.XML(chunk)
        log_entry = LogEntry()
        for key, value in xml.attrib.iteritems():
            if key in self.int_keys:
                value = int(value)
            elif key in self.float_keys:
                values = float(value)
            log_entry[key] = value
        for child in xml:
            if child.text:
                log_entry[child.tag] = child.text
            else:
                log_entry[child.tag] = "" # Should be string instead of None.
        return log_entry

    def XML_to_log_entries(self, xml):
        # Do incremental parsing of the xml stream.
        context = iter(cElementTree.iterparse(xml, events=("start", "end")))
        # Get the root element
        event, root = context.next()
        for event, elem in context:
            if event == "end":
                log_entry = LogEntry()

                for key, value in elem.attrib.iteritems():
                    if key in self.int_keys:
                        value = int(value)
                    elif key in self.float_keys:
                        values = float(value)
                    log_entry[key] = value
                for child in elem:
                    print 'child', child
                    if child.text:
                        log_entry[child.tag] = child.text
                    else:
                        log_entry[child.tag] = "" # Should be string instead of None.
                
                print elem
                print elem.attrib.iteritems()
                print log_entry
                # Free memory.
                root.clear()
                yield log_entry
