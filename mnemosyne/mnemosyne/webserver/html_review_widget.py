#
# html_review_widget.py <Peter.Bienstman@UGent.be>
#

from string import Template

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class HtmlReviewWidget(ReviewWidget):

    """I've tried fiddling with css to get the grades area always show up at
    the bottom of the screen, no matter the contents of the cards, but I
    never got this to work reliably both on Firefox and IE. Therefore, we
    place the grades at the top, where they are also always at the same
    location for easy ergonomic access.

    """
    
    def __init__(self, component_manager):
        ReviewWidget.__init__(self, component_manager)
        self._question_label = ""
        self._question = ""
        self._question_box_visible = True
        self._answer = ""
        self._answer_label = _("Answer:")
        self._answer_box_visible = True
        self._show_button = ""
        self._show_button_enabled = True              
        self._grade_buttons_enabled = False
        self._status_bar = ""
        self.template = Template(\
            file("mnemosyne/webserver/review_page.html").read())
        
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
        card_type = card.fact.card_type
        card_css = card_type.renderer().css(card_type)
        #card_css = ""
        buttons = ""
        if self._grade_buttons_enabled:
            buttons = ""
            for i in range(6):
                buttons += """
                  <td>
                    <form action="" method="post">
                      <input type="submit" name="grade" accesskey="%d"
                       value="%d">
                    </form>
                  </td>""" % (i, i)
        if self._show_button_enabled:
            buttons = """
              <td>
                <form action="" method="post">
                  <input type="submit" name="show_answer" value="%s">
                </form>
              </td>""" % (self._show_button)
        question = ""
        if self._question_box_visible:
            if not self._question:
                question += "&nbsp;"
            else:
                for field in card.fact_view.q_fields:
                    s = card.fact[field]
                    for f in self.filters():
                        if f.run_on_export:
                            s = f.run(s)
                    question += "<div id=\"%s\">%s</div>" % (field, s) 
        answer = ""
        if self._answer_box_visible: # TODO: fixed using new renderers
            if not self._answer:
                answer += "&nbsp;"
            else:
                for field in card.fact_view.a_fields:
                    s = card.fact[field]
                    for f in self.filters():
                        if f.run_on_export:
                            s = f.run(s)
                    answer += "<div id=\"%s\">%s</div>" % (field, s)
        return self.template.substitute(card_css=card_css, buttons=buttons,
            question_label=self._question_label, question=question,
            answer_label=self._answer_label, answer=answer,
            status_bar=self._status_bar).encode("utf-8")

       
