#
# log_entry.py <Peter.Bienstman@UGent.be>
#

class EventTypes(object):

    """Codes to identify event types."""

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
    DELETED_MEDIA = 20


class LogEntry(dict):

    """A dictionary consisting of (key, value) pairs to sync.

    type (int): event type from list above
    time (int): timestamp for log entry
    o_id (string): id of object involved in log entry (e.g. tag id for
        ADDED_TAG, string with name and version for STARTED_PROGRAM,
        STARTED_SCHEDULER, ...

    sch, n_mem, act (int): optional, but suggested for compatibility with
        Mnemosyne. The number of scheduled, non memorised and active cards in
        the database in a LOADED_DATABASE and SAVED_DATABASE event.

    name (unicode): tag name


    extra (unicode): extra data for objects. Optional.

    Note the difference between a string and a unicode type is that a string
    should be useable directly as an attribute or tag name in XML. A unicode
    object can be arbitrary and will be encoded/escaped as appropriate.

    """
    
    pass

