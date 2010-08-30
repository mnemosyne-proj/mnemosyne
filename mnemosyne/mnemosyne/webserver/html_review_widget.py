#
# html_review_widget.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class HtmlReviewWidget(ReviewWidget):
    
    def __init__(self, component_manager):
        ReviewWidget.__init__(self, component_manager)
        self._question_label = ""
        self._question = ""
        self._question_box_visible = True
        self._answer_label = "Answer:"
        self._answer = ""
        self._answer_box_visible = True
        self._show_button = ""
        self._show_button_enabled = True              
        self._grade_buttons_enabled = False
        self._status_bar = ""
        
    def set_question_label(self, text):
        self._question_label = text
        
    def set_question(self, text):
        self._question = text

    def clear_question(self):
		self._question = ""
        
    def question_box_visible(self, visible):
        self._question_box_visible = visible

    def set_answer(self, text):
        self._answer = text

    def clear_answer(self):
		self._answer = ""
            
    def answer_box_visible(self, visible):
        self._answer_box_visible = visible

    def update_show_button(self, text, default, enabled):
        self._show_button = text
        self._show_button_enabled = enabled

    def enable_grades(self, enabled):
        self._grade_buttons_enabled = enabled
        
    def set_default_grade(self, grade):
        pass
        
    def show_answer(self):
        self.review_controller().show_answer()
           
    def grade_answer(self, grade):
        self.review_controller().grade_answer(grade)

    def update_status_bar(self):
        scheduled_count, non_memorised_count, active_count = \
                   self.review_controller().counters()
        self._status_bar  = "Sch.: %d Not mem.: %d Act.: %d" % \
            (scheduled_count, non_memorised_count, active_count)

    def to_html(self):
        card = self.review_controller().card
        #card_type = card.fact.card_type
        #css = card_type.renderer().css(card_type)

        #TODO: http://www.wickham43.supanet.com/tutorial/headerfooterfixexample.html

        css = """     
html { margin: 0; padding: 0; height: 100%; }
body { margin: 0; padding: 0; height: 100%; }
input.button {width: 100%; margin: 0; padding: 0;}
table { align: center; width: 99%; margin: 2px 0px; height: 39%;  border: 1px solid black;}
#container { position: absolute; left: 0px; top: 0px; margin-left: 1%; width: 99%; height: 99%; }
#footer { position:absolute; left: 0px; bottom: 0px; width: 100%; height: 10%;}
#footer table {height: 10%; border: 0; margin: 0; padding:0;}
"""     
        html = "<html><head><meta http-equiv=\"Content-Type\""
        html += "content=\"text/html; charset=UTF-8\"/>"
        html += "<style type=\"text/css\">" + css + "</style>"
        html += "</head><body>"

        html += "<div id=\"container\">"
        
        if self._question_box_visible and self._question:
            # Last clause was needed for 'learn ahead'.
            html += self._question_label + "<br><table><tr><td>"
            for field in card.fact_view.q_fields:
                s = card.fact[field]
                for f in self.filters():
                    if f.run_on_export:
                        s = f.run(s)
                html += "<div id=\"%s\">%s</div>" % (field, s)
            html += "</td></tr></table><br>"
        html += self._answer_label + "<br>"
        html +=  "<table><tr><td>"   
        if self._answer_box_visible and self._answer: # Todo: fixed using new renderers
            for field in card.fact_view.a_fields:
                s = card.fact[field]
                for f in self.filters():
                    if f.run_on_export:
                        s = f.run(s)
                html += "<div id=\"%s\">%s</div>" % (field, s)
        html += "</td></tr></table>"

        html += "<div id=\"footer\">"
        
        html += "<table><tr>"
            
        if self._grade_buttons_enabled:
            for i in range(6):
                html += "<td><form action=\"\" method=\"post\">"
                html += "<input class=\"button\" type=\"submit\" name=\"grade\""
                html += "accesskey=\"%d\" value=\"%d\"></form></td>" % (i, i)
        if self._show_button_enabled:
            html += "<td><form action=\"\" method=\"post\"><input type=\"submit\""
            html += "class=\"button\" name=\"show_answer\" value=\"%s\"" % (self._show_button)
            html += "</form></td>"
            
        html += "</tr></table>"
        
        html += self._status_bar 
        
        html += "</div></div>"

        
        html += "</body></html>"
        return html.encode("utf-8")

       
