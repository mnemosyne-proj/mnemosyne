#
# log_entry.py <Peter.Bienstman@gmail.com>
#

class EventTypes(object):

    """Codes to identify event types."""

    # Relevant for all clients.

    STARTED_PROGRAM = 1
    STOPPED_PROGRAM = 2
    STARTED_SCHEDULER = 3
    LOADED_DATABASE = 4
    SAVED_DATABASE = 5

    ADDED_CARD = 6
    EDITED_CARD = 7
    DELETED_CARD = 8
    REPETITION = 9

    ADDED_TAG = 10
    EDITED_TAG = 11
    DELETED_TAG = 12

    ADDED_MEDIA_FILE = 13
    EDITED_MEDIA_FILE = 14
    DELETED_MEDIA_FILE = 15

    # Only relevant for fact-based clients.

    ADDED_FACT = 16
    EDITED_FACT = 17
    DELETED_FACT = 18

    ADDED_FACT_VIEW = 19
    EDITED_FACT_VIEW = 20
    DELETED_FACT_VIEW = 21

    ADDED_CARD_TYPE = 22
    EDITED_CARD_TYPE = 23
    DELETED_CARD_TYPE = 24

    ADDED_CRITERION = 25
    EDITED_CRITERION = 26
    DELETED_CRITERION = 27

    # Optional.

    EDITED_SETTING = 28
    WARNED_TOO_MANY_CARDS = 29

class LogEntry(dict):

    """A dictionary consisting of (key, value) pairs to sync.

    General keys:
        type (int): event type from list above.
        time (int): Unix timestamp for log entry.
        o_id (nice_string): id of object involved in log entry (e.g. tag id for
            ADDED_TAG, string with name and version for STARTED_PROGRAM,
            STARTED_SCHEDULER, ... .
            Object ids should not contain commas.
        extra (string): extra data for tags, cards and card_types, typically
            the representation of a Python dictionary. Optional.

    Keys specific to LOADED_DATABASE and SAVED_DATABASE:
        sch, n_mem, act (int): optional, but suggested for compatibility with
            Mnemosyne. The number of scheduled, non memorised and active cards
            in the database.

    Keys specific to ADDED_CARD, EDITED_CARD:
        c_time, m_time (int): creation time, modification time, Unix timestamp
        card_t (nice_string): card type id, if partner supports facts
        fact (nice_string), fact_v (nice_string): fact id and fact view id
        q, a (string): question and answer, if partner does not support facts.
        tags (nice_string): comma separated list of tag ids
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
        sch_i (int): scheduled previous interval in seconds
        act_i (int): actual previous interval in seconds
        th_t (int): thinking time in seconds
        n_rp (int): next repetition, Unix timestamp
          (note: last rep is the same as the entry's timestamp')

        Optional, but suggested for compatibility with Mnemosyne:

        ac_rp (int): number of acquisition repetitions (gr < 2)
        rt_rp (int): number of retention repetitions (gr >= 2)
        lps (int): number of lapses (new grade < 2 if old grade >= 2)
        ac_rp_l, rt_rp_l (int): number of ac_rp, rt_rp since last lapse
        sch_data (int): extra scheduler data

        Note that a repetition entry serves two purposes: on one hand it
        contains the info needed to create the anonymous logs to send to the
        science server and to have some data available locally for statistics
        plugins to work with. On the other hand, it contains all the info
        needed to update the corresponding card in the database.

    Keys specific to ADDED_TAG, EDITED_TAG:
        name (string): tag name

    Keys specific to ADDED_MEDIA_FILE, EDITED_MEDIA_FILE, DELETED_MEDIA_FILE:
        fname (string): filename

    Keys specific to ADDED_FACT, EDITED_FACT:
        <fact_key> (string): any different key name than the general keys
            above will be treated as belonging to the fact's data
            dictionary.

    The following events are entirely optional, certainly for card-based
    clients. Consult libmnemosyne's code for more details.

    Keys specific to ADDED_FACT_VIEW, EDITED_FACT_VIEW, DELETED_FACT_VIEW:
        name (string)
        q_fact_keys (string)
        a_fact_keys (string)
        q_fact_key_decorators (string)
        a_fact_key_decorators (string)
        a_on_top_of_q (bool)
        type_answer (bool)
        extra (string)

    Keys specific to ADDED_CARD_TYPE, EDITED_CARD_TYPE, DELETED_CARD_TYPE:
        name (string)
        fact_keys_and_names (string)
        fact_views (string)
        unique_fact_keys (string)
        required_fact_keys (string)
        keyboard_shortcuts (string)
        extra (string)

    Keys specific to ADDED_CRITERION, EDITED_CRITERION, DELETED_CRITERION:
        name (string)
        criterion_type (string)
        data (string)

    Keys specific to EDITED_SETTING:
        value (string)

    Any other keys in LogEntry that don't appear in the list above will be
    synced as string.

    Events like DELETED_TAG, DELETED_FACT, etc only pass on the object id as
    data.

    The difference between nice_string and string is that nice_string can be
    used directly as an attribute or tag name in XML, i.e. it should not
    contain <, >, &, ... . A normal string can be arbitrary and will be
    encoded/escaped as appropriate.

    """

    pass
