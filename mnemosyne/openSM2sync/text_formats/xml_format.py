#
# xml_format.py <Peter.Bienstman@UGent.be>
#

from xml.sax import saxutils
from xml.etree import cElementTree
from openSM2sync.log_entry import LogEntry

PROTOCOL_VERSION = "openSM2sync 1.0"

              
class XMLFormat(object):
    
    """Class handling the conversion from data to XML streams and vice versa.

    Example of typical XML for log entries:

    <openSM2sync number_of_entries='5'>
    <log type='1' o_id='Mnemosyne 2.0-pre posix linux2' time='1268213369'>
    </log>
    <log type='3' o_id='SM2 Mnemosyne' time='1268213369'></log>
    <log n_mem='0' act='0' type='4' sch='0' time='1268213369'></log>
    <log type='6' o_id='068c2472-b1f7-424d-aefa-ae723437702e'
    time='1268213369'><name>abcd</name></log>
    <log n_mem='0' act='0' type='5' sch='0' time='1268213369'></log>
    </openSM2sync>
    
    
    Note that the returned XML is a unicode object, and in order to send it
    across a socket e.g., we still need to encode it first.
        
    """

    def repr_partner_info(self, info):          
        repr_info = " <partner "
        for key, value in info.iteritems():
            repr_info += "%s='%s' " % (key, value)
        repr_info += "protocol_version='%s'></partner>" % (PROTOCOL_VERSION, )
        return repr_info

    def parse_partner_info(self, xml):
        parsed_xml = cElementTree.fromstring(xml)
        partner_info = {}
        for key in parsed_xml.keys():
            value = parsed_xml.get(key)
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            partner_info[key] = value
        return partner_info

    # The list of LogEntry keys to be passed on as attributes.
    keys_in_attribs = ["type", "time", "o_id", "sch", "n_mem", "c_time",
        "m_time", "card_t", "fact", "fact_v", "tags", "act", "gr", "e", "l_rp",
        "n_rp", "ac_rp", "rt_rp", "lps", "ac_rp_l", "rt_rp_l", "sch_data",
        "sch_i", "act_i", "new_i", "th_t"]
    int_keys = ["type", "time", "sch", "n_mem", "act", "c_time", "m_time",
        "act", "gr", "l_rp", "n_rp", "ac_rp", "rt_rp", "lps", "ac_rp_l",
        "rt_rp_l", "sch_data", "sch_i", "act_i", "new_i", "th_t"]
    float_keys = ["e"]

    def log_entries_header(self, number_of_entries):
        return "<openSM2sync number_of_entries='%d'>" % (number_of_entries, )

    def log_entries_footer(self):
        return "</openSM2sync>\n"    

    def repr_log_entry(self, log_entry):

        """Converts LogEntry to XML.

        For efficiency reasons we require tag names and attribute values to be
        useable without escaping them with saxutils.quoteattr, so they should
        not contain <, >, &, ... .
        
        """

        if log_entry is None:
            return ""
        attribs, tags = "", ""
        for key, value in log_entry.iteritems():
            if key in self.keys_in_attribs:
                attribs += " %s='%s'" % (key, value)
            else:    
                tags += "<%s>%s</%s>" % (key, saxutils.escape(value), key)
        xml = "<log%s>%s</log>" % (attribs, tags)
        #import sys; sys.stderr.write(xml.encode("utf-8") + "\n")
        return xml  # Don't add \n to improve throughput.

    def parse_log_entries(self, xml):

        """Do incremental parsing of the XML stream.

        See http://effbot.org/zone/element-iterparse.htm

        """
        
        context = iter(cElementTree.iterparse(xml, events=("start", "end")))
        event, root = context.next()  # 'start' event on openSM2 tag.
        for key, value in root.attrib.iteritems():
            if key == "number_of_entries":
                yield value 
        for event, elem in context:
            if event == "end" and elem.tag == "log":
                log_entry = LogEntry()
                for key, value in elem.attrib.iteritems():
                    if key in self.int_keys:
                        value = int(value)
                    elif key in self.float_keys:
                        values = float(value)
                    log_entry[key] = value
                for child in elem:
                    if child.text:
                        log_entry[child.tag] = child.text
                    else:
                        # Should be string instead of None.
                        log_entry[child.tag] = ""
                root.clear()  # Avoid taking up unnecessary memory.
                yield log_entry
