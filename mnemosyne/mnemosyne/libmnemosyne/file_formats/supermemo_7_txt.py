##############################################################################
#
# Functions for importing and exporting files in SuperMemo's text file format:
# A line starting with 'Q: ' holds a question, a line starting with 'A: '
# holds an answer.  Several consecutive question lines form a multi line
# question, several consecutive answer lines form a multi line answer.  After
# the answer lines, learning data may follow.  This consists of a line like
# 'I: REP=8 LAP=0 EF=3.200 UF=2.370 INT=429 LAST=27.01.06' and a line like
# 'O: 36'.  After each card (even the last one) there must be an empty line.
#
##############################################################################

def read_line_sm7qa(f):

    line = f.readline()

    if not line:
        return False

    # Supermemo uses the octet 0x03 to represent the accented u character.
    # Since this does not seem to be a standard encoding, we simply replace
    # this.
    
    line = line.replace("\x03", "\xfa")

    try:
        line = unicode(line, "utf-8")
    except:
        try:
            line = unicode(line, "latin")
        except:
            raise EncodingError()
        
    line = line.rstrip()
    line = process_html_unicode(line)

    return line



def import_sm7qa(filename, default_cat, reset_learning_data=False):

    global cards

    # Parse txt file.

    avg_easiness = average_easiness()

    f = None
    try:
        f = file(filename)
    except:
        try:
            f = file(filename.encode("latin"))
        except:
            raise LoadError()

    imported_cards = []
    state = "CARD-START"
    next_state = None
    error = False

    while not error and state != "END-OF-FILE":

        line = read_line_sm7qa(f)

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
                easiness = avg_easiness
                interval = 0
                last = 0
                next_state = "QUESTION"
            else:
                error = True
        elif state == "QUESTION":
            
            # We have already read the first question line. Further question
            # lines may follow, or the first answer line.

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
            # Otherwise, the card has to end with either an empty line or with
            # the end of the input file.

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
                    if ( attributes[0].startswith("REP=")
                            and attributes[1].startswith("LAP=")
                            and attributes[2].startswith("EF=")
                            and attributes[4].startswith("INT=")
                            and attributes[5].startswith("LAST=") ):
                        repetitions = int(attributes[0][4:])
                        lapses = int(attributes[1][4:])
                        easiness = float(attributes[2][3:])
                        interval = int(attributes[4][4:])
                        if attributes[5] == "LAST=0":
                            last = 0
                        else:
                            last = time.strptime(attributes[5][5:], "%d.%m.%y")
                    else:
                        error = True
                next_state = "LEARNING-DATA"
            else:
                error = True
        elif state == "LEARNING-DATA":
            
            # We have already read the first line of the learning data. The
            # second line with the learning data has to follow.
            
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

        if ( (state == "ANSWER" and next_state == "END-OF-FILE")
                or (state == "ANSWER" and next_state == "CARD-START")
                or (state == "CARD-END" and next_state == "END-OF-FILE")
                or (state == "CARD-END" and next_state == "CARD-START") ):
            card = Card()

            if not reset_learning_data:
                
                # A grade information is not given directly in the file
                # format.  To make the transition to Mnemosyne smooth for a
                # SuperMemo user, we make sure that all cards get queried in a
                # similar way as SuperMemo would have done it.
                
                if repetitions == 0:
                    
                    # The card is new, there are no repetitions yet.
                    # SuperMemo queries such cards in a dedicated learning
                    # mode "Memorize new cards", thus offering the user to
                    # learn as many new cards per session as desired.  We
                    # achieve a similar behaviour by grading the card 0.
                    
                    card.grade = 0
                    
                elif repetitions == 1 and lapses > 0:
                    
                    # The learner had a lapse with the last repetition.
                    # SuperMemo users will expect such cards to be queried
                    # during the next session.  Thus, to avoid confusion, we
                    # set the initial grade to 1.
                    
                    card.grade = 1
                    
                else:
                    
                    # There were either no lapses yet, or some successful
                    # repetitions since.
                    
                    card.grade = 4
                    
                card.easiness = easiness

                # There is no possibility to calculate the correct values for
                # card.acq_reps and card.ret_reps from the SuperMemo file
                # format.  Thus, to distinguish between a new card and an card
                # that already has some learning data, the values are set to 0
                # or 1.
                
                if repetitions == 0:
                    card.acq_reps = 0
                    card.ret_reps = 0
                else:
                    card.acq_reps = 1
                    card.ret_reps = 1

                card.lapses = lapses

                # The following information is not reconstructed from
                # SuperMemo: card.acq_reps_since_lapse

                card.ret_reps_since_lapse = max(0, repetitions - 1)

                # Calculate the dates for the last and next repetitions.  The
                # logic makes sure that the interval between last_rep and
                # next_rep is kept.  To do this, it may happen that last_rep
                # gets a negative value.
                
                if last == 0:
                    last_in_days = 0
                else:
                    last_absolute_sec = StartTime(time.mktime(last)).time
                    last_relative_sec = last_absolute_sec - time_of_start.time
                    last_in_days = last_relative_sec / 60. / 60. / 24.
                card.next_rep = long( max( 0, last_in_days + interval ) )
                card.last_rep = card.next_rep - interval

                # The following information from SuperMemo is not used:
                # UF, O_value

            card.q = saxutils.escape(question)
            card.a = saxutils.escape(answer)
            card.cat = default_cat

            card.new_id()

            imported_cards.append(card)

        # Go to the next state.

        state = next_state

    if error:
        return False
    else:
        return imported_cards


register_file_format(_("SuperMemo7 text in Q:/A: format"),
                     filter=_("SuperMemo7 text files (*.txt *.TXT)"),
                     import_function=import_sm7qa,
                     export_function=False)


