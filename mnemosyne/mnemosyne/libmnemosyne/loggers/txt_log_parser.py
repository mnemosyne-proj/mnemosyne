#
# txt_log_parser.py <Peter.Bienstman@UGent.be> starting from code of
# Ryan Michael <kerinin@gmail.com> and Joonatan Kaartinen <jkaartinen@iki.fi>
#

import os
import bz2
import time
import traceback


class TxtLogParser(object):

    """Parse the txt logs and write the info it contains to a database
    object.

    """

    def __init__(self, filename, database): 
        try:
            before_extension = filename.split(".")[0]
            self.user_id, self.log_number = \
                os.path.basename(before_extension).split('_')
            self.log_number = int(self.log_number)
            self.logfile = bz2.BZ2File(self.filename)
        except:
            raise ArgumentError, "%s is not a valid log file." % filename
        self.filename = filename
        self.database = database
        
    def parse(self):
        self.version = "Mnemosyne X.X.X" # TODO: better option?
        self.stamp = None
        self.previous_stamp = None
        lower_stamp_limit = 1121021345 # 2005-07-10 21:49:05.
        upper_stamp_limit = time.time()
        self.database.parsing_started(self.user_id, self.log_number)
        try:
            for line in self.log_file:          
                parts = line.split(" : ")           
                try:
                    self.stamp = time.mktime(time.strptime(parts[0],
                                         "%Y-%m-%d %H:%M:%S"))
                except:
                    # Encountered in 48185e2d_00025.bz2.
                    print "time.strptime failed on %s in line\n%s"\
                          % (filename, line)
                    traceback.print_exc()
                    self.stamp = self.previous_stamp
                    # The line might be completely corrupted, so move on.
                    continue
                if not lower_stamp_limit < self.stamp < upper_stamp_limit:
                    raise TypeError, "Ignoring impossible date", parts[0]
                if parts[1].startswith("R "):
                    self._parse_repetition(parts[1])
                elif parts[1].startswith("Program started"):
                    self.version = parts[2]
                    # log program start
                elif parts[1].startswith("Loaded database"):
                    # log loaded database
                    pass
                elif parts[1].startswith("New item"):
                    self._parse_new_item(parts[1])
                elif parts[1].startswith("Imported item"):
                    self._parse_imported_item(parts[1])
                    # log
                elif parts[1].startswith("Deleted item"):
                    # log
                    pass
                elif parts[1].startswith("Program stopped"):
                    # log
                    pass
                self.previous_stamp = self.stamp
            self.database.parsing_stopped(self.user_id, self.log_number)
        except:
            print "Problem parsing file", self.filename
            traceback.print_exc()
            self.database.rollback()
    
    def _parse_new_item(self, new_item_chunck):

        """Note: there is a fundamental asymmetry in the way the first grading
        occurs for new cards and imported cards. For new cards, this happens
        when selecting the initial grade in the 'add card' dialog. For
        imported cards, this happens the first time the item pops up in the
        revision process.
    
        Starting from Mnemosyne 0.9.8, this asymmetry was recognised and
        removed (by Dirk Hermann) by always counting the initial grading of a
        card as an acquisition repetition, regardless of grade. So, the first
        'R' log entry of a new card added through the 'add cards' dialog was
        actually listed as acquisition repetition 2.
    
        For consistency, we here add the initial grading through the
        'add cards' dialog as a proper Repetition in the database. For cards
        added under the old scheme, we also modify the number of acq reps to
        be in accordance with the new scheme.

        TODO: expand docs
        In the 1.x series, ...
        The time stamps for repetitions are when the card was graded, not
        when it was presented to the user. In order to calculate the
        actual interval, we need the time of presentation, for which we will
        use the time stamp from the previous line.
        TODO: no longer valid still valid for 2.0?

        """
        
        # TODO: is there a log that starts with R?
        #if not self.previous_stamp:
        #    self.previous_stamp = self.stamp
        
        version_number = self.version.split()[1].split("-")[0]
        old_log_format = (version_number in ("0.1","0.9.1","0.9.2","0.9.3",
                                             "0.9.4", "0.9.5","0.9.6","0.9.7"))  
        new, item, id, grade, new_interval = new_item_chunck.split(" ")
        id = get_card_id(self.database, id)
        # Check for id clashes. Note: this could be improved somewhat by also
        # taking the user id in account in the query.
        self.database.execute(card_insert, {
            "user_id":self.user_id,
            "id":id,
            "old_log_format": old_log_format,
            "last_sequence": 1,
            "last_repetition_time": 0,
            "first_repetition_time": self.previous_stamp,
        })
        self.database.execute(repetition_insert, {
                     "card_id"            : id,
                     "user_id"            : self.user_id,
                     "time"               : 0,
                     "sequence"           : 1,
                     "grade"              : int(grade),
                     "easiness"           : 2.5, # Not logged, take default.
                     "acq_reps"           : 1,
                     "ret_reps"           : 0,
                     "lapses"             : 0,
                     "acq_since_lapse"    : 1,
                     "ret_since_lapse"    : 0,
                     "scheduled_interval" : 0,
                     "actual_interval"    : 0,
                     "new_interval"       : int(new_interval),
                     "noise"              : 0,
                     "thinking_time"      : 0,
                     "time_spent"         : self.stamp - self.previous_stamp,
                     "actual_interval_s"  : -666})

    def _parse_imported_item(imported_item_chunck):
        pass
    #    try:
    #    	imported, item, id, grade, ret_reps, last_rep, next_rep, interval \
    #              = imported_item_chunck.split(" ")
    #    id = get_card_id(self.database,id)
    #    except:
    #    	print "Warning! Invalid imported item. "
    #    	return False
        # It is possible that the card is already in the database, e.g. if we
        # export to file, start a new database, and then reimport.

        # Note: in very rare case this masks an id clash between cards.

    # Let _parse_repetition add the card on first repetition so we get
    # the first repetition time right.
    #    self.database.execute(card_insert, {
    #        "user_id"               : self.user_id,
    #        "id"                    : id,
    #        "old_log_format"        : False,
    #        "last_repetition_time"  : 0
    #    })

    def _parse_repetition(self, repetition_chunck):
        # TODO: is there a log that starts with R?
        #if not self.previous_stamp:
        #    self.previous_stamp = self.stamp
        try:       
            blocks = repetition_chunck.split(" | ")
            R, id, grade, easiness = blocks[0].split(" ")
            id = get_card_id(self.database,id)
            acq_reps, ret_reps, lapses, acq_reps_since_lapse, \
               ret_reps_since_lapse = blocks[1].split(" ")
            scheduled_interval, actual_interval = blocks[2].split(" ")
            new_interval, noise = blocks[3].split(" ")
            thinking_time = blocks[4]
        except:      
            print "Problem parsing repetition", repetition_chunck
            traceback.print_exc()
        else:
            # Make sure the card exists (e.g. due to missing logs.)
            result = self.database.execute("""
            SELECT old_log_format, last_repetition_time, 
                   key, first_repetition_time
            FROM card
            WHERE card.id=:id AND card.user_id=:user_id
                """,{"id":id, "user_id": self.user_id}
            ).fetchone()

            if result != None:
            (old_log_format,last_rep_time, key,
             first_rep_time) = result
            else:
            old_log_format = False
            last_rep_time = None
            first_rep_time = self.previous_stamp
                self.database.execute(card_insert, {
                    "user_id"               : self.user_id,
                    "id"                    : id,
                    "old_log_format"        : old_log_format,
                    "last_sequence"         : 1,
                    "last_repetition_time"  : 0,
                    "first_repetition_time" : first_rep_time,
                })

            if last_rep_time != None:
            actual_interval_s = self.previous_stamp - last_rep_time - first_rep_time
        else:
            actual_interval_s = -666
            # Move old log format to new one.
            if old_log_format == True:
                offset_1 = 1
                offset_2 = 1            
            else:
                offset_1 = 0
                offset_2 = 0
            if (int(lapses) != 0):
                offset_2 = 0
            # We assume that thinking times larger than 5 minutes are not
            # relevant (e.g. the phone rang and the user got distracted).
            thinking_time = float(thinking_time)
            if thinking_time > 5*60:
                thinking_time = 5*60
            # Add repetition.       
            sequence = offset_1 + int(acq_reps) + int(ret_reps)
            if result != None:
            self.database.execute(card_update, {
                "last_sequence"        : sequence,
                "last_repetition_time" : self.previous_stamp - first_rep_time,
                "key"                  : key,
            })	    
            data = {
                "card_id"            : id,
                "user_id"            : self.user_id,
                "time"               : self.previous_stamp - first_rep_time,
                "sequence"           : sequence,
                "grade"              : int(grade),
                "easiness"           : float(easiness),
                "acq_reps"           : int(acq_reps) + offset_1,
                "ret_reps"           : int(ret_reps),
                "lapses"             : int(lapses),
                "acq_since_lapse"    : int(acq_reps_since_lapse) + offset_2,
                "ret_since_lapse"    : int(ret_reps_since_lapse),
                "scheduled_interval" : int(scheduled_interval),
                "actual_interval"    : int(actual_interval),
                "new_interval"       : int(new_interval),
                "noise"              : int(noise),
                "thinking_time"      : thinking_time,
                "time_spent"         : self.stamp - self.previous_stamp,
                "actual_interval_s"  : actual_interval_s
            }
        self.database.execute(repetition_insert, data)
