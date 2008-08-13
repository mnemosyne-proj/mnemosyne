#
# both_ways.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView


class BothWays(CardType):

    def __init__(self, language_name=""):
        CardType.__init__(self)

        if not language_name:
            self.id = "2"
            self.name = _("Front-to-back and back-to-front")
            self.is_language = False
        else:
            self.id = "2_" + language_name
            self.name = language_name
            self.is_language = True

        # List and name the keys.

        self.fields.append(("q", _("Question")))
        self.fields.append(("a", _("Answer")))

        # Front-to-back.

        v = FactView(_("Front-to-back"))
        v.q_fields = ["q"]
        v.a_fields = ["a"]
        v.required_fields = ["q"]
        self.fact_views.append(v)

        # Back-to-front.

        v = FactView(_("Back-to-front"))
        v.q_fields = ["a"]
        v.a_fields = ["q"]
        v.required_fields = ["a"]
        self.fact_views.append(v)


################################ OLD CODE - TO CHECK ########################


    ##########################################################################
    #
    # new_cards
    #
    ##########################################################################

    def new_cards(self, data):

        # TODO: move out.

        self.widget.clear()

        return

        # TODO: add duplicate checking.

        ## Old code:

        orig_added = self.check_duplicates_and_add(grade,q,a,cat_names)
        rev_added = None

        if orig_added and add_vice_versa:
            rev_added = self.check_duplicates_and_add(grade,a,q,\
                                               cat_names,orig_added.id+'.inv')

        if add_vice_versa and orig_added and not rev_added:

            # Swap question and answer.

            self.question.setText(a)
            self.answer.setText(q)
            self.addViceVersa.setChecked(False)

        elif orig_added:

            # Clear the form to make room for new question.

            self.question.setText("")
            self.answer.setText("")



    ##########################################################################
    #
    # check_duplicates_and_add
    #
    # TODO: check how this needs to be changed when there are multiple
    # categories possible. Probably replace category by card types then.
    #
    ##########################################################################

    def check_duplicates_and_add(self, grade, q, a, cat_names, id=None):

        if config["check_duplicates_when_adding"] == True:

            # Find duplicate questions and refuse to add if duplicate
            # answers are found as well.

            allow_dif_cat = config["allow_duplicates_in_diff_cat"]

            same_questions = []

            for card in get_cards():
                if card.q == q:
                    if card.a == a:

                        if card.cat.name == cat_name or not allow_dif_cat:
                            QMessageBox.information(None,
                                                    _("Mnemosyne"),
                                _("Card is already in database.\n")\
                                .append(_("Duplicate not added.")),
                                _("&OK"))

                            return None

                    elif card.cat.name == cat_name or not allow_dif_cat:
                        same_questions.append(card)

            # Make a list of already existing answers for this question
            # and merge if the user wishes so.

            if len(same_questions) != 0:

                answers = a
                for i in same_questions:
                    answers += ' / ' + i.a

                status = QMessageBox.question(None,
                   _("Mnemosyne"),
                   _("There are different answers for this question:\n\n")\
                     .append(answers),
                   _("&Merge and edit"),
                   _("&Add as is"),
                   _("&Do not add"), 0, -1)

                if status == 0: # Merge and edit.

                    new_card = add_new_card(grade, q, a, cat_names, id)
                    self.update_combobox(cat_names)

                    for i in same_questions:
                        new_card.grade = min(new_card.grade, i.grade)
                        new_card.a += ' / ' + i.a
                        delete_card(i)

                    dlg = EditCardDlg(new_card, self)

                    dlg.exec_loop()

                    return new_card

                if status == 2: # Don't add.
                    return None

        new_card = add_new_card(grade, q, a, cat_names, id)
        self.update_combobox(cat_names)

        return new_card
