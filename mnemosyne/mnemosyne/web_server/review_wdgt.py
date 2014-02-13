#
# review_wdgt.py <Peter.Bienstman@UGent.be>
#

import os
from string import Template

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class ReviewWdgt(ReviewWidget):

    """I've tried fiddling with css to get the grades area always show up at
    the bottom of the screen, no matter the contents of the cards, but I
    never got this to work satisfactory both on Firefox and IE. There would
    always be issues with spurious scrollbars or the card areas not expanding
    to fill the entire screen.
    Therefore, we place the grades at the top, where they are also always at
    the same location for easy ergonomic access.

    """

    def __init__(self, component_manager):
        ReviewWidget.__init__(self, component_manager)
        self.is_server_local = False
        self.question_label = ""
        self.question = ""
        self.is_question_box_visible = True
        self.answer = ""
        self.answer_label = _("Answer:")
        self.is_answer_box_visible = True
        self.show_button = ""
        self.is_show_button_enabled = True
        self.is_grade_buttons_enabled = False
        self.status_bar = ""
        self.template = Template("""
<!DOCTYPE html>
<html>
<head>
  <title>Mnemosyne</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
<style type="text/css">
table {
  width: 100%;
  border: 1px solid black;
  padding: 1em;
}
table.buttonarea {
  border: 0;
  padding: 0;
  background-color: white;
}
input {
  width: 100%;
}

$card_css
</style>
</head>
<body>

<table class="buttonarea">
  <tr>
  $buttons
  </tr>
</table>

<p>$question_label</p>

<table id="mnem1" class="mnem">
  <tr>
    <td>$question</td>
  </tr>
</table>

<p>$answer_label</p>

<table id="mnem1" class="mnem">
  <tr>
    <td>$answer</td>
  </tr>
</table>

<p>$status_bar</p>

</body>
</html>
""")
        
    def set_is_server_local(self, is_server_local):
        self.is_server_local = is_server_local

    def redraw_now(self):
        pass

    def show_answer(self):
        self.review_controller().show_answer()

    def grade_answer(self, grade):
        self.review_controller().grade_answer(grade)

    def set_question_box_visible(self, is_visible):
        self.is_question_box_visible = is_visible

    def set_answer_box_visible(self, is_visible):
        self.is_answer_box_visible = is_visible

    def set_question_label(self, text):
        self.question_label = text

    def set_question(self, text):
        self.question = text

    def set_answer(self, text):
        self.answer = text

    def clear_question(self):
        self.question = ""

    def clear_answer(self):
        self.answer = ""

    def update_show_button(self, text, is_default, is_enabled):
        self.show_button = text
        self.is_show_button_enabled = is_enabled

    def set_grades_enabled(self, is_enabled):
        self.is_grade_buttons_enabled = is_enabled

    def set_default_grade(self, grade):
        pass

    def update_status_bar_counters(self):
        scheduled_count, non_memorised_count, active_count = \
            self.review_controller().counters()
        counters = "Sch.: %d Not mem.: %d Act.: %d" % \
            (scheduled_count, non_memorised_count, active_count)
        self.status_bar = """
              <table class="buttonarea">
              <tr>
                <td> """ + counters + """ </td>
                <td>
                  <form action="" method="post">
                    <input type="submit" name="star" value="Star">
                  </form>
                </td>
              </tr></table>"""

    def to_html(self):
        self.controller().heartbeat()
        card_css = ""
        card = self.review_controller().card
        if card:
            card_css = self.render_chain().renderer_for_card_type\
                (card.card_type).card_type_css(card.card_type)
        buttons = ""
        if self.is_grade_buttons_enabled:
            buttons = ""
            for i in range(6):
                buttons += """
                  <td>
                    <form action="" method="post">
                      <input type="submit" name="grade" accesskey="%d"
                       value="%d">
                    </form>
                  </td>""" % (i, i)
        if self.is_show_button_enabled:
            buttons = """
              <td>
                <form action="" method="post">
                  <input type="submit" name="show_answer" value="%s">
                </form>
              </td>""" % (self.show_button)
        if not self.question:
            self.question = "&nbsp;"  # For esthetic reasons.
        if not self.answer:
            self.answer = "&nbsp;"
        extended_status_bar = self.status_bar
        if self.is_server_local:
            extended_status_bar = extended_status_bar.replace(\
            "</tr></table>", \
            """<td>
                  <form action="" method="post">
                    <input type="submit" name="exit" value="Exit">
                  </form>
                </td>
            </tr></table>""")
        return self.template.substitute(card_css=card_css, buttons=buttons,
            question_label=self.question_label, question=self.question,
            answer_label=self.answer_label, answer=self.answer,
            status_bar=extended_status_bar).encode("utf-8")

