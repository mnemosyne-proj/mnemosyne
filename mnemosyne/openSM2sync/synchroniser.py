#
# synchroniser.py - Max Usachev <maxusachev@gmail.com>
#                   Ed Bartosh <bartosh@gmail.com>
#                   Peter Bienstman <Peter.Bienstman@UGent.be>

from xml.etree import cElementTree
from openSM2sync.log_entry import LogEntry, EventTypes

PROTOCOL_VERSION = 1.0

QA_CARD_TYPE = 1
VICE_VERSA_CARD_TYPE = 2
N_SIDED_CARD_TYPE = 3

class SyncError(Exception):
    pass

class DictClass:
    def __init__(self, attributes=None):
        for attr in attributes.keys():
            setattr(self, attr, attributes[attr])
            
class Synchroniser:
    
    """Class handling the conversion from LogEntry objects to XML streams and
    vice versa.

    """
    
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
        
        chunk = """<log type="%d" time="%d" o_id="%s\"""" % \
            (log_entry.event_type, log_entry.timestamp, log_entry.object_id)
        for key, value in log_entry.data.iteritems():
            chunk += """ %s="%s\"""" % (key, value)
        chunk += "></log>"
        import sys
        sys.stderr.write("O" + chunk + "\n")
        
        return chunk.encode("utf-8")

    def XML_to_log_entry(self, chunk):
        chunk = chunk.decode("utf-8")
        
        import sys
        sys.stderr.write("I" + chunk)
        
        attrib = cElementTree.fromstring(chunk).attrib
        log_entry = LogEntry()
        log_entry.event_type = attrib["type"]
        log_entry.time_stamp = int(attrib["time"])
        log_entry.object_id = attrib["o_id"]
        
    def create_fact_xml_element(self, log_entry):
        if log_entry["log_entry"] == EventTypes.DELETED_FACT:
            # We only transfer fact id, that should be deleted.
            return "<i><t>fact</t><ev>%s</ev><id>%s</id></i>" % \
                (log_entry["log_entry"], log_entry["id"])
        fact = self.database.get_fact(log_entry["id"], False)
        if not fact:
            return ""
        else:
            dkeys = ",".join(["%s" % key for key, val in fact.data.items()])
            dvalues = "".join(["<dv%s><![CDATA[%s]]></dv%s>" % (num, \
            fact.data.values()[num], num) for num in range(len(fact.data))])
            return "<i><t>fact</t><ev>%s</ev><id>%s</id><ctid>%s</ctid><dk>" \
                "%s</dk>%s<tm>%s</tm></i>" % (log_entry["log_entry"], fact.id, \
                fact.card_type.id, dkeys, dvalues, log_entry["time"])

    def create_card_xml_element(self, log_entry):
        if log_entry["log_entry"] == EventTypes.DELETED_CARD:
            # We only transfer card id, that should be deleted.
            return "<i><t>card</t><ev>%s</ev><id>%s</id></i>" % \
                (log_entry["log_entry"], log_entry["id"])
        card = self.database.get_card(log_entry["id"], False)
        return "<i><t>card</t><ev>%s</ev><id>%s</id><ctid>%s</ctid><fid>" \
            "%s</fid><fvid>%s</fvid><tags>%s</tags><gr>%s</gr><e>%s</e>" \
            "<lr>%s</lr><nr>%s</nr><si>%s</si><ai>%s</ai><ni>%s</ni>" \
            "<ttm>%s</ttm><tm>%s</tm><_id>%s</_id></i>" % (log_entry["log_entry"], \
            card.id, card.fact.card_type.id, card.fact.id, \
            card.fact_view.id, ",".join([item.name for item in card.tags]),\
            card.grade, card.easiness, card.last_rep, card.next_rep, \
            log_entry["s_int"], log_entry["a_int"], log_entry["n_int"], \
            log_entry["t_time"], log_entry["time"], card._id)
        
    def create_card_type_xml_element(self, log_entry):
        cardtype = self.database.get_card_type(log_entry["id"], False)
        fields = [key for key, value in cardtype.fields]
        return "<i><t>ctype</t><ev>%s</ev><id>%s</id><name>%s</name><f>%s</f>"\
        "<uf>%s</uf><ks>%s</ks><edata>%s</edata></i>" % (log_entry["log_entry"], \
        cardtype.id, cardtype.name, ",".join(fields), \
        ",".join(cardtype.unique_fields), "", "")

    def create_media_xml_element(self, log_entry):
        import os
        fname = log_entry["id"].split("__for__")[0]
        if os.path.exists(os.path.join(self.mediadir, fname)):
            return "<i><t>media</t><ev>%s</ev><id>%s</id></i>" % \
                (log_entry["log_entry"], log_entry["id"])
        else:
            return ""

    def create_tag_object(self, item):
        from mnemosyne.libmnemosyne.tag import Tag       
        return Tag(item.find("name").text, item.find("id").text)

    def create_fact_object(self, item):
        from mnemosyne.libmnemosyne.fact import Fact
        dkeys = item.find("dk").text.split(",")
        dvals = [item.find("dv%s" % num).text for num in range(len(dkeys))]
        fact_data = dict([(key, dvals[dkeys.index(key)]) for key in dkeys])
        card_type = self.database.get_card_type(\
            item.find("ctid").text, False)
        creation_time = int(item.find("tm").text)
        fact_id = item.find("id").text
        fact = Fact(fact_data, card_type, creation_time, fact_id)
        return fact

    def create_card_object(self, item):
        
        def get_rep_value(value):
            
            """Return value for repetition log_entry."""
            
            if value == "None":
                return ""
            else:
                return int(value)
            
        return DictClass({"id": item.find("id").text, "fact_view": DictClass(\
            {"id": item.find("fvid").text}), "fact": self.database.get_fact(\
            item.find("fid").text, False), "tags": set(self.database.\
            get_or_create_tag_with_name(tag_name) for tag_name in item.find(\
            "tags").text.split(",")), "grade": int(item.find("gr").text), \
            "easiness": float(item.find("e").text), "acq_reps": 0, "ret_reps": \
            0, "lapses": 0, "acq_reps_since_lapse": 0, "ret_reps_since_lapse": \
            0, "last_rep": int(item.find("lr").text), "next_rep": int(\
            item.find("nr").text), "extra_data": 0, "scheduler_data": 0, \
            "active": True, "in_view": True, "timestamp": int(item.find(\
            "tm").text), "scheduled_interval": get_rep_value(item.find(\
            "si").text), "actual_interval": get_rep_value(item.find(\
            "ai").text), "new_interval": get_rep_value(item.find("ni").text), \
            "thinking_time": get_rep_value(item.find("ttm").text), "_id": \
            item.find("_id").text})

    def create_cardtype_object(self, item):
        return DictClass({"id": item.find("id").text, "name": \
            item.find("name").text, "fields": item.find("f").text.split(","), \
            "keyboard_shortcuts": {}, "extra_data": {}, "unique_fields": \
            item.find("uf").text.split(",")})

    def create_media_object(self, item):
        return None

    def apply_media(self, history, media_count):
        count = 0
        hsize = float(media_count)
        self.ui.show_progressbar()
        for child in cElementTree.fromstring(history):
            self.get_media(child.find("id").text.split("__for__")[0])
            count += 1
            self.ui.update_progressbar(count / hsize)
        self.ui.hide_progressbar()



