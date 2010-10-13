//
// main_wdgt.h <Peter.Bienstman@UGent.be>
//

void main_wdgt_set_window_title(char* text);

void main_wdgt_show_information(char* text);

int main_wdgt_show_question(char* text, char* option_0, char* option_1,
                           char* option_2);

void main_wdgt_show_error(char* text);

void main_wdgt_get_filename_to_open(char* path, char* filter, char *caption,
                                    char* filename, int str_size);

void main_wdgt_get_filename_to_save(char* path, char* filter, char *caption,
                                    char* filename, int str_size);
// Should warn about overwriting existing file.


void main_wdgt_set_status_bar_message(char* text);


void main_wdgt_set_progress_text(char* text);


void main_wdgt_set_progress_range(int min, int max);


void main_wdgt_set_progress_update_interval(int interval);


void main_wdgt_set_progress_value(int value);


void main_wdgt_close_progress();


void main_wdgt_enable_edit_current_card(int is_enabled);


void main_wdgt_enable_delete_current_card(int is_enabled);


void main_wdgt_enable_browse_cards(int is_enabled);

