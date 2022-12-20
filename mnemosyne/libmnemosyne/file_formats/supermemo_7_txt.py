#
# supermemo_7_text.py Dirk Herrmann, <Peter.Bienstman@gmail.com>
#

import re
import time
from xml.sax import saxutils

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.file_format import FileFormat
from mnemosyne.libmnemosyne.file_formats.media_preprocessor \
    import MediaPreprocessor

re0 = re.compile(r"&#(.+?);", re.DOTALL | re.IGNORECASE)

HOUR = 60 * 60 # Seconds in an hour.
DAY = 24 * HOUR # Seconds in a day.


class SuperMemo7Txt(FileFormat, MediaPreprocessor):

    """Imports SuperMemo 7's text file format:
    A line starting with 'Q: ' holds a question, a line starting with 'A: '
    holds an answer.  Several consecutive question lines form a multi line
    question, several consecutive answer lines form a multi line answer.  After
    the answer lines, learning data may follow.  This consists of a line like
    'I: REP=8 LAP=0 EF=3.200 UF=2.370 INT=429 LAST=27.01.06' and a line like
    'O: 36'.  After each card (even the last one) there must be an empty line.

    """

    description = _("SuperMemo7 text in Q:/A: format")
    extension = ".txt"
    filename_filter = _("SuperMemo7 text files (*.txt *.TXT)")
    import_possible = True
    export_possible = False

    def __init__(self, component_manager):
        FileFormat.__init__(self, component_manager)
        MediaPreprocessor.__init__(self, component_manager)

    def process_html_unicode(self, s):

        """Parse html style escaped unicode (e.g. &#33267;)"""

        for match in re0.finditer(s):
            u = chr(int(match.group(1)))  # Integer part.
            s = s.replace(match.group(), u)  # Integer part with &# and ;.
        return s

    def read_line_sm7qa(self, f):
        line = f.readline()
        if not line:
            return False
        # SuperMemo uses 0x03 to represent the accented u character. Since
        # this does not seem to be a standard encoding, we simply replace this.
        line = line.replace("\x03", "\xfa")
        return self.process_html_unicode(line.rstrip())

    def do_import(self, filename, extra_tag_names=""):
        f = None
        try:
            f = open(filename, 'r')
        except:
            self.main_widget().show_error(_("Could not load file."))
            return
        state = "CARD-START"
        next_state = None
        error = False
        card_type = self.card_type_with_id("1")
        tag_names = [tag_name.strip() for \
            tag_name in extra_tag_names.split(",") if tag_name.strip()]
        while not error and state != "END-OF-FILE":
            line = self.read_line_sm7qa(f)
            # Perform the actions of the current state and calculate
            # the next state.
            if state == "CARD-START":
                # Expecting a new card to start, or the end of the input file.
                if line == False:
                    next_state = "END-OF-FILE"
                elif line == "":
                    next_state = "CARD-START"
                elif line.startswith("Q:"):
                    question = line[2:].strip()
                    repetitions = 0
                    lapses = 0
                    easiness = 2.5
                    interval = 0
                    last = 0
                    next_state = "QUESTION"
                else:
                    error = True
            elif state == "QUESTION":
                # We have already read the first question line. Further
                # question lines may follow, or the first answer line.
                if line == False:
                    error = True
                elif line.startswith("Q:"):
                    question = question + "\n" + line[2:].strip()
                    next_state = "QUESTION"
                elif line.startswith("A:"):
                    answer = line[2:].strip()
                    next_state = "ANSWER"
                else:
                    error = True
            elif state == "ANSWER":
                # We have already read the first answer line. Further answer
                # lines may follow, or the lines with the learning data.
                # Otherwise, the card has to end with either an empty line or
                # with the end of the input file.
                if line == False:
                    next_state = "END-OF-FILE"
                elif line == "":
                    next_state = "CARD-START"
                elif line.startswith("A:"):
                    answer = answer + "\n" + line[2:].strip()
                    next_state = "ANSWER"
                elif line.startswith("I:"):
                    attributes = line[2:].split()
                    if len(attributes) != 6:
                        error = True
                    else:
                        if (attributes[0].startswith("REP=") \
                            and attributes[1].startswith("LAP=") \
                            and attributes[2].startswith("EF=") \
                            and attributes[4].startswith("INT=") \
                            and attributes[5].startswith("LAST=")):
                            repetitions = int(attributes[0][4:])
                            lapses = int(attributes[1][4:])
                            easiness = float(attributes[2][3:])
                            interval = int(attributes[4][4:]) * DAY
                            if attributes[5] == "LAST=0":
                                last = 0
                            else:
                                last = int(time.mktime(time.strptime\
                                    (attributes[5][5:], "%d.%m.%y")))
                        else:
                            error = True
                    next_state = "LEARNING-DATA"
                else:
                    error = True
            elif state == "LEARNING-DATA":
                # We have already read the first line of the learning data.
                # The second line with the learning data has to follow.
                if line == False:
                    error = True
                elif line.startswith("O:"): # This line is ignored.
                    next_state = "CARD-END"
                else:
                    error = True
            elif state == "CARD-END":
                # We have already read all learning data. The card has to end
                # with either an empty line or with the end of the input file.
                if line == False:
                    next_state = "END-OF-FILE"
                elif line == "":
                    next_state = "CARD-START"
                else:
                    error = True
            # Perform the transition actions that are common for a set of
            # transitions.
            if ( (state == "ANSWER" and next_state == "END-OF-FILE") \
                    or (state == "ANSWER" and next_state == "CARD-START") \
                    or (state == "CARD-END" and next_state == "END-OF-FILE") \
                    or (state == "CARD-END" and next_state == "CARD-START") ):
                # Grade information is not given directly in the file format.
                # To make the transition to Mnemosyne smooth for a SuperMemo
                # user, we make sure that all cards get queried in a similar
                # way as SuperMemo would have done it.
                if repetitions == 0:
                    grade = -1
                else:
                    grade = 4
                fact_data = {"f": saxutils.escape(question),
                    "b": saxutils.escape(answer)}
                self.preprocess_media(fact_data, tag_names)
                card = self.controller().create_new_cards(fact_data, card_type,
                    grade=grade, tag_names=tag_names,
                    check_for_duplicates=False, save=False)[0]
                if _("MISSING_MEDIA") in tag_names:
                    tag_names.remove(_("MISSING_MEDIA"))
                card.easiness = easiness
                # There is no possibility to calculate the correct values for
                # card.acq_reps and card.ret_reps from the SM file format.
                card.acq_reps = 0
                card.ret_reps = 0
                card.lapses = lapses
                # card.acq_reps_since_lapse cannot be reconstructed from SM.
                card.ret_reps_since_lapse = max(0, repetitions - 1)
                card.last_rep = self.scheduler().midnight_UTC(last)
                card.next_rep = card.last_rep + interval
                # The following information from SM is not used: UF, O_value.
                self.database().update_card(card)
            state = next_state
        self.warned_about_missing_media = False
        if error:
            self.main_widget().show_error(_("An error occured while parsing."))
