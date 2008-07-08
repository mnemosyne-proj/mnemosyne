##############################################################################
#
# Mnemosyne_XML_Importer
#
##############################################################################

from xml.sax import saxutils, make_parser
from xml.sax.handler import feature_namespaces

class Mnemosyne_XML_Importer(saxutils.DefaultHandler):
    
    def __init__(self, default_cat=None, reset_learning_data=False):
        self.reading, self.text = {}, {}
        
        self.reading["cat"] = False
        self.reading["Q"]   = False
        self.reading["A"]   = False

        self.default_cat = default_cat
        self.reset_learning_data = reset_learning_data

        self.imported_cards = []

    def to_bool(self, string):
        if string == '0':
            return False
        else:
            return True
    
    def startElement(self, name, attrs):
        global import_time_of_start
        
        if name == "mnemosyne":
            if attrs.get("time_of_start"):
                import_time_of_start \
                  = StartTime(long(attrs.get("time_of_start")))
            else:
                import_time_of_start = time_of_start
                
        elif name == "item":
            self.card = Card()
            
            self.card.id = 0
            if attrs.get("id"):
                self.card.id = attrs.get("id")

            self.card.grade = 0
            if attrs.get("gr"):
                self.card.grade = int(attrs.get("gr"))

            self.card.easiness = average_easiness()
            if attrs.get("e"):
                self.card.easiness = float(attrs.get("e"))

            self.card.acq_reps = 0
            if attrs.get("ac_rp"):
                self.card.acq_reps = int(attrs.get("ac_rp"))

            self.card.ret_reps = 0
            if attrs.get("rt_rp"):
                self.card.ret_reps = int(attrs.get("rt_rp"))
                
            self.card.lapses = 0
            if attrs.get("lps"):
                self.card.lapses = int(attrs.get("lps"))
                
            self.card.acq_reps_since_lapse = 0
            if attrs.get("ac_rp_l"):
                self.card.acq_reps_since_lapse = int(attrs.get("ac_rp_l"))

            self.card.ret_reps_since_lapse = 0
            if attrs.get("rt_rp_l"):
                self.card.ret_reps_since_lapse = int(attrs.get("rt_rp_l"))
                
            self.card.last_rep = 0
            if attrs.get("l_rp"):
                self.card.last_rep = int(attrs.get("l_rp"))
                
            self.card.next_rep = 0
            if attrs.get("n_rp"):
                self.card.next_rep = int(float(attrs.get("n_rp")))
                
        elif name == "category":
            self.active = self.to_bool(attrs.get("active"))
            self.text["name"] = None

        else:
            self.reading[name] = True
            self.text[name] = ""

    def characters(self, ch):
        for name in self.reading.keys():
            if self.reading[name] == True:
                self.text[name] += ch

    def endElement(self, name):

        self.reading[name] = False

        if name == "cat":

            cat_name = self.text["cat"]
            self.card.cat = get_category_by_name(cat_name)

        elif name == "Q":

            self.card.q = self.text["Q"]

        elif name == "A":

            self.card.a = self.text["A"]

        elif name == "item":

            if self.card.id == 0:
                self.card.new_id()

            if self.card.id.startswith('_'):
                unanonymise_id(self.card)

            if self.card.cat == None:
                self.card.cat = self.default_cat

            if self.reset_learning_data == True:
                self.card.reset_learning_data()
                self.card.easiness = average_easiness()

            self.imported_cards.append(self.card)

        elif name == "category":

            name = self.text["name"]
            if (name != None):
                ensure_category_exists(name)
            get_category_by_name(name).active = self.active


# TODO: remove duplication over different XML formats

##############################################################################
#
# import_XML
#
#   Note that we do not register separate file formats for Mnemosyne and
#   Memaid XML. We're able to figure out the difference on our own and do not
#   need to put this burden on the user.
#
##############################################################################

def import_XML(filename, default_cat, reset_learning_data=False):
    global cards

    # Determine if we import a Mnemosyne or a Memaid file.

    handler = None

    f = None
    try:
        f = file(filename)
    except:
        try:
            f = file(unicode(filename).encode("latin"))
        except:
            raise LoadError()
    
    l = f.readline()
    l += f.readline();    
    if "mnemosyne" in l:
        handler = XML_Importer(default_cat, reset_learning_data)
    elif "smconv_pl" in l:
    	handler = smconv_XML_Importer(default_cat, reset_learning_data)
    else:
        handler = memaid_XML_Importer(default_cat, reset_learning_data)
        
    f.close()

    # Parse XML file.
    
    parser = make_parser()
    parser.setFeature(feature_namespaces, 0)
    parser.setContentHandler(handler)

    try:
        # Use cStringIo to avoid a crash in sax when filename has unicode
        # characters.
        s = file(filename).read()
        f = cStringIO.StringIO(s)
        parser.parse(f)
    except Exception, e:
        raise XMLError(stack_trace=True)

    # Calculate offset with current start date.
    
    cur_start_date =        time_of_start.time
    imp_start_date = import_time_of_start.time
    
    offset = long(round((cur_start_date - imp_start_date) / 60. / 60. / 24.))
        
    # Adjust timings.

    if reset_learning_data == False:
        if cur_start_date <= imp_start_date :
            for card in handler.imported_cards:
                card.last_rep += abs(offset)
                card.next_rep += abs(offset)
        else:
            time_of_start = StartTime(imp_start_date)
            for card in cards:
                card.last_rep += abs(offset)
                card.next_rep += abs(offset)

    return handler.imported_cards


##############################################################################
#
# encode_cdata
#
##############################################################################

def encode_cdata(s):
    return saxutils.escape(s.encode("utf-8"))



##############################################################################
#
# write_card_XML
#
##############################################################################

def write_card_XML(e, outfile, reset_learning_data=False):

    if reset_learning_data == False:
        print >> outfile, "<item id=\""+str(e.id) + "\"" \
                         + " gr=\""+str(e.grade) + "\"" \
                         + " e=\""+ "%.3f" % e.easiness + "\"" \
                         + " ac_rp=\""+str(e.acq_reps) + "\"" \
                         + " rt_rp=\""+str(e.ret_reps) + "\""  \
                         + " lps=\""+str(e.lapses) + "\"" \
                         + " ac_rp_l=\""+str(e.acq_reps_since_lapse) + "\"" \
                         + " rt_rp_l=\""+str(e.ret_reps_since_lapse) + "\"" \
                         + " l_rp=\""+str(e.last_rep) + "\"" \
                         + " n_rp=\""+str(e.next_rep) + "\">"
    else:
        print >> outfile, "<item id=\"" + anonymise_id(e) + "\">"

    print >> outfile, " <cat>" + encode_cdata(e.cat.name) + "</cat>"
    print >> outfile, " <Q>" + encode_cdata(e.q) + "</Q>"
    print >> outfile, " <A>" + encode_cdata(e.a) + "</A>"
    print >> outfile, "</item>"



##############################################################################
#
# bool_to_digit
#
##############################################################################

def bool_to_digit(b):
    
    if b == True:
        return "1"
    else:
        return "0"



##############################################################################
#
# write_category_XML
#
##############################################################################

def write_category_XML(category, outfile, reset_learning_data):

    if reset_learning_data == True:
        active = True
    else:
        active = category.active
    
    print >> outfile, "<category active=\"" \
          + bool_to_digit(active) + "\">"
    print >> outfile, " <name>" + encode_cdata(category.name) + "</name>"
    print >> outfile, "</category>"



##############################################################################
#
# export_XML
#
##############################################################################

def export_XML(filename, cat_names_to_export, reset_learning_data):
        
    try:
        outfile = file(filename,'w')
    except:
        return False

    print >> outfile, """<?xml version="1.0" encoding="UTF-8"?>"""

    print >> outfile, "<mnemosyne core_version=\"1\"",

    if reset_learning_data == False:
        print >> outfile, "time_of_start=\"" + \
              str(long(time_of_start.time))+"\"",

    print >> outfile, ">"
    
    for cat in categories:
        if cat.name in cat_names_to_export:
            write_category_XML(cat, outfile, reset_learning_data)

    for e in cards:
        if e.cat.name in cat_names_to_export:
            write_card_XML(e, outfile, reset_learning_data)

    print >> outfile, """</mnemosyne>"""

    outfile.close()

    return True


register_file_format("Mnemosyne XML",
                     filter=_("Mnemosyne XML files (*.xml *.XML)"),
                     import_function=import_XML,
                     export_function=export_XML)
