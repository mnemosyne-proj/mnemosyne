
//
// main_widget.h <Peter.Bienstman@UGent.be>
//

void main_widget_set_window_title(char* title);

void main_widget_show_information(char* message);

int main_widget_show_question(char* question, char* option_0, char* option_1,
                              char* option_2);

void main_widget_show_error(char* message);

void main_widget_get_filename_to_open(char* path, char* filter, char *caption,
                                      char* filename, int str_size);

// The following function should warn about overwritin existing file.
void main_widget_get_filename_to_save(char* path, char* filter, char *caption,
                                      char* filename, int str_size);


void main_widget_set_status_bar_message(char* message);


void main_widget_set_progress_text(char* text);


void main_widget_set_progress_range(int min, int max);


void main_widget_set_progress_update_interval(int interval);


void main_widget_set_progress_value(int value);


void main_widget_close_progress();


void main_widget_enable_edit_current_card(int enable);


void main_widget_enable_delete_current_card(int enable);


void main_widget_enable_browse_cards(int enable);

