
##############################################################################
#
# Cuecard *.wcu importer/exporter by Chris Aakre (caaakre at gmail dot com).
#
# Issues: Does not handle sounds on import/export (not sure how to set it 
# up...help anyone?). Attribute tags are QuestionSound and AnswerSound.
#
##############################################################################

def import_wcu(filename, default_cat, reset_learning_data=False):
    
    global cards
    imported_cards = []
    avg_easiness = average_easiness()

    from xml.dom import minidom, Node
    f = None
    try:
        f = file(filename)
    except:
        try:
            f = file(unicode(filename).encode("latin"))
        except:
            raise LoadError()

    def wcuwalk(parent, cards, level=0):
        
        for node in parent.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                
                card = Card()
                
                if node.attributes.has_key("QuestionPicture"):
                    card.q='<img src="'+\
                            node.attributes.get("QuestionPicture").nodeValue+\
                            '"><br/>'+\
                            node.attributes.get("Question").nodeValue
                else:
                    card.q=node.attributes.get("Question").nodeValue
                    
                if node.attributes.has_key("AnswerPicture"):
                    card.a='<img src="'+\
                            node.attributes.get("AnswerPicture").nodeValue+\
                            '"><br/>'+\
                            node.attributes.get("Answer").nodeValue
                else:
                    card.a=node.attributes.get("Answer").nodeValue
                    
                card.easiness=avg_easiness
                card.cat = default_cat
                card.new_id()
                cards.append(card)
                
                wcuwalk(node, cards, level+1)

    wcuwalk(minidom.parse(filename).documentElement,imported_cards)
    
    return imported_cards



def export_wcu(filename, cat_names_to_export, reset_learning_data=False):
    
    try:
        if os.path.splitext(filename)[1] == '.wcu':
            outfile = file(filename,'w')
        else:
            outfile = file(filename+'.wcu','w')
    except:
        return False
    
    print >> outfile, '<?xml version="1.0" encoding="utf-8"?>'
    print >> outfile, '<CueCards Version="1">'
    
    for e in cards:
        if e.cat.name in cat_names_to_export:
            question = e.q.encode("utf-8")
            question = question.replace("\n", "<br/>")
            answer = e.a.encode("utf-8")
            answer = answer.replace("\n", "<br/>")
            print >> outfile, '<Card Question="'+question+\
                  '" Answer="'+answer+'" History=""/>'

    print >> outfile, '</CueCards>'
    outfile.close()
    
    return True

register_file_format(_("Cuecard .wcu"),
                     filter=_("Cuecard files (*.wcu *.WCU)"),
                     import_function=import_wcu,
                     export_function=export_wcu)
