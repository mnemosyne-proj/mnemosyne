
from xml.sax import saxutils, make_parser
from xml.sax.handler import feature_namespaces, ContentHandler



##############################################################################
#
# memaid_XML_Importer
#
##############################################################################

class memaid_XML_Importer(ContentHandler):
    
    def __init__(self, default_cat=None, reset_learning_data=False):
        self.reading, self.text = {}, {}
        
        self.reading["cat"] = False
        self.reading["f"]   = False
        self.reading["b"]   = False

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
        
        if name == "memaid":
            if attrs.get("time_of_start"):
                import_time_of_start \
                  = StartTime(long(attrs.get("time_of_start")))
            else:
                import_time_of_start = time_of_start
                
        elif name == "item":
            self.card = Card()

            self.card.id        = long(attrs.get("id"))
            self.card.grade     =  int(attrs.get("gr"))
            self.card.next_rep  =  int(attrs.get("tm_t_rpt"))
            self.card.ret_reps  =  int(attrs.get("rp"))
            interval            =  int(attrs.get("ivl"))
            self.card.last_rep  = self.card.next_rep - interval
            self.card.easiness  = average_easiness()

        elif name == "category":
            self.active = self.to_bool(attrs.get("scheduled"))
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

        elif name == "f":

            self.card.q = self.text["f"]

        elif name == "b":

            self.card.a = self.text["b"]

        elif name == "item":

            if self.card.id == 0:
                self.card.new_id()

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