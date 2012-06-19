#
# _cloze.py <Peter.Bienstman@UGent.be>
#

"""Utility functions for cloze handling, used e.g. in the Cloze and Sentence
card types.

"""

def get_q_a_from_cloze(text, index):

    """Return question and answer for the cloze with a given index in a text
    which can have the following form

    La [casa:house] es [grande:big]

    Use 'index=-1' to get the cloze text without brackets and without hints.

    """

    cursor = 0
    current_index = 0
    question = text
    answer = None
    while True:
        cursor = text.find("[", cursor)
        if cursor == -1:
            break
        cloze = text[cursor + 1:text.find("]", cursor)]
        if ":" in cloze:
            cloze_without_hint, hint = cloze.split(":", 1)
        else:
            cloze_without_hint, hint = cloze, "..."
        if current_index == index:
            question = question.replace(\
                "[" + cloze + "]", "[" + hint + "]", 1)
            answer = cloze_without_hint
        else:
            question = question.replace(\
                "[" + cloze + "]", cloze_without_hint, 1)
        cursor += 1
        current_index += 1
    return question, answer