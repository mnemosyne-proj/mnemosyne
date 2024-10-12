#
# review_wdgt.py <Peter.Bienstman@gmail.com>
#

import os
from string import Template

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget
import re


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
        self.review_controller().set_render_chain("web_server")
        self.client_on_same_machine_as_server = False
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
img {
  max-width: 100%;
}

$card_css
$hide_answer_css
</style>
</head>
<body>
<table class="buttonarea">
  <tr>
  $buttons
  </tr>
</table>
<p class="question">$question_label</p>
<table id="mnem1" class="mnem question">
  <tr>
    <td>$question</td>
  </tr>
</table>
<p class="answer">$answer_label</p>
<table id="mnem1" class="mnem answer">
  <tr>
    <td>$answer</td>
  </tr>
</table>
<p>$status_bar</p>
$js
</body>
</html>
""")

    def set_client_on_same_machine_as_server\
        (self, client_on_same_machine_as_server):
        self.client_on_same_machine_as_server = \
            client_on_same_machine_as_server

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

        hide_answer_css = ""
        if card is not None and card.fact_view.a_on_top_of_q:
            hide_answer_css += """
              .answer {
                display: none;
              }
            """
        extended_status_bar = self.status_bar
        if self.client_on_same_machine_as_server:
            extended_status_bar = extended_status_bar.replace(\
            "</tr></table>", \
            """<td>
                  <form action="" method="post">
                    <input type="submit" name="exit" value="Exit">
                  </form>
                </td>
            </tr></table>""")

        player_and_index = ""
        call_player = ""
        for match in re.finditer(r'player_(\d+)', self.question, re.DOTALL):
              end_index = self.question.find("</audio>", match.start())
              substr = self.question[match.start():end_index]
              ids_count = substr.count('<source src=')
              if ids_count > 1:
                  str1 = self.question[match.start():match.end()]
                  idstr = re.findall(r'player_(\d+)', str1)
                  i = idstr.pop()
                  player_and_index += \
                  'var audio_player_{id} = null;\n'.format(id = i)
                  player_and_index += "let index_{id} = {val};\n". \
                                  format(id = i, val =  "{val : 0}" )
                  call_player += \
                      "init_player(audio_player_{id}, 'player_{id}' , index_{id});\n".format(id = i) 
        for match in re.finditer(r'player_(\d+)', self.answer, re.DOTALL):
            end_index = self.answer.find("</audio>", match.start())
            substr = self.answer[match.start():end_index]
            ids_count = substr.count('<source src=')
            if ids_count > 1:
                str1 = self.answer[match.start():match.end()]
                idstr = re.findall(r'player_(\d+)', str1)
                i = idstr.pop()
                player_and_index += \
                'var audio_player_{id} = null;\n'.format(id = i)
                player_and_index += "let index_{id} = {val};\n". \
                                format(id = i, val =  "{val : 0}" )
                call_player += \
                    "init_player(audio_player_{id}, 'player_{id}' , index_{id});\n".format(id = i) 
        if player_and_index == "":
            javascript = ""
        else:
            javascript = """
                <script>
                    %s
                    function init_player(audio_player, fact_id, index)
                    {
                        var audio_player = document.getElementById(fact_id, index);
                        if (null === audio_player) return;
                            
                        if(audio_player.children.length > 1)  
                        {
                            audio_player.addEventListener('ended', function(event)
                            {
                                play.call(this, event, audio_player, index);
                            }, false);
                        }
                        audio_player.src = audio_player.children[index.val].src
                    }
                    
                    var play = function play_playlist(event, audio_player, index)
                    {
                        index.val += 1; 
                        audio_player.autoplay = true;
                        if(index.val == audio_player.children.length)
                        {
                            audio_player.autoplay = false;
                            index.val = 0;
                        }
                        audio_player.src = audio_player.children[index.val].src
                    }
                    %s   
              </script> 		 
              """ % (player_and_index, call_player)
        
        return self.template.substitute(card_css=card_css, buttons=buttons,
            question_label=self.question_label, question=self.question,
            answer_label=self.answer_label, answer=self.answer,
            status_bar=extended_status_bar, 
            hide_answer_css=hide_answer_css, js = javascript).encode("utf-8")