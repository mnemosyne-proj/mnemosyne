#
# xml_format.py <Peter.Bienstman@gmail.com>
#

from xml.sax import saxutils
from xml.etree import cElementTree
from openSM2sync.log_entry import LogEntry

PROTOCOL_VERSION = "openSM2sync 1.0   "


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

    mime_type = "text/xml"

    def repr_partner_info(self, info):
        repr_info = "<partner "
        for key, value in list(info.items()):
            if key.lower() == "partners":
                if value:
                    repr_info += "%s=%s " % \
                        (key, saxutils.quoteattr(",".join(value)))
            else:
                if type(value) != str and type(value) != str:
                    value = repr(value)
                repr_info += "%s=%s " % (key, saxutils.quoteattr(value))
        repr_info += "protocol_version=\"%s\"></partner>\n" \
            % (PROTOCOL_VERSION, )
        #import sys; sys.stderr.write(repr_info)
        return repr_info

    def parse_partner_info(self, xml):
        parsed_xml = cElementTree.fromstring(xml)
        partner_info = {}
        partner_info["partners"] = ()
        for key in list(parsed_xml.keys()):
            value = parsed_xml.get(key)
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            if key.lower() == "partners":
                value = value.split(",")
            partner_info[key] = value
        #import sys; sys.stderr.write(repr(partner_info))
        return partner_info

    # The list of LogEntry keys to be passed on as attributes.
    keys_in_attribs = ["type", "time", "o_id", "sch", "n_mem", "c_time",
        "m_time", "card_t", "fact", "fact_v", "tags", "act", "gr", "e", "l_rp",
        "n_rp", "ac_rp", "rt_rp", "lps", "ac_rp_l", "rt_rp_l", "sch_data",
        "sch_i", "act_i", "th_t"]
    int_keys = ["type", "time", "sch", "n_mem", "act", "c_time", "m_time",
        "act", "gr", "l_rp", "n_rp", "ac_rp", "rt_rp", "lps", "ac_rp_l",
        "rt_rp_l", "sch_data", "sch_i", "act_i", "th_t"]
    float_keys = ["e"]

    def log_entries_header(self, number_of_entries):
        return "<openSM2sync number_of_entries=\"%d\">" % (number_of_entries, )

    def log_entries_footer(self):
        return "</openSM2sync>\n"

    def repr_log_entry(self, log_entry):

        """Converts LogEntry to XML.

        For efficiency reasons we require tag names and attribute values to be
        useable without escaping them with saxutils.quoteattr, so they should
        not contain <, >, &, ... .

        We add an newline after each entry to improve parsing throughput
        (side effect of WSGI 1.x not supporting chunked requests).

        """

        if log_entry is None:
            # Dummy entries for card-based clients.
            return ""
        attribs, tags = "", ""
        for key, value in list(log_entry.items()):
            if key in self.keys_in_attribs:
                attribs += " %s=\"%s\"" % (key, value)
            else:
                # Anki keys can be numbers.
                if key[0].isdigit():
                    key = "___" + key
                tags += "<%s>%s</%s>" % (key, saxutils.escape(value), key)
        xml = "<log%s>%s</log>\n" % (attribs, tags)
        # Strip control characters.
        xml = "".join([i for i in xml if 31 < ord(i) or ord(i) in [9, 10, 13]])
        #import sys; sys.stderr.write(xml)
        return xml

    def parse_log_entries(self, xml):

        """Do incremental parsing of the XML stream.

        See http://effbot.org/zone/element-iterparse.htm

        """
        context = iter(cElementTree.iterparse(xml, events=("start", "end")))
        event, root = next(context)  # 'start' event on openSM2 tag.
        for key, value in list(root.attrib.items()):
            if key == "number_of_entries":
                yield value
        for event, element in context:
            if event == "end" and element.tag == "log":
                log_entry = LogEntry()
                for key, value in list(element.attrib.items()):
                    if key in self.int_keys:
                        value = int(value)
                    elif key in self.float_keys:
                        values = float(value)
                    log_entry[key] = value
                for child in element:
                    if child.tag.startswith("___"):  # Escaped number.
                        child.tag = child.tag[3:]
                    if child.text:
                        log_entry[child.tag] = child.text
                    else:
                        # Should be string instead of None.
                        log_entry[child.tag] = ""
                root.clear()  # Avoid taking up unnecessary memory.
                #import sys; sys.stderr.write(str(log_entry) + "\n")
                yield log_entry

    def repr_message(self, message, traceback=None):
        xml = "<openSM2sync message=\"%s\">" % (message, )
        if traceback:
            xml += "<traceback>%s</traceback>" % saxutils.escape(traceback)
        xml += "</openSM2sync>\n"
        return xml

    def parse_message(self, xml):
        element = cElementTree.XML(xml)
        message = element.attrib["message"]
        traceback = None
        if element.find("traceback") is not None:
            traceback = element.find("traceback").text
        return message, traceback

