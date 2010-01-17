#
# log_entry.py <Peter.Bienstman@UGent.be>
#

class EventTypes(object):

    """Codes to identify event types.

    Note that a REPETITION event needs to be accompanied by a corresponding
    UPDATED_CARD event, as the main purpose of the REPETITION event is to be
    able to do quick statistics on your learning history without needing to
    know the contents of the card.
    
    """

    STARTED_PROGRAM = 1
    STOPPED_PROGRAM = 2
    STARTED_SCHEDULER = 3
    LOADED_DATABASE = 4
    SAVED_DATABASE = 5
    ADDED_TAG = 6
    UPDATED_TAG = 7
    DELETED_TAG = 8
    ADDED_FACT = 9
    UPDATED_FACT = 10
    DELETED_FACT = 11
    ADDED_CARD = 12
    UPDATED_CARD = 13
    DELETED_CARD = 14
    ADDED_CARD_TYPE = 15
    UPDATED_CARD_TYPE = 16
    DELETED_CARD_TYPE = 17
    REPETITION = 18
    ADDED_MEDIA = 19
    UPDATED_MEDIA = 20
    DELETED_MEDIA = 21


class LogEntry(dict):

    """A dictionary consisting of (key, value) pairs to sync.

    General keys:
        type (int): event type from list above.
        time (int): Unix timestamp for log entry.
        o_id (string): id of object involved in log entry (e.g. tag id for
            ADDED_TAG, string with name and version for STARTED_PROGRAM,
            STARTED_SCHEDULER, filename for MEDIA events, ... .
            Object ids should not contain commas.
        extra (unicode): extra data for tags, cards and card_types, typically
            the representation of a Python dictionary. Optional.
        
    Keys specific to LOADED_DATABASE and SAVED_DATABASE:
        sch, n_mem, act (int): optional, but suggested for compatibility with
            Mnemosyne. The number of scheduled, non memorised and active cards
            in the database.
        
    Keys specific to ADDED_TAG, UPDATED_TAG:
        name (unicode): tag name

    Keys specific to ADDED_FACT, UPDATED_FACT:
        card_t (string), c_time (int), m_time (int): card type id,
            creation time, modification time (Unix timestamp).

        <fact_key> (unicode): any different key name than the ones above will
            be treated as belonging to the fact's data dictionary.
            
    Keys specific to ADDED_CARD, UPDATED_CARD:
        fact (string), fact_v (string): fact id and fact view id
        tags (string): comma separated list of tag ids
        act (int): card active?
        gr (int): grade (-1 through 5, -1 meaning unseen)
        e (float): easiness
        l_rp (int): last repetiton, Unix timestamp
        n_rp (int): next repetition, Unix timestamp

        Optional, but suggested for compatibility with Mnemosyne:
        
        ac_rp (int): number of acquisition repetitions (gr < 2)
        rt_rp (int): number of retention repetitions (gr >= 2)
        lps (int): number of lapses (new grade < 2 if old grade >= 2)
        ac_rp_l, rt_rp_l (int): number of ac_rp, rt_rp since last lapse
        sch_data (int): extra scheduler data

    Keys specific to REPETITION:
        gr (int): grade (-1 through 5, -1 meaning unseen)
        e (float): easiness
        sch_i (int): scheduled interval in seconds
        act_i (int): actual interval in seconds
        new_i (int): new interval in seconds
        th_t (int): thinking time in seconds
        
        Optional, but suggested for compatibility with Mnemosyne:
        
        ac_rp (int): number of acquisition repetitions (gr < 2)
        rt_rp (int): number of retention repetitions (gr >= 2)
        lps (int): number of lapses (new grade < 2 if old grade >= 2)
        ac_rp_l, rt_rp_l (int): number of ac_rp, rt_rp since last lapse

    Keys specific to ADDED_MEDIA, UPDATED_MEDIA, DELETED_MEDIA:
        o_id (unicode): filename
        fact (string): id of fact where filename is used 
    
    Any other keys in LogEntry that don't appear in the list above will be
    synced as unicode.

    Events like DELETED_TAG, DELETED_FACT, etc only pass on the object id as
    data.

    Note the difference between a string and a unicode type is that a string
    should be useable directly as an attribute or tag name in XML. A unicode
    object can be arbitrary and will be encoded/escaped as appropriate.

    """
    
    pass

