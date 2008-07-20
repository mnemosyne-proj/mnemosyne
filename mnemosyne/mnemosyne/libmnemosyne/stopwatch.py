##############################################################################
#
# stopwatch.py <Peter.Bienstman@UGent.be>
#
##############################################################################

import time

# TODO: rework into class

_thinking_time = 0
_time_of_last_question = 0


##############################################################################
#
# start_thinking
#
##############################################################################

def start_thinking():

    global _thinking_time, _time_of_last_question

    _thinking_time = 0
    _time_of_last_question = time.time()



##############################################################################
#
# pause_thinking
#
##############################################################################

def pause_thinking():

    global _thinking_time

    if _time_of_last_question != 0:
        _thinking_time += time.time() - _time_of_last_question



##############################################################################
#
# unpause_thinking
#
##############################################################################

def unpause_thinking():

    global _time_of_last_question
    
    if _time_of_last_question != 0:
        _time_of_last_question = time.time()



##############################################################################
#
# stop_thinking
#
##############################################################################

def stop_thinking():

    global _thinking_time, _time_of_last_question
    
    _thinking_time += time.time() - _time_of_last_question
    _time_of_last_question = 0

    return _thinking_time
