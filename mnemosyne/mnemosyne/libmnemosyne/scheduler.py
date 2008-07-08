##############################################################################
#
# scheduler.py <Peter.Bienstman@UGent.be>
#
##############################################################################

# TODO: make into a class?

##############################################################################
#
# calculate_initial_interval
#
##############################################################################

def calculate_initial_interval(grade):

    # If this is the first time we grade this card, allow for slightly
    # longer scheduled intervals, as we might know this card from before.

    interval = (0, 0, 1, 3, 4, 5) [grade]
    return interval



##############################################################################
#
# calculate_interval_noise
#
##############################################################################

def calculate_interval_noise(interval):

    if interval == 0:
        noise = 0
    elif interval == 1:
        noise = random.randint(0,1)
    elif interval <= 10:
        noise = random.randint(-1,1)
    elif interval <= 60:
        noise = random.randint(-3,3)
    else:
        a = .05 * interval
        noise = int(random.uniform(-a,a))

    return noise


##############################################################################
#
# rebuild_revision_queue
#
##############################################################################

def rebuild_revision_queue(learn_ahead = False):
            
    global revision_queue
    
    revision_queue = []

    if len(cards) == 0:
        return

    time_of_start.update_days_since()

    # Always add cards that are due for revision.

    revision_queue = [i for i in cards if i.is_due_for_retention_rep()]
    random.shuffle(revision_queue)

    # If the queue is empty, then add cards which are not yet memorised.
    # Take only a limited number of grade 0 cards from the unlearned cards,
    # to avoid too long intervals between repetitions.
    
    if len(revision_queue) == 0:
        
        not_memorised = [i for i in cards if i.is_due_for_acquisition_rep()]

        grade_0 = [i for i in not_memorised if i.grade == 0]
        grade_1 = [i for i in not_memorised if i.grade == 1]

        limit = get_config("grade_0_cards_at_once")

        grade_0_selected = []

        if limit != 0:
            for i in grade_0:
                for j in grade_0_selected:
                    if cards_are_inverses(i, j):
                        break
                else:
                    grade_0_selected.append(i)

                if len(grade_0_selected) == limit:
                    break

        random.shuffle(grade_0_selected)
        revision_queue[0:0] = grade_0_selected

        random.shuffle(grade_1)
        revision_queue[0:0] = grade_1
        
        random.shuffle(grade_0_selected)
        revision_queue[0:0] = grade_0_selected

    # If the queue is still empty, then simply return. The user can signal
    # that he wants to learn ahead by calling rebuild_revision_queue with
    # 'learn_ahead' set to True. Don't shuffle this queue, as it's more
    # useful to review the earliest scheduled cards first.

    if len(revision_queue) == 0:
        
        if learn_ahead == False:
            return
        else:
            revision_queue = [i for i in cards \
                              if i.qualifies_for_learn_ahead()]

            revision_queue.sort(key=Card.sort_key)



##############################################################################
#
# in_revision_queue
#
##############################################################################

def in_revision_queue(card):
    return card in revision_queue



##############################################################################
#
# remove_from_revision_queue
#
#   Remove a single instance of an card from the queue. Necessary when
#   the queue needs to be rebuilt, and there is still a question pending.
#
##############################################################################

def remove_from_revision_queue(card):
    
    global revision_queue
    
    for i in revision_queue:
        if i.id == card.id:
            revision_queue.remove(i)
            return


##############################################################################
#
# get_new_question
#
##############################################################################

def get_new_question(learn_ahead = False):
            
    # Populate list if it is empty.
        
    if len(revision_queue) == 0:
        rebuild_revision_queue(learn_ahead)
        if len(revision_queue) == 0:
            return None

    # Pick the first question and remove it from the queue.

    card = revision_queue[0]
    revision_queue.remove(card)

    return card



##############################################################################
#
# process_answer
#
##############################################################################

def process_answer(card, new_grade, dry_run=False):

    global revision_queue, cards

    # When doing a dry run, make a copy to operate on. Note that this
    # leaves the original in cards and the reference in the GUI intact.

    if dry_run:
        card = copy.copy(card)

    # Calculate scheduled and actual interval, taking care of corner
    # case when learning ahead on the same day.
    
    scheduled_interval = card.next_rep    - card.last_rep
    actual_interval    = days_since_start - card.last_rep

    if actual_interval == 0:
        actual_interval = 1 # Otherwise new interval can become zero.

    if card.is_new():

        # The card is not graded yet, e.g. because it is imported.

        card.acq_reps = 1
        card.acq_reps_since_lapse = 1

        new_interval = calculate_initial_interval(new_grade)

        # Make sure the second copy of a grade 0 card doesn't show up again.

        if not dry_run and card.grade == 0 and new_grade in [2,3,4,5]:
            for i in revision_queue:
                if i.id == card.id:
                    revision_queue.remove(i)
                    break

    elif card.grade in [0,1] and new_grade in [0,1]:

        # In the acquisition phase and staying there.
    
        card.acq_reps += 1
        card.acq_reps_since_lapse += 1
        
        new_interval = 0

    elif card.grade in [0,1] and new_grade in [2,3,4,5]:

         # In the acquisition phase and moving to the retention phase.

         card.acq_reps += 1
         card.acq_reps_since_lapse += 1

         new_interval = 1

         # Make sure the second copy of a grade 0 card doesn't show up again.

         if not dry_run and card.grade == 0:
             for i in revision_queue:
                 if i.id == card.id:
                     revision_queue.remove(i)
                     break

    elif card.grade in [2,3,4,5] and new_grade in [0,1]:

         # In the retention phase and dropping back to the acquisition phase.

         card.ret_reps += 1
         card.lapses += 1
         card.acq_reps_since_lapse = 0
         card.ret_reps_since_lapse = 0

         new_interval = 0

         # Move this card to the front of the list, to have precedence over
         # cards which are still being learned for the first time.

         if not dry_run:
             cards.remove(card)
             cards.insert(0,card)

    elif card.grade in [2,3,4,5] and new_grade in [2,3,4,5]:

        # In the retention phase and staying there.

        card.ret_reps += 1
        card.ret_reps_since_lapse += 1

        if actual_interval >= scheduled_interval:
            if new_grade == 2:
                card.easiness -= 0.16
            if new_grade == 3:
                card.easiness -= 0.14
            if new_grade == 5:
                card.easiness += 0.10
            if card.easiness < 1.3:
                card.easiness = 1.3
            
        new_interval = 0
        
        if card.ret_reps_since_lapse == 1:
            new_interval = 6
        else:
            if new_grade == 2 or new_grade == 3:
                if actual_interval <= scheduled_interval:
                    new_interval = actual_interval * card.easiness
                else:
                    new_interval = scheduled_interval
                    
            if new_grade == 4:
                new_interval = actual_interval * card.easiness
                
            if new_grade == 5:
                if actual_interval < scheduled_interval:
                    new_interval = scheduled_interval # Avoid spacing.
                else:
                    new_interval = actual_interval * card.easiness

        # Shouldn't happen, but build in a safeguard.

        if new_interval == 0:
            logger.info("Internal error: new interval was zero.")
            new_interval = scheduled_interval

        new_interval = int(new_interval)

    # When doing a dry run, stop here and return the scheduled interval.

    if dry_run:
        return new_interval

    # Add some randomness to interval.

    noise = calculate_interval_noise(new_interval)

    # Update grade and interval.
    
    card.grade    = new_grade
    card.last_rep = days_since_start
    card.next_rep = days_since_start + new_interval + noise
    
    # Don't schedule inverse or identical questions on the same day.

    for j in cards:
        if (j.q == card.q and j.a == card.a) or cards_are_inverses(card, j):
            if j != card and j.next_rep == card.next_rep and card.grade >= 2:
                card.next_rep += 1
                noise += 1
                
    # Create log entry.
        
    logger.info("R %s %d %1.2f | %d %d %d %d %d | %d %d | %d %d | %1.1f",
                card.id, card.grade, card.easiness,
                card.acq_reps, card.ret_reps, card.lapses,
                card.acq_reps_since_lapse, card.ret_reps_since_lapse,
                scheduled_interval, actual_interval,
                new_interval, noise, thinking_time)

    return new_interval + noise
