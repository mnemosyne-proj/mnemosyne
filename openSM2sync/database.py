#
# database.py <Peter.Bienstman@gmail.com>
#

class Database(object):

    """Interface that needs to be implemented by the database object used in the
    Client and the Server.

    It is interesting checking out the implementation in libmnemosyne/databases,
    mainly SQLite_sync.py, as there are some interesting corner cases which
    need to be taken care off in the implementation, e.g. adding and
    immediately deleting an object between two syncs.

    We also provide here an example SQL schema for a minimal openSM2client, i.e.
    one that only supports cards, not facts. It is a stripped-down version of
    libmnemosyne's SQL schema.

    create table cards(
        _id integer primary key,
        id text,
        question text,
        answer text,
        grade integer,
        easiness real,
        acq_reps integer,
        ret_reps integer,
        lapses integer,
        acq_reps_since_lapse integer,
        ret_reps_since_lapse integer,
        last_rep integer,
        next_rep integer
    );
    create index i_cards on cards (id);

    create table tags(
        _id integer primary key,
        id text,
        name text,
    );
    create index i_tags on tags (id);

    create table tags_for_card(
        _card_id integer,
        _tag_id integer
    );
    create index i_tags_for_card on tags_for_card (_card_id);

    /* For object_id, we need to store the full ids as opposed to the _ids.
       When deleting an object, there is no longer a way to get the ids from
       the _ids, and for robustness and interoperability, we need to send the
       ids across when syncing.
    */

    create table log(
        _id integer primary key autoincrement, /* Should never be reused. */
        event_type integer,
        timestamp integer,
        object_id text,
        grade integer,
        easiness real,
        acq_reps integer,
        ret_reps integer,
        lapses integer,
        acq_reps_since_lapse integer,
        ret_reps_since_lapse integer,
        scheduled_interval integer,
        actual_interval integer,
        new_interval integer,
        thinking_time integer,
        last_rep integer,
        next_rep integer,
    );
    create index i_log_timestamp on log (timestamp);
    create index i_log_object_id on log (object_id);

    /* We track the last _id as opposed to the last timestamp, as importing
       another database could add log events with earlier dates, but which
       still need to be synced. Also avoids issues with clock drift. */

    create table partnerships(
        partner text,
        _last_log_id integer
    );

    create table media(
        filename text primary key,
        _hash text
    );

    This minimal client will not be sent any events sister to facts, so it
    does not need to implement them.

    """

    # General info.

    version = "Database version string"

    def path(self):

        """Returns full path of the database."""

        raise NotImplementedError


    def name(self):

        """Returns bare name of the database, without parent paths and
        suffixes.

        """

        raise NotImplementedError

    def media_dir(self):
        raise NotImplementedError

    def user_id(self):
        raise NotImplementedError

    def change_user_id(self, user_id):
        raise NotImplementedError

    # File operations.

    def new(self, path):
        raise NotImplementedError

    def save(self, path=None):
        raise NotImplementedError

    def backup(self):
        raise NotImplementedError

    def restore(self, path):
        raise NotImplementedError

    def load(self, path):
        raise NotImplementedError

    def abandon(self):
        raise NotImplementedError

    def is_empty(self):
        raise NotImplementedError

    # Partnerships.

    def set_sync_partner_info(self, info):
        raise NotImplementedError

    def partners(self):
        raise NotImplementedError

    def create_if_needed_partnership_with(self, partner):
        raise NotImplementedError

    def remove_partnership_with(self, partner):
        raise NotImplementedError

    def merge_partners(self, remote_partners):
        raise NotImplementedError

    def reset_partnerships(self):
        raise NotImplementedError

    def is_sync_reset_needed(self, partner):
        raise NotImplementedError

    def append_to_sync_partner_info(self, partner_info):
        return partner_info

    # Syncing process.

    def update_last_log_index_synced_for(self, partner):
        raise NotImplementedError

    def number_of_log_entries_to_sync_for(self, partner,
            interested_in_old_reps=True):
        raise NotImplementedError

    def number_of_log_entries(self, interested_in_old_reps=True):
        raise NotImplementedError

    def log_entries_to_sync_for(self, partner, interested_in_old_reps=True):
        raise NotImplementedError

    def all_log_entries(self, interested_in_old_reps=True):
        raise NotImplementedError

    def check_for_edited_media_files(self):
        raise NotImplementedError

    def media_filenames_to_sync_for(self, partner):
        raise NotImplementedError

    def all_media_filenames(self):
        raise NotImplementedError

    def apply_log_entry(self, log_entry):
        raise NotImplementedError

    def generate_log_entries_for_settings(self):

        """Needed after binary initial upload/download of the database, to
        ensure that the side effects to config get applied.

        """

        raise NotImplementedError

    # Science log. Only relevant if the client decides to deal with this.
    # Can be left to a libmnemosyne-based server.

    def dump_to_science_log(self):
        pass

    def skip_science_log(self):
        pass
